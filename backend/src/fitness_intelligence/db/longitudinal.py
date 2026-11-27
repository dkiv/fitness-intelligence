"""Latest-state longitudinal reads for an owner resolved by a trusted caller."""

import re
from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime
from decimal import localcontext
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Engine, select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from fitness_intelligence.adapters.hevy.analytics import HevyHistoryProfile, read_hevy_facts
from fitness_intelligence.analytics.exposure import (
    RECOVERY_CATEGORIES,
    ActivityDay,
    EnduranceExposure,
    RecoveryExposure,
    StrengthExposure,
)
from fitness_intelligence.analytics.longitudinal import (
    Coverage,
    DailyExpenditure,
    DailyIntake,
    DailyWeight,
    IntakeObservation,
    Issue,
    LongitudinalReport,
    Metric,
    ObservationId,
    OpenIssue,
    ReportDay,
    WeighIn,
    WeightExclusion,
    daily_median,
)
from fitness_intelligence.analytics.strength import DAY, Period
from fitness_intelligence.analytics.weight import partition_weigh_ins
from fitness_intelligence.db.endurance_models import DailyRecoveryObservation
from fitness_intelligence.db.exposure import read_outings, recovery_day, recovery_fact
from fitness_intelligence.db.history_models import GarminCoverage, GarminIssue
from fitness_intelligence.db.models import SourceAccount
from fitness_intelligence.db.nutrition_models import BodyWeightObservation, DailyIntakeObservation
from fitness_intelligence.domain.endurance import DailyMetric, Source
from fitness_intelligence.nutrition.intake import IntakeSelection, select_daily_intake
from fitness_intelligence.nutrition.weight import WeightDay, select_weight_day

# Reviewed producer contracts. Unknown mapping versions need a new provenance review.
GARMIN_NUTRITION_V1 = "garmin-personal-b3.2-v1"
FOOD_FIELD = "DailyNutritionSummaryDTO.dailyNutritionContent.calories"
type DayKey = tuple[UUID, str, date]


def _empty_scan_start(row: GarminCoverage | None) -> datetime | None:
    if row is None or row.status != "empty":
        return None
    receipt = row.receipts.get("empty_activity_scan")
    stamp = receipt.get("started_at") if isinstance(receipt, dict) else None
    if not isinstance(stamp, str):
        return None
    try:
        start = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    return start if start.tzinfo is not None else None


def _coverage(
    source: Source,
    account_status: str,
    category: str,
    day: date,
    row: GarminCoverage | None,
    issues: tuple[Issue, ...],
    retained: int,
) -> Coverage:
    receipts = row.receipts if row else {}
    return Coverage(
        source=source,
        account_status=account_status,
        category=category,
        provider_date=day,
        status=row.status if row else "never_queried",
        attempted_at=row.attempted_at if row else None,
        last_success=row.last_success if row else None,
        last_success_count=row.eligible_count if row else None,
        policy=row.policy if row else None,
        pass_key=row.pass_key if row else None,
        source_receipts=tuple(sorted(receipts.get("sources", {}).items())),
        acquisition_gap=receipts.get("unavailable", {}).get("reason"),
        issues=issues,
        retained_count=retained,
    )


def _intake_fact(
    row: DailyIntakeObservation, source: Source, status: str, aligned: bool
) -> IntakeObservation:
    exclusion = None
    if status == "legacy_unresolved":
        exclusion = "unresolved_binding"
    elif row.reported_kcal == 0:
        # The recognized food mapper only persists zero after a positive logged-food event.
        food_event = (
            source.provider == "garmin"
            and row.source_field == FOOD_FIELD
            and row.mapping_version == GARMIN_NUTRITION_V1
            and row.source_data_present is not False
        )
        if row.source_data_present is not True and not food_event:
            exclusion = "unsupported_zero"
    return IntakeObservation(
        identity=ObservationId(source, "daily_intake", row.id),
        provider_date=row.local_date,
        report_date=row.local_date if aligned else None,
        occurred_at=None,
        recorded_at=None,
        retrieved_at=row.retrieved_at,
        value=row.reported_kcal,
        method="reported",
        unit="kcal",
        source_field=row.source_field,
        mapping_version=row.mapping_version,
        upstream_writer=row.upstream_writer,
        source_data_present=row.source_data_present,
        logging_completeness=row.completeness,
        exclusion_reason=exclusion,
    )


def _intake_day(
    day: date,
    selection: IntakeSelection,
    facts: tuple[IntakeObservation, ...],
    coverage: tuple[Coverage, ...],
    zones: Mapping[UUID, ZoneInfo],
) -> DailyIntake:
    eligible = tuple(f for f in facts if f.exclusion_reason is None)
    accounts = {f.identity.source.source_account_id for f in facts}
    calendars = {zones[account].key if account in zones else None for account in accounts}
    reasons = {issue.reason for c in coverage for issue in c.issues}
    if selection.status == "conflict":
        reasons.add("source_disagreement")
    if not facts:
        reasons.add("no_intake_observation")
        reasons.update(c.status for c in coverage)
    if len(accounts) > 1 and (None in calendars or len(calendars) != 1):
        reasons.add("incompatible_or_unknown_provider_days")
    if any(f.exclusion_reason == "unresolved_binding" for f in facts):
        reasons.add("unresolved_binding")
    if facts and not eligible:
        reasons.update(f.exclusion_reason for f in facts if f.exclusion_reason)
    status = selection.status
    if reasons and status not in ("conflict", "missing"):
        status = "withheld"
    metric = Metric(
        scope="owner_day",
        status=status,
        value=None if reasons else selection.reported_kcal,
        unit="kcal",
        report_date=day if facts and all(f.report_date == day for f in facts) else None,
        supporting=() if reasons else tuple(f.identity for f in eligible),
        retained_count=len(selection.observation_ids),
        reasons=tuple(sorted(reasons)),
    )
    return DailyIntake(metric, selection.completeness, facts, coverage)


def _verification_basis(
    row: BodyWeightObservation, coverage: Coverage
) -> Literal["historical_segment", "bounded_operator_verified"] | None:
    if (
        row.mapping_version != GARMIN_NUTRITION_V1
        or row.source_field != "DateWeightDTO.weight"
        or row.documented_source_unit != "kg"
        or row.source_unit not in ("kg", "g")
        or row.measured_at is None
        or row.time_resolution_us != 1000
        or row.upstream_id is not None
    ):
        return None
    with localcontext() as ctx:
        ctx.prec = 38
        expected = row.source_value / 1000 if row.source_unit == "g" else row.source_value
    if row.mass_kg != expected:
        return None
    if row.verification_scope is not None:
        if row.source_unit == "g" and re.fullmatch("[0-9a-f]{64}", row.verification_scope):
            return "historical_segment"
        return None
    # Both writers share a mapper. Positive historical acquisition without the row's
    # segment receipt is ambiguous. A never-queried day or a failed first refresh is
    # compatible with an older operator-verified bounded write.
    if coverage.status == "never_queried" or (
        coverage.status == "failed"
        and coverage.last_success is None
        and coverage.attempted_at is not None
        and row.retrieved_at < coverage.attempted_at
    ):
        return "bounded_operator_verified"
    return None


def _weight_day(
    selection: WeightDay,
    records: Mapping[UUID, BodyWeightObservation],
    coverage: Coverage,
    period: Period,
    day_aligned: bool,
) -> DailyWeight:
    eligible: list[WeighIn] = []
    excluded: list[WeightExclusion] = []
    # The selector withholds measurements as a unit. Hydrate only the values it releases.
    selected = (
        dict(zip(selection.retained_ids, selection.measurements, strict=True))
        if selection.measurements
        else {}
    )
    for ident in selection.retained_ids:
        row = records[ident]
        identity = ObservationId(coverage.source, "body_weight", ident)
        if ident not in selected:
            excluded.append(WeightExclusion(identity, selection.reasons or ("withheld",)))
            continue
        basis = _verification_basis(row, coverage)
        if basis is None:
            excluded.append(WeightExclusion(identity, ("unverified_weight_unit",)))
            continue
        instant, kg = selected[ident]
        assert instant is not None and row.time_resolution_us is not None
        eligible.append(
            WeighIn(
                identity=identity,
                provider_date=row.local_date,
                report_date=instant.astimezone(period.zone).date(),
                occurred_at=instant,
                retrieved_at=row.retrieved_at,
                recorded_at=None,
                value=kg,
                unit="kg",
                method="reported_weigh_in",
                source_field=row.source_field,
                mapping_version=row.mapping_version,
                upstream_writer=row.upstream_writer,
                source_value=row.source_value,
                interpreted_unit=row.source_unit,
                documented_unit=row.documented_source_unit,
                time_resolution_us=row.time_resolution_us,
                verification_basis=basis,
                verification_scope=row.verification_scope,
            )
        )
    reasons = set(selection.reasons)
    if not selection.retained_ids:
        reasons.update(("no_weight_observation", coverage.status))
    reasons.update(reason for item in excluded for reason in item.reasons)
    groups = partition_weigh_ins(eligible)
    median = None
    if len(groups) == 1:
        median = daily_median(tuple(w.value for w in eligible))
        status = "observed"
    elif groups:
        known_writers = {key.writer for key in groups if key.writer is not None}
        reasons.add(
            "incompatible_weight_regimes"
            if len(known_writers) > 1
            else "weight_comparability_unverified"
        )
        status = "withheld"
    else:
        status = "withheld" if excluded or selection.reasons else "missing"
    aligned = day_aligned and all(w.report_date == coverage.provider_date for w in eligible)
    return DailyWeight(
        Metric(
            scope="account_day",
            status=status,
            value=median,
            unit="kg",
            report_date=coverage.provider_date if aligned else None,
            supporting=tuple(w.identity for w in eligible),
            retained_count=len(selection.retained_ids),
            reasons=tuple(sorted(reasons)),
        ),
        tuple(eligible),
        tuple(excluded),
        coverage,
    )


ENERGY = (DailyMetric.TOTAL_ENERGY, DailyMetric.ACTIVE_ENERGY, DailyMetric.BASAL_ENERGY)


def _expenditure_day(
    rows: Mapping[str, DailyRecoveryObservation], coverage: Coverage, aligned: bool
) -> DailyExpenditure:
    day = coverage.provider_date
    report_date = day if aligned else None
    facts = []
    metrics = []
    for component in ENERGY:
        row = rows.get(component)
        # Known component subjects qualify only that field. Unknown scopes hold the category.
        reasons = {
            issue.reason
            for issue in coverage.issues
            if issue.subject == component or issue.subject not in ENERGY
        }
        supporting = ()
        if row is None:
            reasons.update(("no_component_observation", coverage.status))
            status = "missing"
        else:
            fact = recovery_fact(row, coverage.source, aligned)
            facts.append(fact)
            if (row.method, row.unit) != ("wearable_estimate", "kcal"):
                reasons.add("ineligible_method_or_unit")
            status = "withheld" if reasons else "observed"
            if not reasons:
                supporting = (fact.identity,)
        metrics.append(
            Metric(
                "account_day",
                status,
                row.value if supporting else None,
                "kcal",
                report_date,
                supporting,
                int(row is not None),
                tuple(sorted(reasons)),
            )
        )
    total, active, basal = metrics
    return DailyExpenditure(total, active, basal, tuple(facts), coverage)


@dataclass(frozen=True)
class TrainingDay:
    day: date
    strength: StrengthExposure | None
    endurance: EnduranceExposure | None
    recovery: RecoveryExposure | None
    open_issues: tuple[OpenIssue, ...]


def training_ledger_scope(
    model: type[GarminCoverage | GarminIssue],
    owner: UUID,
    start: date,
    stop: date,
    endurance_account: UUID | None,
    recovery_account: UUID | None,
) -> tuple[ColumnElement[bool], ...]:
    selected = (
        (model.source_account_id == endurance_account)
        & model.category.in_(("activities", "running_steps"))
    ) | (
        (model.source_account_id == recovery_account)
        & model.category.in_(set(RECOVERY_CATEGORIES.values()))
    )
    return (
        model.user_id == owner,
        model.local_date >= start,
        model.local_date < stop,
        selected,
    )


def read_training_days(
    db: Session,
    owner: UUID,
    period: Period,
    zones: Mapping[UUID, ZoneInfo],
    hevy_profile: HevyHistoryProfile | None,
    endurance: Source | None,
    recovery_source: Source | None,
    statuses: Mapping[UUID, str],
) -> tuple[TrainingDay, ...]:
    """The same daily D1D training views, within the calling reader's transaction."""
    sources = {s.source_account_id: s for s in (endurance, recovery_source) if s}
    if any(s.owner_id != owner or s.provider != "garmin" for s in sources.values()):
        raise ValueError("invalid training source")
    if not sources and hevy_profile is None:
        return tuple(
            TrainingDay(period.start + n * DAY, None, None, None, ())
            for n in range((period.stop - period.start).days)
        )
    if hevy_profile:
        i = hevy_profile.source_account_id
        sources[i] = Source(owner, "hevy", i)
    endurance_account = endurance.source_account_id if endurance else None
    recovery_account = recovery_source.source_account_id if recovery_source else None

    selection = owner, period.start, period.stop, endurance_account, recovery_account
    ledger = {
        (r.source_account_id, r.category, r.local_date): r
        for r in db.scalars(
            select(GarminCoverage).where(*training_ledger_scope(GarminCoverage, *selection))
        )
    }
    issues: dict[DayKey, list[Issue]] = defaultdict(list)
    open_issues: dict[date, list[OpenIssue]] = defaultdict(list)
    for r in db.scalars(
        select(GarminIssue)
        .where(*training_ledger_scope(GarminIssue, *selection), GarminIssue.resolved_at.is_(None))
        .order_by(
            GarminIssue.source_account_id,
            GarminIssue.category,
            GarminIssue.subject,
            GarminIssue.reason,
        )
    ):
        issue = Issue(r.subject, r.reason)
        issues[r.source_account_id, r.category, r.local_date].append(issue)
        open_issues[r.local_date].append(
            OpenIssue(
                sources[r.source_account_id],
                r.category,
                r.local_date,
                issue,
                r.evidence_digest,
                r.first_seen,
                r.last_seen,
            )
        )

    def coverage(i: UUID, category: str, day: date, retained: int) -> Coverage:
        key = i, category, day
        return _coverage(
            sources[i], statuses[i], category, day, ledger.get(key), tuple(issues[key]), retained
        )

    recovery: dict[date, dict[str, DailyRecoveryObservation]] = defaultdict(dict)
    if recovery_source:
        for r in db.scalars(
            select(DailyRecoveryObservation).where(
                DailyRecoveryObservation.user_id == owner,
                DailyRecoveryObservation.provider == "garmin",
                DailyRecoveryObservation.source_account_id == recovery_account,
                DailyRecoveryObservation.local_date >= period.start,
                DailyRecoveryObservation.local_date < period.stop,
                DailyRecoveryObservation.metric.in_(tuple(RECOVERY_CATEGORIES)),
            )
        ):
            recovery[r.local_date][r.metric] = r
    hevy_days = defaultdict(list)
    if hevy_profile is not None:
        for fact in read_hevy_facts(db, owner_id=owner, period=period, profile=hevy_profile):
            hevy_days[fact.report_date].append(fact)
    outings = (
        read_outings(db, sources[endurance_account], period, issues)
        if endurance_account is not None
        else {}
    )

    def aligned(i: UUID) -> bool:
        return i in zones and zones[i].key == period.zone.key

    days = []
    for offset in range((period.stop - period.start).days):
        day = period.start + DAY * offset
        strength_view = None
        if hevy_profile is not None:
            i = hevy_profile.source_account_id
            strength_view = StrengthExposure(sources[i], statuses[i], (day,), tuple(hevy_days[day]))
        endurance_view = None
        if endurance_account is not None:
            activities = tuple(outings.get(day, ()))
            native = ActivityDay(
                coverage(endurance_account, "activities", day, len(activities)),
                coverage(
                    endurance_account,
                    "running_steps",
                    day,
                    sum(f.instruction_rows or 0 for f in activities if f.sport == "running"),
                ),
                activities,
                aligned(endurance_account) and all(f.report_date == day for f in activities),
                provider_zone=zones.get(endurance_account),
                scan_started_at=_empty_scan_start(
                    ledger.get((endurance_account, "activities", day))
                ),
            )
            endurance_view = EnduranceExposure((native,))
        recovery_view = None
        if recovery_account is not None:
            recovery_counts = Counter(RECOVERY_CATEGORIES[m] for m in recovery[day])
            recovery_view = recovery_day(
                recovery[day],
                {
                    c: coverage(recovery_account, c, day, recovery_counts[c])
                    for c in sorted(set(RECOVERY_CATEGORIES.values()))
                },
                aligned(recovery_account),
            )
        days.append(
            TrainingDay(day, strength_view, endurance_view, recovery_view, tuple(open_issues[day]))
        )
    return tuple(days)


def _read(
    db: Session,
    owner: UUID,
    period: Period,
    account: UUID,
    zones: Mapping[UUID, ZoneInfo],
    expenditure_account: UUID | None,
    hevy_profile: HevyHistoryProfile | None,
    endurance_account: UUID | None,
    recovery_account: UUID | None,
) -> LongitudinalReport:
    accounts = {
        a.id: a
        for a in db.execute(
            select(SourceAccount.id, SourceAccount.provider, SourceAccount.status)
            .where(SourceAccount.user_id == owner)
            .order_by(SourceAccount.id)
        )
    }
    requested = [
        (i, "garmin")
        for i in (account, expenditure_account, endurance_account, recovery_account)
        if i is not None
    ]
    if hevy_profile is not None:
        requested.append((hevy_profile.source_account_id, "hevy"))
    if zones.keys() - accounts.keys() or any(
        i not in accounts
        or accounts[i].provider != provider
        or accounts[i].status == "legacy_unresolved"
        for i, provider in requested
    ):
        raise ValueError("invalid source account for report")
    sources = {i: Source(owner, a.provider, i) for i, a in accounts.items()}

    def in_range(
        model: type[
            DailyIntakeObservation
            | BodyWeightObservation
            | DailyRecoveryObservation
            | GarminCoverage
            | GarminIssue
        ],
    ) -> tuple[ColumnElement[bool], ...]:
        return (
            model.user_id == owner,
            model.local_date >= period.start,
            model.local_date < period.stop,
        )

    intake: dict[date, list[IntakeObservation]] = defaultdict(list)
    intake_accounts = {i for i, a in accounts.items() if a.provider == "garmin"}
    for row in db.scalars(
        select(DailyIntakeObservation)
        .where(*in_range(DailyIntakeObservation))
        .order_by(DailyIntakeObservation.id)
    ):
        i = row.source_account_id
        intake_accounts.add(i)
        intake[row.local_date].append(
            _intake_fact(
                row, sources[i], accounts[i].status, i in zones and zones[i].key == period.zone.key
            )
        )

    weights = {
        row.id: row
        for row in db.scalars(
            select(BodyWeightObservation).where(
                *in_range(BodyWeightObservation),
                BodyWeightObservation.source_account_id == account,
                BodyWeightObservation.provider == "garmin",
            )
        )
    }

    def recovery_rows(
        i: UUID | None, metrics: tuple[DailyMetric, ...]
    ) -> dict[date, dict[str, DailyRecoveryObservation]]:
        rows: dict[date, dict[str, DailyRecoveryObservation]] = defaultdict(dict)
        if i is not None:
            for row in db.scalars(
                select(DailyRecoveryObservation).where(
                    *in_range(DailyRecoveryObservation),
                    DailyRecoveryObservation.provider == "garmin",
                    DailyRecoveryObservation.source_account_id == i,
                    DailyRecoveryObservation.metric.in_(metrics),
                )
            ):
                rows[row.local_date][row.metric] = row
        return rows

    energy = recovery_rows(expenditure_account, ENERGY)

    def categories(model: type[GarminCoverage | GarminIssue]) -> ColumnElement[bool]:
        selected_categories = (model.category == "intake") | (
            (model.category == "weight") & (model.source_account_id == account)
        )

        if expenditure_account is not None:
            selected_categories |= (model.category == "expenditure") & (
                model.source_account_id == expenditure_account
            )
        return selected_categories

    ledger = {
        (c.source_account_id, c.category, c.local_date): c
        for c in db.scalars(
            select(GarminCoverage).where(*in_range(GarminCoverage), categories(GarminCoverage))
        )
    }
    issues: dict[DayKey, list[Issue]] = defaultdict(list)
    for issue in db.scalars(
        select(GarminIssue)
        .where(*in_range(GarminIssue), categories(GarminIssue), GarminIssue.resolved_at.is_(None))
        .order_by(GarminIssue.subject, GarminIssue.reason)
    ):
        issues[issue.source_account_id, issue.category, issue.local_date].append(
            Issue(issue.subject, issue.reason)
        )

    def coverage(i: UUID, category: str, day: date, retained: int) -> Coverage:
        key = (i, category, day)
        return _coverage(
            sources[i],
            accounts[i].status,
            category,
            day,
            ledger.get(key),
            tuple(issues[key]),
            retained,
        )

    training = read_training_days(
        db,
        owner,
        period,
        zones,
        hevy_profile,
        sources.get(endurance_account),
        sources.get(recovery_account),
        {i: a.status for i, a in accounts.items()},
    )

    def aligned(i: UUID) -> bool:
        return i in zones and zones[i].key == period.zone.key

    days = []
    for offset in range((period.stop - period.start).days):
        day = period.start + DAY * offset
        facts = tuple(intake[day])
        counts = Counter(f.identity.source.source_account_id for f in facts)
        intake_coverage = tuple(
            coverage(i, "intake", day, counts[i]) for i in sorted(intake_accounts)
        )
        selected = select_daily_intake(db, owner, day)
        weight = select_weight_day(db, sources[account], day)
        days.append(
            ReportDay(
                day,
                _intake_day(day, selected, facts, intake_coverage, zones),
                _weight_day(
                    weight,
                    weights,
                    coverage(account, "weight", day, len(weight.retained_ids)),
                    period,
                    account in zones and zones[account].key == period.zone.key,
                ),
                _expenditure_day(
                    energy[day],
                    coverage(expenditure_account, "expenditure", day, len(energy[day])),
                    expenditure_account in zones
                    and zones[expenditure_account].key == period.zone.key,
                )
                if expenditure_account is not None
                else None,
                strength=training[offset].strength,
                endurance=training[offset].endurance,
                recovery=training[offset].recovery,
            )
        )
    return LongitudinalReport(
        owner,
        sources[account],
        period,
        tuple(sorted((i, z.key) for i, z in zones.items())),
        tuple(days),
        hevy_profile=hevy_profile,
        endurance_source=sources.get(endurance_account),
        recovery_source=sources.get(recovery_account),
        expenditure_source=sources[expenditure_account]
        if expenditure_account is not None
        else None,
    )


@contextmanager
def read_snapshot(engine: Engine) -> Iterator[Session]:
    """One PostgreSQL read-only, repeatable-read transaction for all evidence families."""
    if not isinstance(engine, Engine) or engine.dialect.name != "postgresql":
        raise ValueError("a PostgreSQL Engine is required for a fresh report transaction")
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        with conn.begin():
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
            conn.exec_driver_sql("SET LOCAL TIME ZONE 'UTC'")
            settings = conn.execute(
                text(
                    "SELECT current_setting('transaction_isolation'), "
                    "current_setting('transaction_read_only')"
                )
            ).one()
            if tuple(settings) != ("repeatable read", "on"):
                raise ValueError("unsuitable report transaction")
            with Session(conn, autoflush=False) as db:
                yield db


def query_longitudinal(
    engine: Engine,
    *,
    owner_id: UUID,
    period: Period,
    weight_account_id: UUID,
    source_zones: Mapping[UUID, ZoneInfo] | None = None,
    expenditure_account_id: UUID | None = None,
    hevy_profile: HevyHistoryProfile | None = None,
    endurance_account_id: UUID | None = None,
    recovery_account_id: UUID | None = None,
) -> LongitudinalReport:
    """Own a fresh read-only snapshot. Source zones describe verified calendars for this period."""
    if not isinstance(engine, Engine) or engine.dialect.name != "postgresql":
        raise ValueError("a PostgreSQL Engine is required for a fresh report transaction")
    zones = dict(source_zones or {})
    if not isinstance(period.zone, ZoneInfo) or any(
        not isinstance(z, ZoneInfo) for z in zones.values()
    ):
        raise ValueError("report and source calendars require IANA zones")
    with read_snapshot(engine) as db:
        return _read(
            db,
            owner_id,
            period,
            weight_account_id,
            zones,
            expenditure_account_id,
            hevy_profile,
            endurance_account_id,
            recovery_account_id,
        )

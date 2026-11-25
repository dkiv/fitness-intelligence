"""Latest-state longitudinal reads for an owner resolved by a trusted caller."""

import re
from collections import Counter, defaultdict
from collections.abc import Mapping
from datetime import date
from decimal import localcontext
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Engine, select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from fitness_intelligence.analytics.longitudinal import (
    Coverage,
    DailyIntake,
    DailyWeight,
    IntakeObservation,
    Issue,
    LongitudinalReport,
    Metric,
    ObservationId,
    ReportDay,
    WeighIn,
    WeightExclusion,
    daily_median,
)
from fitness_intelligence.analytics.strength import DAY, Period
from fitness_intelligence.db.history_models import GarminCoverage, GarminIssue
from fitness_intelligence.db.models import SourceAccount
from fitness_intelligence.db.nutrition_models import BodyWeightObservation, DailyIntakeObservation
from fitness_intelligence.domain.endurance import Source
from fitness_intelligence.nutrition.intake import IntakeSelection, select_daily_intake
from fitness_intelligence.nutrition.weight import WeightDay, select_weight_day

# Reviewed producer contracts. Unknown mapping versions need a new provenance review.
GARMIN_NUTRITION_V1 = "garmin-personal-b3.2-v1"
FOOD_FIELD = "DailyNutritionSummaryDTO.dailyNutritionContent.calories"
type DayKey = tuple[UUID, str, date]


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
    aligned = day_aligned and all(w.report_date == coverage.provider_date for w in eligible)
    return DailyWeight(
        Metric(
            scope="account_day",
            status="observed"
            if eligible
            else "withheld"
            if excluded or selection.reasons
            else "missing",
            value=daily_median(tuple(w.value for w in eligible)),
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


def _read(
    db: Session, owner: UUID, period: Period, account: UUID, zones: Mapping[UUID, ZoneInfo]
) -> LongitudinalReport:
    accounts = {
        a.id: a
        for a in db.execute(
            select(SourceAccount.id, SourceAccount.provider, SourceAccount.status)
            .where(SourceAccount.user_id == owner)
            .order_by(SourceAccount.id)
        )
    }
    weight_account = accounts.get(account)
    if (
        weight_account is None
        or weight_account.provider != "garmin"
        or weight_account.status == "legacy_unresolved"
        or zones.keys() - accounts.keys()
    ):
        raise ValueError("invalid source account for report")
    sources = {i: Source(owner, a.provider, i) for i, a in accounts.items()}

    def in_range(
        model: type[DailyIntakeObservation | BodyWeightObservation | GarminCoverage | GarminIssue],
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

    def categories(model: type[GarminCoverage | GarminIssue]) -> ColumnElement[bool]:
        return (model.category == "intake") | (
            (model.category == "weight") & (model.source_account_id == account)
        )

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
            )
        )
    return LongitudinalReport(
        owner,
        sources[account],
        period,
        tuple(sorted((i, z.key) for i, z in zones.items())),
        tuple(days),
    )


def query_longitudinal(
    engine: Engine,
    *,
    owner_id: UUID,
    period: Period,
    weight_account_id: UUID,
    source_zones: Mapping[UUID, ZoneInfo] | None = None,
) -> LongitudinalReport:
    """Own a fresh read-only snapshot. Source zones describe verified calendars for this period."""
    if not isinstance(engine, Engine) or engine.dialect.name != "postgresql":
        raise ValueError("a PostgreSQL Engine is required for a fresh report transaction")
    zones = dict(source_zones or {})
    if not isinstance(period.zone, ZoneInfo) or any(
        not isinstance(z, ZoneInfo) for z in zones.values()
    ):
        raise ValueError("report and source calendars require IANA zones")
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
                return _read(db, owner_id, period, weight_account_id, zones)

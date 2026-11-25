"""Invented provider days spanning the Toronto spring clock change."""

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, localcontext
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest
import test_adaptive_cycle as adaptive
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from fitness_intelligence.analytics.longitudinal import LongitudinalReport, daily_median
from fitness_intelligence.analytics.strength import DAY, Period
from fitness_intelligence.db import longitudinal
from fitness_intelligence.db.history_models import GarminCoverage, GarminIssue
from fitness_intelligence.db.models import SourceAccount, User
from fitness_intelligence.db.nutrition_models import BodyWeightObservation, DailyIntakeObservation
from fitness_intelligence.db.plan_models import (
    PlanDecision,
    PlanRevision,
    SessionOutcome,
    TrainingPlan,
)
from fitness_intelligence.nutrition.intake import IntakeSelection
from fitness_intelligence.planning.outcomes import Actual
from fitness_intelligence.planning.planner import Slot

START = date(2025, 3, 3)
ZONE = ZoneInfo("America/Toronto")
PERIOD = Period(START, START + 7 * DAY, ZONE)
NOW = datetime(2025, 3, 12, tzinfo=UTC)
VERSION = "garmin-personal-b3.2-v1"
SUMMARY = "UserDailySummaryDto.consumedKilocalories"
FOOD = "DailyNutritionSummaryDTO.dailyNutritionContent.calories"
SEGMENT = "a" * 64
approved_cycle = adaptive.cycle


def account(db: Session, owner: UUID | None = None, provider: str = "garmin") -> SourceAccount:
    if owner is None:
        user = User()
        db.add(user)
        db.flush()
        owner = user.id
    source = SourceAccount(
        user_id=owner, provider=provider, status="active", provider_account_id=str(uuid4())
    )
    db.add(source)
    db.flush()
    return source


def intake(
    src: SourceAccount, n: int, kcal: int, field: str = SUMMARY, presence: bool | None = None
) -> DailyIntakeObservation:
    return DailyIntakeObservation(
        user_id=src.user_id,
        source_account_id=src.id,
        provider=src.provider,
        local_date=START + n * DAY,
        reported_kcal=kcal,
        source_field=field,
        retrieved_at=NOW,
        mapping_version=VERSION,
        source_data_present=presence,
        completeness="unknown",
    )


def weight(
    src: SourceAccount, n: int, grams: str, hour: int = 12, scope: str | None = SEGMENT
) -> BodyWeightObservation:
    day = START + n * DAY
    return BodyWeightObservation(
        user_id=src.user_id,
        source_account_id=src.id,
        provider=src.provider,
        local_date=day,
        source_value=Decimal(grams),
        source_unit="g",
        documented_source_unit="kg",
        mass_kg=Decimal(grams) / 1000,
        measured_at=datetime.combine(day, time(hour), UTC),
        time_resolution_us=1000,
        source_field="DateWeightDTO.weight",
        mapping_version=VERSION,
        verification_scope=scope,
        retrieved_at=NOW,
    )


def coverage(
    src: SourceAccount, n: int, category: str, status: str, count: int | None
) -> GarminCoverage:
    return GarminCoverage(
        user_id=src.user_id,
        source_account_id=src.id,
        provider=src.provider,
        local_date=START + n * DAY,
        category=category,
        status=status,
        attempted_at=NOW,
        last_success=NOW
        if status in {"observed", "empty"}
        else NOW - DAY
        if count is not None
        else None,
        eligible_count=count,
        policy=SEGMENT if category == "weight" else "history-v1",
        pass_key=str(uuid4()),
        receipts={"sources": {"daily": "observed", "food": "unavailable"}}
        if category == "intake" and status == "partial"
        else {},
    )


def issue(src: SourceAccount, n: int, category: str, reason: str) -> GarminIssue:
    return GarminIssue(
        user_id=src.user_id,
        source_account_id=src.id,
        provider=src.provider,
        local_date=START + n * DAY,
        category=category,
        subject="day",
        reason=reason,
        evidence_digest="synthetic",
        first_seen=NOW,
        last_seen=NOW,
    )


def report(
    db: Session, src: SourceAccount, zones: dict[UUID, ZoneInfo] | None = None
) -> LongitudinalReport:
    return longitudinal.query_longitudinal(
        db.get_bind(),
        owner_id=src.user_id,
        period=PERIOD,
        weight_account_id=src.id,
        source_zones=zones,
    )


def test_decimal_median_independent_of_display_precision() -> None:
    with localcontext() as ctx:
        ctx.prec = 4
        a, b = Decimal("70.000000001"), Decimal("70.000000002")
        assert daily_median((b, a)) == Decimal("70.0000000015")
        assert daily_median((b, a, a)) == a
        assert daily_median(()) is None


def test_requires_fresh_postgres_engine() -> None:
    with pytest.raises(ValueError, match="PostgreSQL Engine"):
        longitudinal.query_longitudinal(
            create_engine("sqlite://"), owner_id=uuid4(), period=PERIOD, weight_account_id=uuid4()
        )


def test_seven_provider_days(db: Session) -> None:
    src = account(db)
    a, b = intake(src, 0, 2100), intake(src, 0, 2100, FOOD)
    old = weight(src, 1, "70400", scope=None)
    db.add_all(
        [
            a,
            b,
            intake(src, 1, 0, presence=True),
            intake(src, 2, 0, "UserDailySummaryV2DTO.calories.consumedValue"),
            intake(src, 4, 1800),
            intake(src, 4, 1801, FOOD),
            intake(src, 5, 2000),
            intake(src, 5, 2000, FOOD),
            issue(src, 5, "intake", "source_disagreement"),
            intake(src, 6, 0, FOOD),
            weight(src, 0, "70000.000002", 13),
            weight(src, 0, "70000.000001", 12),
            old,
            weight(src, 2, "71000"),
            weight(src, 2, "71500", 13),
            issue(src, 2, "weight", "possible_retime"),
            weight(src, 4, "72000", scope=None),
            weight(src, 5, "73000"),
            weight(src, 6, "74000", 2),
            intake(src, -1, 999),
            intake(src, 7, 999),
            weight(src, 7, "55000"),
            coverage(src, 0, "intake", "partial", None),
            coverage(src, 0, "weight", "observed", 2),
            coverage(src, 2, "weight", "observed", 2),
            coverage(src, 3, "intake", "empty", 0),
            coverage(src, 3, "weight", "empty", 0),
            coverage(src, 4, "weight", "observed", 1),
            coverage(src, 5, "weight", "failed", 1),
            coverage(src, 6, "weight", "partial", None),
        ]
    )
    db.commit()
    result = report(db, src, {src.id: ZONE})
    assert result == report(db, src, {src.id: ZONE})
    assert [d.provider_date for d in result.days] == [START + DAY * i for i in range(7)]
    assert [d.intake.metric.value for d in result.days] == [2100, 0, None, None, None, None, 0]
    assert [d.intake.metric.status for d in result.days] == [
        "reported",
        "explicit_zero",
        "withheld",
        "missing",
        "conflict",
        "conflict",
        "explicit_zero",
    ]
    mon, tue, wed, thu, fri, sat, sun = result.days
    assert mon.intake.metric.scope == "owner_day" and mon.intake.metric.retained_count == 2
    assert [f.identity.id for f in mon.intake.facts] == sorted([a.id, b.id])
    assert mon.intake.metric.supporting == tuple(f.identity for f in mon.intake.facts)
    assert mon.intake.coverage[0].source_receipts == (
        ("daily", "observed"),
        ("food", "unavailable"),
    )
    assert (
        mon.intake.coverage[0].status == "partial" and mon.intake.logging_completeness == "unknown"
    )
    assert all(f.upstream_writer is None and f.recorded_at is None for f in mon.intake.facts)
    assert wed.intake.metric.reasons == ("unsupported_zero",)
    assert thu.intake.metric.reasons == ("empty", "no_intake_observation")
    assert sat.intake.coverage[0].issues[0].reason == "source_disagreement"
    assert mon.weight.metric.value == Decimal("70.0000000015")
    assert [w.source_value for w in mon.weight.measurements] == [
        Decimal("70000.000001"),
        Decimal("70000.000002"),
    ]
    assert all(
        w.verification_scope == SEGMENT
        and w.verification_basis == "historical_segment"
        and w.documented_unit == "kg"
        and w.interpreted_unit == "g"
        and w.time_resolution_us == 1000
        for w in mon.weight.measurements
    )
    assert (
        tue.weight.coverage.observations_without_coverage
        and tue.weight.coverage.last_success is None
    )
    assert (
        tue.weight.measurements[0].identity.id == old.id
        and tue.weight.measurements[0].verification_basis == "bounded_operator_verified"
    )
    assert (
        wed.weight.coverage.reconciliation == "unresolved" and wed.weight.metric.retained_count == 2
    )
    assert (
        wed.weight.metric.eligible_count == 0
        and len(wed.weight.excluded) == 2
        and wed.weight.metric.value is None
    )
    assert wed.weight.metric.reasons == ("possible_retime",)
    assert thu.weight.metric.reasons == ("empty", "no_weight_observation")
    assert fri.weight.metric.reasons == ("unverified_weight_unit",)
    assert sat.weight.metric.value == 73 and sat.weight.coverage.status == "failed"
    assert (
        sat.weight.coverage.last_success == NOW - DAY
        and sat.weight.coverage.attempted_at == NOW
        and sat.weight.coverage.last_success_count == 1
    )
    assert sun.weight.measurements[0].report_date == START + 5 * DAY
    assert sun.weight.metric.report_date is None and sun.weight.metric.value == 74
    assert sun.intake.metric.report_date == START + 6 * DAY


def test_owner_scope_account_binding_and_calendar(db: Session) -> None:
    src = account(db)
    other = account(db, src.user_id)
    foreign = account(db)
    unrelated = account(db, src.user_id, "hevy")
    db.add_all(
        [
            intake(src, 0, 1500),
            intake(other, 0, 1501),
            intake(foreign, 0, 999),
            intake(src, 1, 1500),
            intake(other, 1, 1500),
            weight(other, 0, "80000"),
            weight(foreign, 0, "90000"),
            issue(foreign, 1, "intake", "source_disagreement"),
        ]
    )
    db.commit()
    days = report(db, src).days
    assert days[0].intake.metric.status == "conflict" and days[0].weight.metric.retained_count == 0
    assert {f.identity.source.source_account_id for f in days[0].intake.facts} == {src.id, other.id}
    assert days[1].intake.metric.reasons == ("incompatible_or_unknown_provider_days",)
    assert days[1].intake.metric.value is None and len(days[1].intake.facts) == 2
    assert (
        report(db, src, {src.id: ZONE, other.id: ZoneInfo("UTC")}).days[1].intake.metric.value
        is None
    )
    assert report(db, src, {src.id: ZONE, other.id: ZONE}).days[1].intake.metric.value == 1500
    for invalid in (unrelated.id, foreign.id):
        with pytest.raises(ValueError, match="invalid source account"):
            longitudinal.query_longitudinal(
                db.get_bind(), owner_id=src.user_id, period=PERIOD, weight_account_id=invalid
            )
    with pytest.raises(ValueError, match="PostgreSQL Engine"):
        longitudinal.query_longitudinal(
            db.connection(), owner_id=src.user_id, period=PERIOD, weight_account_id=src.id
        )


def test_partial_refresh_and_empty_do_not_revoke_retained_facts(db: Session) -> None:
    src = account(db)
    legacy = weight(src, 0, "68000", scope=None)
    legacy.retrieved_at = NOW - DAY
    db.add_all(
        [
            legacy,
            coverage(src, 0, "weight", "failed", None),
            intake(src, 1, 0, FOOD),
            coverage(src, 1, "intake", "empty", 0),
        ]
    )
    db.commit()
    first, second, *_ = report(db, src).days
    assert first.weight.metric.value == 68
    assert first.weight.measurements[0].verification_basis == "bounded_operator_verified"
    assert (
        second.intake.metric.status == "explicit_zero"
        and second.intake.coverage[0].status == "empty"
    )


def test_repeatable_read_during_concurrent_repair(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = account(db)
    original = intake(src, 0, 1800)
    db.add_all([original, weight(src, 0, "70000"), coverage(src, 0, "weight", "observed", 1)])
    db.commit()
    selector = longitudinal.select_daily_intake

    def repair(reader: Session, owner: UUID, day: date) -> IntakeSelection:
        if day == START:
            original.reported_kcal = 1900
            original.retrieved_at = NOW + DAY
            db.add(issue(src, 0, "weight", "ambiguous_correction"))
            db.commit()
        return selector(reader, owner, day)

    with monkeypatch.context() as patch:
        patch.setattr(longitudinal, "select_daily_intake", repair)
        before = report(db, src).days[0]
    after = report(db, src).days[0]
    assert before.intake.metric.value == before.intake.facts[0].value == 1800
    assert (
        before.weight.metric.value == 70
        and before.weight.coverage.reconciliation == "no_open_issue"
    )
    assert after.intake.metric.value == after.intake.facts[0].value == 1900
    assert after.intake.facts[0].retrieved_at == NOW + DAY
    assert (
        after.weight.metric.value is None and after.weight.coverage.reconciliation == "unresolved"
    )


def test_server_enforces_read_only(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    src = account(db)
    db.commit()

    def probe(reader: Session, owner: UUID, day: date) -> None:
        assert not reader.autoflush
        assert reader.scalar(text("SHOW transaction_isolation")) == "repeatable read"
        reader.execute(text("DELETE FROM daily_intake_observations WHERE false"))

    monkeypatch.setattr(longitudinal, "select_daily_intake", probe)
    with pytest.raises(DBAPIError) as exc:
        report(db, src)
    assert exc.value.orig.sqlstate == "25006"


def test_report_preserves_records(db: Session, approved_cycle: adaptive.Cycle) -> None:
    src = account(db, approved_cycle.owner)
    approved_cycle.record(Slot.SHORT_RUN, 5, Actual(status="completed", run_seconds=1200))
    db.add_all(
        [
            weight(src, 0, "71000"),
            intake(src, 1, 1950),
            coverage(src, 0, "weight", "observed", 1),
            issue(src, 0, "weight", "possible_retime"),
        ]
    )
    db.commit()

    def fingerprint() -> tuple:
        result = []
        for model in (
            TrainingPlan,
            PlanRevision,
            PlanDecision,
            SessionOutcome,
            BodyWeightObservation,
            DailyIntakeObservation,
            GarminCoverage,
            GarminIssue,
        ):
            table = model.__table__
            rows = db.execute(select(table).order_by(*table.primary_key)).all()
            assert rows
            result.append(tuple(rows))
        return tuple(result)

    before = fingerprint()
    report(db, src)
    assert fingerprint() == before


def test_dst_instants_and_half_open_source_dates(db: Session) -> None:
    src = account(db)
    end = PERIOD.stop
    # Across the spring transition local midnight moves from 05:00 to 04:00 UTC.
    start_instant = datetime.combine(START, time.min, ZONE).astimezone(UTC)
    stop_instant = datetime.combine(end, time.min, ZONE).astimezone(UTC)
    assert (start_instant.hour, stop_instant.hour) == (5, 4)
    first = weight(src, 0, "69000", start_instant.hour)
    last = weight(src, 6, "70000")
    last.measured_at = stop_instant - timedelta(milliseconds=1)
    outside = weight(src, 7, "71000", stop_instant.hour)
    db.add_all([first, last, outside])
    db.commit()
    rows = report(db, src, {src.id: ZONE}).days
    assert rows[0].weight.measurements[0].report_date == START
    assert rows[-1].weight.measurements[0].report_date == end - DAY
    assert sum(d.weight.metric.eligible_count for d in rows) == 2


def test_verification_is_per_measurement(db: Session) -> None:
    src = account(db)
    eligible = weight(src, 0, "68000", hour=7)
    absent = weight(src, 0, "72000", hour=8, scope=None)
    malformed = weight(src, 0, "73000", hour=9, scope="unverified")
    mismapped = weight(src, 0, "74000", hour=10)
    mismapped.mass_kg = Decimal("75")
    unrecognized = weight(src, 1, "71000", scope=None)
    unrecognized.mapping_version = "unverified-import"
    db.add_all(
        [
            eligible,
            absent,
            malformed,
            mismapped,
            unrecognized,
            coverage(src, 0, "weight", "observed", 4),
        ]
    )
    db.commit()
    first, second, *_ = (day.weight for day in report(db, src).days)
    assert first.metric.value == 68 and first.metric.eligible_count == 1
    assert {x.identity.id for x in first.excluded} == {absent.id, malformed.id, mismapped.id}
    assert second.metric.value is None and second.metric.reasons == ("unverified_weight_unit",)

"""Synthetic provider calendars, independent expenditure components and verified weight series."""

from dataclasses import replace
from datetime import date
from decimal import Decimal, localcontext
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.orm import Session
from test_longitudinal import (
    PERIOD,
    SEGMENT,
    START,
    ZONE,
    account,
    coverage,
    energy,
    intake,
    issue,
    weight,
)

from fitness_intelligence.analytics.longitudinal import (
    Coverage,
    DailyIntake,
    DailyWeight,
    LongitudinalReport,
    Metric,
    ReportDay,
)
from fitness_intelligence.analytics.strength import DAY, Period
from fitness_intelligence.analytics.weekly import (
    WeeklyIntake,
    WeightChange,
    WeightContinuity,
    aggregate_weeks,
)
from fitness_intelligence.db.longitudinal import query_longitudinal
from fitness_intelligence.domain.endurance import DailyMetric, Source


def test_empty_clipped_calendar_and_stable_order_without_database() -> None:
    period = Period(date(2025, 3, 8), date(2025, 3, 12), ZONE)
    source = Source(UUID(int=1), "garmin", UUID(int=2))
    days = []
    for n in range(4):
        day = period.start + n * DAY
        c = Coverage(
            source, "active", "weight", day, "empty", None, None, None, None, None, (), None, (), 0
        )
        cell = Metric("account_day", "missing", None, "kg", None, (), 0, ("no_weight_observation",))
        days.append(
            ReportDay(
                day,
                DailyIntake(
                    replace(
                        cell, scope="owner_day", unit="kcal", reasons=("no_intake_observation",)
                    ),
                    "unknown",
                    (),
                    (replace(c, category="intake"),),
                ),
                DailyWeight(cell, (), (), c),
            )
        )
    daily = LongitudinalReport(source.owner_id, source, period, (), tuple(days))
    result = aggregate_weeks(daily, reference_date=period.stop)
    shuffled = replace(daily, days=tuple(reversed(days)))
    assert aggregate_weeks(shuffled, reference_date=period.stop) == result
    first, second = result.weeks
    assert first.requested_dates == (period.start, period.start + DAY) and first.closed
    assert not first.fully_requested and not second.fully_requested and not second.closed
    for week in result.weeks:
        calories = week.intake.calories
        assert (
            calories.observed_subtotal_kcal is None and calories.mean_per_eligible_date_kcal is None
        )
        assert calories.sample.eligible_dates == () and week.weight.series == ()
        assert calories.sample.dates_with_status("missing") == week.requested_dates
        assert week.weight.changes[0].change_kg is None
        assert "no_eligible_weight" in week.weight.changes[0].reasons
        assert week.expenditure is None
    with pytest.raises(ValueError, match="date spine"):
        aggregate_weeks(replace(daily, days=(days[0],) * 4), reference_date=period.stop)


def test_weekly_intake_checks_source_changes_between_days(db: Session) -> None:
    a = account(db)
    b = account(db, a.user_id)
    db.add_all([intake(a, 0, 1800), intake(b, 1, 0, presence=True)])
    db.commit()

    def result(zones: dict[UUID, ZoneInfo]) -> WeeklyIntake:
        daily = query_longitudinal(
            db.get_bind(),
            owner_id=a.user_id,
            period=PERIOD,
            weight_account_id=a.id,
            source_zones=zones,
        )
        return aggregate_weeks(daily, reference_date=PERIOD.stop).weeks[0].intake

    for zones in ({}, {a.id: ZONE}, {a.id: ZONE, b.id: ZoneInfo("UTC")}):
        week = result(zones)
        assert week.calories.observed_subtotal_kcal is None
        assert week.calories.mean_per_eligible_date_kcal is None
        assert week.calories.subtotal_status == "unverified_common_calendar"
        assert len(week.calories.sample.eligible_dates) == 2
        assert len(week.coverage) == 2 and week.explicit_zero_dates == (START + DAY,)
    compatible = result({a.id: ZoneInfo("UTC"), b.id: ZoneInfo("UTC")})
    assert compatible.calories.mean_per_eligible_date_kcal == 900
    assert compatible.calories.sample.report_calendar_aligned is False


def test_expenditure_binding_independent_coverage_and_holds(db: Session) -> None:
    src = account(db)
    selected = account(db, src.user_id)
    outsider = account(db)
    hevy = account(db, src.user_id, "hevy")
    field_hold = issue(selected, 0, "expenditure", "disputed_component")
    field_hold.subject = DailyMetric.ACTIVE_ENERGY
    legacy = energy(selected, 0, DailyMetric.TOTAL_ENERGY, 2150)
    legacy.mapping_version = legacy.retrieved_at = legacy.source_field = None
    db.add_all(
        [
            legacy,
            energy(selected, 0, DailyMetric.ACTIVE_ENERGY, 400),
            energy(selected, 0, DailyMetric.BASAL_ENERGY, 1750, "measured"),
            energy(selected, 1, DailyMetric.ACTIVE_ENERGY, 0),
            energy(selected, 2, DailyMetric.ACTIVE_ENERGY, 350),
            issue(selected, 2, "expenditure", "disputed_day"),
            energy(src, 0, DailyMetric.TOTAL_ENERGY, 888),
            energy(outsider, 0, DailyMetric.TOTAL_ENERGY, 999),
            issue(outsider, 0, "expenditure", "foreign_issue"),
            coverage(selected, 0, "expenditure", "partial", None),
        ]
    )
    db.commit()

    def query(i: UUID | None) -> LongitudinalReport:
        return query_longitudinal(
            db.get_bind(),
            owner_id=src.user_id,
            period=PERIOD,
            weight_account_id=src.id,
            expenditure_account_id=i,
        )

    assert query(None).days[0].expenditure is None
    for i in (outsider.id, hevy.id):
        with pytest.raises(ValueError, match="invalid source account"):
            query(i)
    db.add(field_hold)
    db.commit()
    report = query(selected.id)
    week = aggregate_weeks(report, reference_date=PERIOD.stop).weeks[0].expenditure
    assert week.total.observed_subtotal_kcal == 2150 and week.total.method == "wearable_estimate"
    assert week.active.mean_per_eligible_date_kcal == 0 and week.active.sample.eligible_dates == (
        START + DAY,
    )
    assert week.basal.observed_subtotal_kcal is None
    assert week.coverage.source.source_account_id == selected.id
    assert week.coverage.unresolved_dates == (START, START + 2 * DAY)
    assert week.coverage.days[0].status == "partial"
    mon = report.days[0].expenditure
    assert mon.active.reasons == ("disputed_component",)
    assert mon.basal.reasons == ("ineligible_method_or_unit",)
    assert report.days[2].expenditure.active.reasons == ("disputed_day",)
    assert mon.facts[0].source_field is None and mon.facts[0].retrieved_at is None


def test_weight_comparisons_require_closed_supported_comparable_weeks(db: Session) -> None:
    src = account(db)
    period = Period(START, START + 14 * DAY, ZONE)
    rows = [
        weight(src, 0, "68000.000001", hour=10),
        weight(src, 0, "72000.000002", hour=12),
        weight(src, 2, "69000"),
        weight(src, 4, "73000"),
        weight(src, 7, "71000", scope="b" * 64),
        weight(src, 9, "70500", scope="b" * 64),
        weight(src, 12, "73000", scope="b" * 64),
    ]
    db.add_all(rows)
    db.commit()

    def read(p: Period = period) -> LongitudinalReport:
        return query_longitudinal(
            db.get_bind(),
            owner_id=src.user_id,
            period=p,
            weight_account_id=src.id,
            source_zones={src.id: ZONE},
        )

    daily = read()
    evidence = WeightContinuity(
        daily.weight_source,
        period.start,
        period.stop,
        frozenset({SEGMENT, "b" * 64}),
        "synthetic-scale-and-protocol-review",
    )

    def compare(r: LongitudinalReport = daily, reference: date = period.stop) -> WeightChange:
        return (
            aggregate_weeks(r, reference_date=reference, weight_continuity=evidence)
            .weeks[-1]
            .weight.changes[0]
        )

    separate = aggregate_weeks(daily, reference_date=period.stop).weeks
    assert separate[1].weight.changes[0].reasons == ("no_comparable_earlier_series",)
    with localcontext() as ctx:
        ctx.prec = 4
        change = compare()
    assert change.earlier.median_kg == Decimal("70.0000000015") and change.later.median_kg == 71
    assert change.change_kg == Decimal("0.9999999985") and change.reasons == ()
    assert [d.day for d in change.earlier.dates] == [START, START + 2 * DAY, START + 4 * DAY]
    assert change.earlier.observation_count == 4 and change.later.observation_count == 3
    assert compare(reference=period.stop - DAY).reasons == ("later_week_open",)
    clipped = read(Period(START + DAY, period.stop, ZONE))
    assert "earlier_week_clipped" in compare(clipped).reasons
    with pytest.raises(ValueError, match="owner/account"):
        aggregate_weeks(
            daily,
            reference_date=period.stop,
            weight_continuity=replace(
                evidence, source=replace(daily.weight_source, source_account_id=UUID(int=42))
            ),
        )
    # Same fingerprint and reviewed interval cannot bridge a change of measurement writer.
    rows[-1].upstream_writer = "different-scale"
    db.commit()
    split = (
        aggregate_weeks(read(), reference_date=period.stop, weight_continuity=evidence)
        .weeks[1]
        .weight
    )
    assert sorted(s.observation_count for s in split.series) == [1, 2]
    assert all(c.change_kg is None for c in split.changes)
    assert "later_span_under_three_days" in split.changes[0].reasons
    assert "later_fewer_than_three_dates" in split.changes[0].reasons


def test_mixed_regimes_within_a_day_and_all_selected_dates(db: Session) -> None:
    src = account(db)
    first = weight(src, 0, "70000")
    first.upstream_writer = "scale-a"
    second = weight(src, 0, "80000", hour=14)
    second.upstream_writer = "scale-b"
    db.add_all([intake(src, n, 1500 + n) for n in range(7)])
    db.add_all([first, second])
    db.commit()
    daily = query_longitudinal(
        db.get_bind(), owner_id=src.user_id, period=PERIOD, weight_account_id=src.id
    )
    weight_day = daily.days[0].weight
    assert weight_day.metric.status == "withheld" and weight_day.metric.value is None
    assert weight_day.metric.reasons == ("incompatible_weight_regimes",)
    assert weight_day.excluded == ()
    assert weight_day.metric.eligible_count == weight_day.metric.retained_count == 2
    assert [w.identity.id for w in weight_day.measurements] == [first.id, second.id]
    assert weight_day.metric.supporting == tuple(w.identity for w in weight_day.measurements)
    week = aggregate_weeks(daily, reference_date=PERIOD.stop).weeks[0]
    assert {
        s.key.writer: (s.median_kg, s.dates[0].measurements[0].identity.id)
        for s in week.weight.series
    } == {"scale-a": (70, first.id), "scale-b": (80, second.id)}
    assert week.weight.sample.eligible_dates == ()
    assert week.weight.sample.eligible_observation_count == 2
    assert week.intake.calories.observed_subtotal_kcal == 10521
    assert week.intake.calories.subtotal_status == "all_requested_dates"
    assert week.intake.calories.mean_per_eligible_date_kcal == 1503
    assert week.intake.coverage[0].acquisition_counts == (("never_queried", 7),)


@pytest.mark.parametrize(
    ("writers", "reason"),
    [
        (("scale-a", "scale-a"), None),
        ((None, None), None),
        (("scale-a", None), "weight_comparability_unverified"),
    ],
)
def test_same_day_writer_evidence(
    db: Session, writers: tuple[str | None, str | None], reason: str | None
) -> None:
    src = account(db)
    first, second = weight(src, 0, "70000"), weight(src, 0, "80000", hour=14)
    first.upstream_writer, second.upstream_writer = writers
    db.add_all([first, second])
    db.commit()
    daily = query_longitudinal(
        db.get_bind(), owner_id=src.user_id, period=PERIOD, weight_account_id=src.id
    )
    metric = daily.days[0].weight.metric
    series = aggregate_weeks(daily, reference_date=PERIOD.stop).weeks[0].weight.series
    assert metric.eligible_count == 2
    if reason:
        assert (metric.status, metric.value, metric.reasons) == ("withheld", None, (reason,))
        assert sorted(s.median_kg for s in series) == [70, 80]
    else:
        assert (metric.status, metric.value, metric.reasons) == ("observed", 75, ())
        assert [s.median_kg for s in series] == [75]


def test_reviewed_continuity_combines_same_day_verified_partitions(db: Session) -> None:
    src = account(db)
    second_scope = "b" * 64
    db.add_all([weight(src, 0, "70000"), weight(src, 0, "80000", hour=14, scope=second_scope)])
    db.commit()
    daily = query_longitudinal(
        db.get_bind(), owner_id=src.user_id, period=PERIOD, weight_account_id=src.id
    )
    weight_day = daily.days[0].weight
    assert weight_day.metric.value is None
    assert weight_day.metric.reasons == ("weight_comparability_unverified",)
    separate = aggregate_weeks(daily, reference_date=PERIOD.stop).weeks[0].weight.series
    assert sorted(s.median_kg for s in separate) == [70, 80]
    continuity = WeightContinuity(
        daily.weight_source,
        PERIOD.start,
        PERIOD.stop,
        frozenset({SEGMENT, second_scope}),
        "synthetic-common-scale-review",
    )
    (combined,) = (
        aggregate_weeks(daily, reference_date=PERIOD.stop, weight_continuity=continuity)
        .weeks[0]
        .weight.series
    )
    assert combined.median_kg == 75 and combined.dates[0].measurements == weight_day.measurements

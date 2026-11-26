"""Synthetic D1E reports through the owner-bound D1D query and pure report entry point."""

from dataclasses import replace
from decimal import Decimal
from fractions import Fraction

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_longitudinal import NOW, PERIOD, START, ZONE, account, coverage, issue
from test_training_exposure import lift, outing, read, recovery

from fitness_intelligence.analytics.performance import (
    PerformanceReport,
    Review,
    RunningTask,
    StrengthTask,
    analyze_performance,
    compare_running,
    compare_strength,
)
from fitness_intelligence.analytics.references import RecoveryRegime
from fitness_intelligence.analytics.strength import DAY, Period
from fitness_intelligence.analytics.weekly import aggregate_weeks
from fitness_intelligence.db.history_models import GarminCoverage
from fitness_intelligence.domain.endurance import DailyMetric

SQUAT = StrengthTask(
    "squat", "high bar", "barbell", "external_kg", "primary", "paused", match_ordinal=False
)
RUN = RunningTask(
    Decimal(5000), "park loop", "elapsed_s", "reported RPE 6", "dry, calm", "uninterrupted"
)


def test_strength_differences_and_top_support(db: Session) -> None:
    src = account(db)
    hevy = account(db, src.user_id, "hevy")
    first = lift(
        db,
        hevy,
        0,
        "first",
        [
            (
                "squat",
                [
                    ("normal", 5, True),
                    ("normal", 5, True),
                    ("normal", 5, False),
                    ("warmup", 5, True),
                ],
            )
        ],
    )
    first.exercises[0].sets[2].weight_kg = 70
    lift(db, hevy, 1, "second", [("squat", [("normal", 6, True)])])
    for day, kg, rpe in [(2, 65, 7), (3, 60, 8), (4, 60, None)]:
        w = lift(db, hevy, day, str(day), [("squat", [("normal", 6, True)])])
        w.exercises[0].sets[0].weight_kg = kg
        w.exercises[0].sets[0].rpe = rpe
    db.commit()
    weekly = aggregate_weeks(read(db, src, hevy), reference_date=PERIOD.stop)
    reviews = {f: Review(SQUAT, "synthetic review") for f in weekly.weeks[0].strength.facts}
    report = analyze_performance(weekly, strength_reviews=reviews)
    a, b, inferred, warm, second, third, harder, unknown = report.strength
    winner = min((a, b), key=lambda p: p.fact.row.set_id)
    assert winner.workout_best and winner.estimated_1rm_kg == Decimal("70.00")
    assert sum(p.workout_best for p in (a, b)) == 1
    assert inferred.workout_best and inferred.estimated_1rm_kg == Decimal("81.67")
    assert warm.estimated_1rm_kg is None
    assert report.successive_estimates[0].earlier == winner
    assert report.successive_estimates[0].estimated_1rm_kg.value == 2
    assert compare_strength(a, second).reps_at_fixed_load.value == 1
    assert compare_strength(second, third).kg_at_fixed_reps.value == 5
    assert report.fixed_work_comparisons("load")[0].reps_at_fixed_load.value == 1
    assert report.fixed_work_comparisons("repetitions")[0].kg_at_fixed_reps.value == 5
    assert compare_strength(second, harder).achieved_rpe_at_fixed_work.value == 1
    assert compare_strength(second, harder).estimated_1rm_kg.reasons == ("different_rpe",)
    assert compare_strength(second, unknown).kg_at_fixed_reps.value is None
    assert compare_strength(inferred, second).estimated_1rm_kg.value is None
    filtered = analyze_performance(
        weekly, strength_reviews=reviews, rpe_range=(Decimal(7), Decimal(7))
    )
    assert filtered.strength[0].estimated_1rm_kg == 70
    assert all(filtered.strength[i].estimated_1rm_kg is None for i in (2, 6, 7))
    for field, value in (
        ("equipment", "machine"),
        ("variation", "low bar"),
        ("protocol", "touch and go"),
        ("load_convention", "per side"),
        ("role", "backoff"),
        ("movement", None),
    ):
        changed = reviews | {second.fact: Review(replace(SQUAT, **{field: value}), "other review")}
        changed_point = analyze_performance(weekly, strength_reviews=changed).strength[4]
        assert compare_strength(a, changed_point).reps_at_fixed_load.value is None
    ordinal = analyze_performance(
        weekly,
        strength_reviews={
            f: Review(replace(SQUAT, match_ordinal=True), "ordinal review") for f in reviews
        },
    )
    assert (
        compare_strength(ordinal.strength[1], ordinal.strength[4]).reps_at_fixed_load.value is None
    )
    protocol = analyze_performance(
        weekly,
        strength_reviews={
            f: Review(replace(SQUAT, effort_basis="reviewed_protocol"), "fixed protocol")
            for f in reviews
        },
    )
    assert (
        compare_strength(protocol.strength[4], protocol.strength[-1]).reps_at_fixed_load.value == 0
    )
    assert (
        compare_strength(
            protocol.strength[4], protocol.strength[-1]
        ).achieved_rpe_at_fixed_work.value
        is None
    )


def test_ambiguous_movement_and_exact_review_scope(db: Session) -> None:
    src = account(db)
    hevy = account(db, src.user_id, "hevy")
    lift(db, hevy, 0, "ambiguous", [("", [("normal", 5, True)])])
    db.commit()
    weekly = aggregate_weeks(read(db, src, hevy), reference_date=PERIOD.stop)
    (fact,) = weekly.weeks[0].strength.facts
    for f in (
        replace(fact, external_id="other"),
        replace(fact, source=replace(fact.source, source_account_id=src.id)),
        replace(fact, source=replace(fact.source, owner_id=hevy.id)),
    ):
        with pytest.raises(ValueError, match="exact selected"):
            analyze_performance(weekly, strength_reviews={f: Review(SQUAT, "review")})
    point = analyze_performance(weekly, strength_reviews={fact: Review(SQUAT, "review")}).strength[
        0
    ]
    assert "unverified_movement" in point.reasons and point.estimated_1rm_kg is None


def test_reviewed_running_and_withheld_tasks(db: Session) -> None:
    src = account(db)
    for n, (activity, moving, elapsed) in enumerate(
        [(1600, 1500, 1700), (1610, 1450, 1640), (1500, None, 1550)]
    ):
        outing(db, src, n, str(n + 1), "running", "running", 5000, activity, moving, elapsed)
    db.add(issue(src, 2, "activities", "disputed"))
    db.add(coverage(src, 0, "activities", "partial", None))
    db.commit()
    weekly = aggregate_weeks(read(db, src), reference_date=PERIOD.stop)
    facts = [f for day in weekly.weeks[0].endurance.days for f in day.facts]

    def reviewed(task: RunningTask) -> PerformanceReport:
        return analyze_performance(
            weekly, running_reviews={f: Review(task, "synthetic task log") for f in facts}
        )

    for field, expected in (("duration_s", 10), ("elapsed_s", -60), ("moving_s", -50)):
        report = reviewed(replace(RUN, timing=field))
        assert len(report.successive_runs) == 1
        assert report.successive_runs[0].seconds.value == expected
        assert "activity_reconciliation_hold" in report.running[-1].reasons
    assert reviewed(RUN).running[0].fact.pace[1] == 250
    assert not analyze_performance(weekly).successive_runs
    for field, value in (
        ("course_or_protocol", None),
        ("timing", None),
        ("effort", None),
        ("conditions", None),
        ("course_or_protocol", "unknown"),
        ("restrictions_or_interruptions", None),
        ("distance_m", Decimal(4990)),
    ):
        report = reviewed(replace(RUN, **{field: value}))
        assert len(report.running) == 3 and not report.successive_runs
        assert compare_running(*report.running[:2]).seconds.reasons
    changed = analyze_performance(
        weekly,
        running_reviews={
            facts[0]: Review(RUN, "first"),
            facts[1]: Review(replace(RUN, conditions="snow"), "second"),
        },
    )
    assert compare_running(*changed.running[:2]).seconds.reasons == ("different_running_task",)
    with pytest.raises(ValueError, match="exact selected"):
        analyze_performance(
            weekly,
            running_reviews={replace(facts[0], distance_m=Decimal(4000)): Review(RUN, "stale")},
        )


def test_representative_running_and_observed_strength_consistency(db: Session) -> None:
    src = account(db)
    hevy = account(db, src.user_id, "hevy")
    period = Period(START - 2 * DAY, START + 34 * DAY, ZONE)
    lift(db, hevy, 0, "confirmed", [("squat", [("normal", 5, True)])])
    lift(db, hevy, 8, "inferred", [("squat", [("normal", 5, False)])])
    # Prior four native weeks: two complete zeros, partial listing, completed positive listing.
    success = NOW + 60 * DAY
    for i in range(35):
        if i in (14, 21):
            outing(db, src, i, str(i), "running", "running", 5000, 1500, None, 1600)
            row = coverage(src, i, "activities", "observed" if i == 21 else "partial", 1)
        else:
            row = coverage(src, i, "activities", "empty", 0)
            row.receipts = {"empty_activity_scan": {"started_at": (success - DAY).isoformat()}}
        row.last_success = row.attempted_at = success
        db.add(row)
    db.commit()

    def report() -> PerformanceReport:
        return analyze_performance(
            aggregate_weeks(read(db, src, hevy, p=period), reference_date=START + 30 * DAY)
        )

    performance = report()
    refs = performance.running_references(START + 28 * DAY)
    assert {r.metric for r in refs} == {
        "sessions",
        "distance_m",
        "duration_s",
        "moving_s",
        "elapsed_s",
    }
    for r in refs:
        assert r.median == 0 and len(r.weeks) == 4
        assert [w.monday for w in r.contributing] == [START, START + 7 * DAY]
        assert r.weeks[2].observed.supporting_workouts or r.metric == "moving_s"
        assert "partial" in r.weeks[2].reasons
        assert "enumerated_identities_not_retained" in r.weeks[3].reasons
    first = performance.running_references(START)
    assert "clipped_week" in first[0].weeks[-1].reasons and first[0].median is None
    consistency = performance.consistency
    assert consistency.confirmed_fraction == Fraction(1, 4)
    assert consistency.confirmed_or_inferred_fraction == Fraction(2, 4)
    assert len(consistency.eligible_weeks) == 4 and len(consistency.excluded) == 2
    assert "open_week" in consistency.excluded[-1][1]

    legacy = db.scalars(select(GarminCoverage).where(GarminCoverage.local_date == START)).one()
    legacy.receipts = {}
    db.commit()
    for r in report().running_references(START + 28 * DAY):
        assert r.median is None and len(r.contributing) == 1
        assert "empty_at_retrieval" in r.weeks[0].reasons
        assert r.reasons == ("fewer_than_two_eligible_weeks",)


def test_recovery_reference_windows_and_regimes(db: Session) -> None:
    src = account(db)
    period = Period(START, START + 32 * DAY, ZONE)
    hr = DailyMetric.RESTING_HR
    sleep = DailyMetric.SLEEP
    # Fourteen HR dates in [0,15), spanning fourteen days. Fourteen sleep dates span thirteen.
    for i in range(15):
        if i != 7:
            db.add(recovery(src, i, hr, 54 if i < 7 else 58))
        if i < 14:
            db.add(recovery(src, i, sleep, 24000))
    db.add_all(
        [
            recovery(src, 15, hr, 90),
            recovery(src, 16, hr, 110),
            recovery(src, 0, DailyMetric.WEEKLY_HRV, 42),
        ]
    )
    change = recovery(src, 17, hr, 60)
    change.mapping_version = "other-mapper"
    db.add_all([change, recovery(src, 18, hr, 57)])
    db.commit()
    weekly = aggregate_weeks(read(db, src, p=period), reference_date=period.stop)

    def regime(metric: DailyMetric) -> RecoveryRegime:
        return RecoveryRegime(
            weekly.daily_report.recovery_source,
            metric,
            START,
            period.stop,
            "same device and protocol",
            "synthetic review",
        )

    report = analyze_performance(weekly, recovery_regimes=(regime(hr), regime(sleep)))
    ref = report.recovery_reference(START + 15 * DAY, hr)
    assert (ref.n, ref.minimum, ref.median, ref.maximum) == (14, 54, 56, 58)
    assert ref.target.fact.value == 90 and ref.target.day not in ref.dates
    assert ref.window_start == START and ref.facts[-1].provider_date == START + 14 * DAY
    assert len(ref.excluded) == 1 and ref.excluded[0].cell.day == START + 7 * DAY
    assert ref.missing_dates == (START + 7 * DAY,) and ref.dates[-1] == START + 14 * DAY
    assert len({f.identity for f in ref.facts}) == 14
    short = report.recovery_reference(START + 14 * DAY, sleep)
    assert short.n == 14 and short.median is None and short.reasons == ("span_under_14_days",)
    assert report.recovery_reference(START + 14 * DAY, hr).n == 13
    assert report.recovery_reference(START + 17 * DAY, hr).n == 0
    assert report.recovery_reference(START + 19 * DAY, hr).n == 1
    later = report.recovery_reference(START + 31 * DAY, hr)
    assert later.window_start == START + 3 * DAY and len(later.facts) + len(later.excluded) == 28
    clipped_regime = replace(regime(hr), start=START + 8 * DAY)
    short = analyze_performance(weekly, recovery_regimes=(clipped_regime,)).recovery_reference(
        START + 15 * DAY, hr
    )
    assert short.n == 7 and short.maximum is None
    assert analyze_performance(weekly).recovery_reference(START + 15 * DAY, hr).median is None
    with pytest.raises(ValueError, match="sleep duration or resting HR"):
        report.recovery_reference(START + 15 * DAY, DailyMetric.WEEKLY_HRV)
    with pytest.raises(ValueError, match="invalid recovery regime"):
        analyze_performance(weekly, recovery_regimes=(replace(regime(hr), regime="unknown"),))
    with pytest.raises(ValueError, match="overlapping"):
        analyze_performance(weekly, recovery_regimes=(regime(hr), clipped_regime))
    with pytest.raises(ValueError, match="selected source"):
        analyze_performance(
            weekly,
            recovery_regimes=(
                replace(regime(hr), source=replace(regime(hr).source, owner_id=src.id)),
            ),
        )


def test_unrounded_estimate_ranking_and_set_eligibility(db: Session) -> None:
    src = account(db)
    hevy = account(db, src.user_id, "hevy")
    w = lift(
        db,
        hevy,
        0,
        "precision",
        [("squat", [("normal", 5, True)] * 4 + [("normal", 11, True), ("normal", 5, True)])],
    )
    first, second, timed, distance, high_reps, unloaded = w.exercises[0].sets
    # Force the lower UUID to lose on unrounded value despite identical display estimates.
    lower, higher = sorted((first, second), key=lambda s: s.id)
    lower.weight_kg = Decimal("60.0000")
    higher.weight_kg = Decimal("60.0001")
    timed.duration_seconds = 30
    distance.distance_m = 20
    unloaded.weight_kg = 0
    db.commit()
    weekly = aggregate_weeks(read(db, src, hevy), reference_date=PERIOD.stop)
    unreviewed = analyze_performance(weekly)
    assert sum(p.estimated_1rm_kg is not None for p in unreviewed.strength) == 2
    assert not unreviewed.successive_estimates
    reviewed = analyze_performance(
        weekly,
        strength_reviews={p.fact: Review(SQUAT, "synthetic protocol") for p in unreviewed.strength},
    )
    by_id = {p.fact.row.set_id: p for p in reviewed.strength}
    assert by_id[lower.id].estimated_1rm_kg == by_id[higher.id].estimated_1rm_kg == Decimal("70.00")
    assert by_id[higher.id].workout_best and not by_id[lower.id].workout_best
    assert all(by_id[s.id].estimated_1rm_kg is None for s in (timed, distance, high_reps, unloaded))
    assert all("timed_or_distance_task" in by_id[s.id].reasons for s in (timed, distance))

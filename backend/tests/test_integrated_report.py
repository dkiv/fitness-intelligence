"""Five synthetic weeks spanning Toronto's spring transition, read through the normal selectors."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.orm import Session
from test_longitudinal import NOW, START, ZONE, account, coverage, energy, intake, issue, weight
from test_training_exposure import lift, outing, recovery

from fitness_intelligence.adapters.hevy.analytics import HevyHistoryProfile
from fitness_intelligence.analytics.integrated import IntegratedReport, integrate, report_json
from fitness_intelligence.analytics.performance import (
    Review,
    RunningTask,
    StrengthTask,
    analyze_performance,
)
from fitness_intelligence.analytics.proximity import SessionTiming
from fitness_intelligence.analytics.references import RecoveryRegime
from fitness_intelligence.analytics.strength import DAY, Period
from fitness_intelligence.analytics.weekly import aggregate_weeks
from fitness_intelligence.db.longitudinal import query_longitudinal
from fitness_intelligence.db.models import SourceAccount, Workout
from fitness_intelligence.domain.endurance import DailyMetric

PERIOD = Period(START - 21 * DAY, START + 14 * DAY, ZONE)
FOCUS = PERIOD.stop - DAY


@dataclass
class Example:
    garmin: SourceAccount
    hevy: SourceAccount
    workouts: dict[str, UUID]
    foreign: tuple[UUID, ...]

    def report(self, db: Session, *, known_zone: bool = True) -> IntegratedReport:
        profile = HevyHistoryProfile(
            self.hevy.id, frozenset({"squat", "lunge"}), frozenset({"squat", "lunge"})
        )
        daily = query_longitudinal(
            db.get_bind(),
            owner_id=self.garmin.user_id,
            period=PERIOD,
            weight_account_id=self.garmin.id,
            endurance_account_id=self.garmin.id,
            expenditure_account_id=self.garmin.id,
            recovery_account_id=self.garmin.id,
            hevy_profile=profile,
            source_zones={self.garmin.id: ZONE} if known_zone else {},
        )
        weekly = aggregate_weeks(daily, reference_date=PERIOD.stop)
        reviews = {
            f: Review(
                StrengthTask("squat", "high bar", "barbell", "external_kg", "primary", "paused"),
                "synthetic protocol",
            )
            for w in weekly.weeks
            for f in w.strength.facts
            if f.series and f.series.template_id == "squat" and f.execution == "confirmed"
        }
        runs = {
            f: Review(
                RunningTask(
                    5000, "park loop", "elapsed_s", "recorded RPE 6", "dry", "uninterrupted"
                ),
                "synthetic log",
            )
            for w in weekly.weeks
            for day in w.endurance.days
            for f in day.facts
            if f.workout_id in (self.workouts["early_run"], self.workouts["monday_run"])
        }
        source = daily.recovery_source
        change = START + 7 * DAY
        regimes = (
            RecoveryRegime(
                source, DailyMetric.SLEEP, PERIOD.start, PERIOD.stop, "device A", "sleep review"
            ),
            RecoveryRegime(
                source, DailyMetric.RESTING_HR, PERIOD.start, change, "device A", "first review"
            ),
            RecoveryRegime(
                source, DailyMetric.RESTING_HR, change, PERIOD.stop, "device B", "second review"
            ),
        )
        return integrate(
            analyze_performance(
                weekly, strength_reviews=reviews, running_reviews=runs, recovery_regimes=regimes
            )
        )


@pytest.fixture
def example(db: Session) -> Example:
    garmin = account(db)
    hevy = account(db, garmin.user_id, "hevy")
    ids = {}

    def strength(
        label: str,
        n: int,
        hour: int,
        minute: int,
        length: int | None,
        exercises: list[tuple[str, list[tuple[str, int, bool]]]],
    ) -> None:
        w = lift(db, hevy, n, label, exercises, ended=length is not None)
        start = datetime.combine(START + n * DAY, time(hour, minute), UTC)
        w.started_at = start
        w.ended_at = start + timedelta(minutes=length) if length is not None else None
        for ex in w.exercises:
            for st in ex.sets:
                if st.completed_at is not None:
                    st.completed_at = start + timedelta(minutes=2)
        ids[label] = w.id

    strength("early_lift", -6, 16, 0, 30, [("squat", [("normal", 7, False)])])
    strength("sunday_lift", 6, 16, 0, 60, [("squat", [("normal", 5, True)])])
    strength(
        "monday_lift",
        7,
        15,
        45,
        35,
        [
            ("squat", [("normal", 6, True), ("drop", 5, False)]),
            ("lunge", [("normal", 4, True)]),
            ("unclassified", [("normal", 20, True)]),
        ],
    )
    strength("open_lift", 10, 14, 0, None, [("squat", [("normal", 6, True)])])
    strength("unclassified_lift", 12, 16, 0, 45, [("other", [("normal", 10, True)])])
    activities = [
        ("early_run", -5, 16, 0, 5000, 1600, 1500, 1700, None),
        ("saturday_run", 5, 17, 0, 3000, 1050, None, 1100, None),
        ("monday_run", 7, 16, 0, 5000, 1610, 1450, 1640, 30),
        ("calendar_disagreement", 9, 2, 0, 2000, 600, 570, 620, None),
        ("thursday_run", 10, 15, 0, 2000, 620, None, 650, None),
        ("held_run", 11, 16, 0, 9000, 3000, None, 3200, None),
    ]
    for i, (label, n, h, m, dist, act, moving, elapsed, length) in enumerate(activities):
        a = outing(db, garmin, n, str(101 + i), "running", "running", dist, act, moving, elapsed)
        w = db.get(Workout, a.workout_id)
        w.started_at = datetime.combine(START + n * DAY, time(h, m), UTC)
        w.ended_at = w.started_at + timedelta(minutes=length) if length is not None else None
        ids[label] = w.id
    ids["squash"] = outing(
        db, garmin, 12, "107", "squash", "squash", None, 900, None, None
    ).workout_id
    for n in range(-21, 14):
        has_activity = n in (-5, 5, 7, 9, 10, 11, 12)
        c = coverage(
            garmin,
            n,
            "activities",
            "partial" if n in (-5, 7) else "observed" if has_activity else "empty",
            None if n in (-5, 7) else int(has_activity),
        )
        if not has_activity:
            c.receipts = {"empty_activity_scan": {"started_at": (NOW + 20 * DAY).isoformat()}}
            c.attempted_at = c.last_success = NOW + 21 * DAY
        db.add(c)
    hold = issue(garmin, 11, "activities", "contradictory_revision")
    hold.subject = "106"
    instr = issue(garmin, 7, "running_steps", "incomplete_steps")
    instr.subject = "103"
    db.add_all(
        [
            hold,
            instr,
            intake(garmin, 7, 2100),
            intake(garmin, 9, 0, presence=True),
            energy(garmin, 7, DailyMetric.TOTAL_ENERGY, 2300),
            energy(garmin, 7, DailyMetric.ACTIVE_ENERGY, 500),
            recovery(garmin, 7, DailyMetric.OVERNIGHT_HRV, 45),
            recovery(garmin, 8, DailyMetric.WEEKLY_HRV, 47),
            issue(garmin, 10, "sleep", "disputed_sleep"),
            issue(garmin, 8, "weight", "possible_retime"),
        ]
    )
    for n in range(-15, 14):
        if n != 9:
            db.add(recovery(garmin, n, DailyMetric.SLEEP, 24000))
        db.add(recovery(garmin, n, DailyMetric.RESTING_HR, 55 if n < 7 else 59))
    for n in (0, 3, 6, 7, 8, 10, 13):
        db.add(weight(garmin, n, "70000" if n < 7 else "71000"))
    others = []
    for g in (account(db), account(db, garmin.user_id)):
        others.append(
            outing(db, g, 7, "103", "running", "running", 9999, 999, None, None).workout_id
        )
        db.add(issue(g, 7, "activities", "other_source"))
    for h in (account(db, garmin.user_id, "hevy"), account(db, provider="hevy")):
        others.append(lift(db, h, 7, "monday_lift", [("squat", [("normal", 99, True)])]).id)
    db.commit()
    return Example(garmin, hevy, ids, tuple(others))


def test_cross_domain_evidence_and_timing(db: Session, example: Example) -> None:
    report = example.report(db)
    ids = example.workouts
    pairs = {(p.strength_workout_id, p.running_workout_id): p for p in report.proximity.pairs}
    assert len(pairs) == len(report.proximity.pairs) == 5
    mixed = pairs[ids["monday_lift"], ids["monday_run"]]
    assert (
        len(mixed.exercise_ids),
        len(mixed.confirmed_sets),
        len(mixed.inferred_sets),
        mixed.recorded_reps,
    ) == (2, 2, 1, 15)
    assert mixed.timing.order == "strength_first" and mixed.timing.relation == "overlap"
    assert (mixed.timing.start_to_start_s, mixed.timing.end_to_start_s) == (900, -1200)
    cross = pairs[ids["sunday_lift"], ids["monday_run"]]
    assert cross.run_minus_strength_days == 1 and cross.timing.end_to_start_s == 23 * 3600
    dst = pairs[ids["sunday_lift"], ids["saturday_run"]]
    assert dst.run_minus_strength_days == -1 and dst.timing.order == "run_first"
    assert dst.timing.start_to_start_s == 23 * 3600 and dst.timing.end_to_start_s is None
    unknown = pairs[ids["open_lift"], ids["thursday_run"]]
    assert (
        unknown.timing.relation == "earlier_end_unknown" and unknown.timing.start_to_start_s == 3600
    )
    assert pairs[ids["early_lift"], ids["early_run"]].evidence == "tentative_inferred"
    held = {r.running_workout_id: r.reasons for r in report.proximity.excluded_runs}
    assert held == {
        ids["calendar_disagreement"]: ("provider_report_date_disagreement",),
        ids["held_run"]: ("activity_reconciliation_hold",),
    }
    assert not any(ids["unclassified_lift"] in k for k in pairs)
    detail = report.inspect_pair(ids["monday_lift"], ids["monday_run"])
    assert (
        detail["running"]["acquisition"].status == "partial"
        and detail["running"]["instructions"].issues
    )
    assert (
        detail["running"]["fact"].ended_at.hour == 16
        and detail["running"]["review"].task.effort == "recorded RPE 6"
    )
    assert len(detail["lower_body_working_sets"]) == 3 and detail["tolerance"] is None
    assert {p.fact.row.set_id for p in detail["lower_body_working_sets"]} == set(
        mixed.confirmed_sets + mixed.inferred_sets
    )
    for excluded in example.foreign:
        with pytest.raises(KeyError):
            report.inspect_workout(excluded)
        assert str(excluded) not in report.to_json()
    assert report.inspect_workout(ids["held_run"])["fact"].distance_m == 9000
    assert not report.inspect_workout(ids["calendar_disagreement"])["calendar_aligned"]
    assert report.inspect_workout(ids["monday_run"])["calendar_aligned"]
    unknown_zone = example.report(db, known_zone=False)
    assert not unknown_zone.proximity.pairs and len(unknown_zone.proximity.excluded_runs) == 6


def test_five_week_summary_and_inspection(db: Session, example: Example) -> None:
    report = example.report(db)
    view = json.loads(report.to_json())
    assert report.to_json() == example.report(db).to_json(FOCUS)
    assert len(view["weeks"]) == 5 and view["closed"] and view["fully_requested"]
    assert (
        view["strength"]["confirmed_working_sets"] == 5
        and view["strength"]["inferred_working_sets"] == 1
    )
    assert any(
        c["reps_at_fixed_load"]["value"] == 1 for c in view["strength"]["comparisons"]["fixed_load"]
    )
    running = view["endurance"]
    assert Decimal(running["comparisons"][0]["seconds"]["value"]) == -60
    assert running["comparison_exclusions"]["no_task_review"] >= 1
    sports = {s["sport"]: s for s in running["sports"]}
    assert (
        sports["running"]["sessions"]["value"] == 3 and sports["squash"]["sessions"]["value"] == 1
    )
    for field, expected, measured in (
        ("distance_m", 9000, 3),
        ("activity_s", 2830, 3),
        ("moving_s", 2020, 2),
        ("elapsed_s", 2910, 3),
    ):
        cell = sports["running"][field]
        assert Decimal(cell["value"]) == expected and cell["measured_workouts"] == measured
        assert cell["status"] == "lower_bound"
    ref = next(r for r in running["references"] if r["metric"] == "sessions")
    assert ref["sampled_week_median"] == "0" and len(ref["contributing_weeks"]) == 2
    assert [w["observed"]["value"] for w in ref["weeks"] if w["exclusions"]] == [1, 1]
    assert ref["habitual_exposure"] == "insufficient_evidence"
    assert (
        "Habitual exposure unknown" in report.render()
        and "Excluded weeks, observed sessions" in report.render()
    )
    assert view["intake"]["date_statuses"] == {"explicit_zero": 1, "reported": 1, "missing": 5}
    assert Decimal(view["intake"]["mean_kcal"]) == 1050
    assert view["expenditure"]["basal"]["subtotal_kcal"] is None
    assert Decimal(view["weight"]["changes"][0]["change_kg"]) == 1
    refs = {r["metric"]: r for r in view["recovery"]["references"]}
    assert refs[DailyMetric.RESTING_HR]["n"] == 6 and refs[DailyMetric.RESTING_HR]["median"] is None
    assert (
        refs[DailyMetric.SLEEP]["n"] == 26 and Decimal(refs[DailyMetric.SLEEP]["median"]) == 24000
    )
    day = json.loads(report_json(report.inspect_day(START + 9 * DAY)))
    assert Decimal(day["intake"]["metric"]["value"]) == 0
    assert (
        next(c for c in day["recovery"]["cells"] if c["metric"] == DailyMetric.SLEEP)["status"]
        == "missing"
    )
    assert report.inspect_day(START + 8 * DAY).weight.excluded
    assert len(view["recovery"]["hrv"][0]["source_only_dates"]) == 1
    with pytest.raises(KeyError):
        report.inspect_day(PERIOD.stop)


def test_reference_evidence_and_optional_domains(db: Session, example: Example) -> None:
    report = example.report(db)
    sleep = report.inspect_recovery_reference(FOCUS, DailyMetric.SLEEP)
    assert sleep["n"] == len(sleep["contributing"]) == 26
    assert len(sleep["excluded"]) == 2 and sleep["target"].day == FOCUS
    running = report.inspect_running_reference(START + 7 * DAY, "sessions")
    assert len(running["candidate_weeks"]) == 4
    assert len(json.loads(report_json(sleep))["contributing"]) == 26
    receipt = json.loads(report_json(running))["candidate_weeks"][0]["native_dates"][0]
    assert receipt["activity_coverage"]["status"] == "empty"
    assert receipt["scan_started_at"] and receipt["provider_zone"] == ZONE.key
    assert all(len(w["native_dates"]) == 7 for w in running["candidate_weeks"])
    assert [w["observed"].value for w in running["candidate_weeks"]] == [0, 0, 1, 1]
    consistency = report.summary()["strength"]["consistency"]
    assert (
        consistency["confirmed_weeks"],
        consistency["confirmed_or_inferred_weeks"],
        consistency["eligible_weeks"],
    ) == (2, 3, 5)
    daily = query_longitudinal(
        db.get_bind(),
        owner_id=example.garmin.user_id,
        period=PERIOD,
        weight_account_id=example.garmin.id,
    )
    view = integrate(analyze_performance(aggregate_weeks(daily, reference_date=PERIOD.stop)))
    summary = json.loads(view.to_json())
    assert all(summary[k] is None for k in ("strength", "endurance", "expenditure", "recovery"))
    assert summary["proximity"] == {"pairs": [], "excluded_runs": [], "selected": False}
    assert "Reported intake" in view.render()


def test_incomplete_and_simultaneous_spans(db: Session, example: Example) -> None:
    ids = example.workouts
    run = db.get(Workout, ids["monday_run"])
    lift = db.get(Workout, ids["monday_lift"])

    def timing() -> SessionTiming:
        return example.report(db).inspect_pair(lift.id, run.id)["pair"].timing

    run.ended_at = None
    db.commit()
    assert timing().relation == "starts_during_earlier"
    run.started_at = lift.started_at
    db.commit()
    same = timing()
    assert (same.order, same.start_to_start_s, same.end_to_start_s, same.relation) == (
        "same_start",
        0,
        None,
        "same_start",
    )
    run.ended_at = run.started_at + timedelta(minutes=10)
    db.commit()
    assert timing().relation == "overlap"

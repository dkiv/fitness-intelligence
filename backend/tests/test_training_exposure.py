"""Synthetic source-scoped weekly report across the spring clock change."""

from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
import test_adaptive_cycle as adaptive
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_longitudinal import (
    NOW,
    PERIOD,
    START,
    ZONE,
    account,
    coverage,
    energy,
    intake,
    issue,
    weight,
)

from fitness_intelligence.adapters.hevy.analytics import HevyHistoryProfile
from fitness_intelligence.analytics.longitudinal import LongitudinalReport
from fitness_intelligence.analytics.strength import DAY, Period, StrengthFact
from fitness_intelligence.analytics.weekly import Week, aggregate_weeks
from fitness_intelligence.db import longitudinal
from fitness_intelligence.db.endurance_models import (
    ActivitySplit,
    ActivityStep,
    DailyRecoveryObservation,
    EnduranceActivity,
)
from fitness_intelligence.db.models import (
    ExerciseSet,
    ExternalReference,
    SourceAccount,
    Workout,
    WorkoutExercise,
)
from fitness_intelligence.db.plan_models import (
    PlanDecision,
    PlanRevision,
    SessionOutcome,
    TrainingPlan,
)
from fitness_intelligence.domain.endurance import DailyMetric, PaceState
from fitness_intelligence.planning.outcomes import Actual
from fitness_intelligence.planning.planner import Slot

approved_cycle = adaptive.cycle


def ref(
    db: Session, src: SourceAccount, w: Workout, external: str, metadata: dict, payload: dict
) -> ExternalReference:
    row = ExternalReference(
        user_id=src.user_id,
        source_account_id=src.id,
        provider=src.provider,
        entity_type="workout",
        workout_id=w.id,
        external_id=external,
        raw_payload=payload,
        last_synced_at=NOW,
        source_updated_at=NOW - DAY,
        sync_metadata=metadata,
    )
    db.add(row)
    db.flush()
    return row


def lift(
    db: Session,
    src: SourceAccount,
    n: int,
    external: str,
    exercises: list[tuple[str, list[tuple[str | None, int, bool]]]],
    *,
    ended: bool = True,
) -> Workout:
    when = datetime.combine(START + n * DAY, time(16), UTC)
    w = Workout(
        title="Synthetic session",
        user_id=src.user_id,
        started_at=when,
        ended_at=when if ended else None,
    )
    db.add(w)
    for pos, (template, sets) in enumerate(exercises):
        exercise = WorkoutExercise(user_id=src.user_id, position=pos, name="same display name")
        w.exercises.append(exercise)
        for ordinal, (kind, reps, confirmed) in enumerate(sets):
            exercise.sets.append(
                ExerciseSet(
                    user_id=src.user_id,
                    position=ordinal,
                    kind=kind,
                    repetitions=reps,
                    weight_kg=60,
                    rpe=7 if confirmed else None,
                    completed_at=when if confirmed else None,
                )
            )
    db.flush()
    ref(
        db,
        src,
        w,
        external,
        {
            "adapter": "hevy-importer-v1",
            "hash_contract": "hevy-semantic-v2",
            "content_hash": "synthetic",
        },
        {
            "id": external,
            "exercises": [
                {"index": p, "exercise_template_id": t} for p, (t, _) in enumerate(exercises)
            ],
        },
    )
    return w


def outing(
    db: Session,
    src: SourceAccount,
    n: int,
    external: str,
    sport: str,
    subtype: str | None,
    distance: int | None,
    activity: int | None,
    moving: int | None,
    elapsed: int | None,
) -> EnduranceActivity:
    day = START + n * DAY
    when = datetime.combine(day, time(2 if n == 0 else 15), UTC)
    w = Workout(title="Synthetic session", user_id=src.user_id, started_at=when)
    db.add(w)
    db.flush()
    fields = {
        "distance_m": {
            "source": "Synthetic.distance",
            "retrieved_at": NOW.isoformat(),
            "source_updated_at": (NOW - DAY).isoformat(),
        }
    }
    link = ref(db, src, w, external, {"mapping_version": "synthetic-v1", "fields": fields}, {})
    row = EnduranceActivity(
        user_id=src.user_id,
        workout_id=w.id,
        reference_id=link.id,
        local_date=day,
        sport=sport,
        subtype=subtype,
        distance_m=distance,
        duration_s=activity,
        moving_s=moving,
        elapsed_s=elapsed,
        average_speed_mps=4 if distance else None,
    )
    db.add(row)
    db.flush()
    return row


def recovery(
    src: SourceAccount, n: int, metric: DailyMetric, value: int
) -> DailyRecoveryObservation:
    hrv = metric in (DailyMetric.OVERNIGHT_HRV, DailyMetric.WEEKLY_HRV)
    day = START + n * DAY
    overnight = datetime.combine(day, time(6), UTC)
    return DailyRecoveryObservation(
        user_id=src.user_id,
        provider=src.provider,
        source_account_id=src.id,
        local_date=day,
        metric=metric,
        value=value,
        unit="source_unit_unverified"
        if hrv
        else "bpm"
        if metric == DailyMetric.RESTING_HR
        else "s",
        method="reported_average" if hrv else "reported",
        source_field=f"Synthetic.{metric}",
        mapping_version="v1",
        retrieved_at=NOW,
        window_start=overnight - DAY if metric == DailyMetric.SLEEP else None,
        window_end=overnight if metric == DailyMetric.SLEEP else None,
    )


def read(
    db: Session,
    src: SourceAccount,
    hevy: SourceAccount | None = None,
    p: Period = PERIOD,
    *,
    provider_zone: ZoneInfo | None = ZONE,
) -> LongitudinalReport:
    return longitudinal.query_longitudinal(
        db.get_bind(),
        owner_id=src.user_id,
        period=p,
        weight_account_id=src.id,
        hevy_profile=HevyHistoryProfile(hevy.id, frozenset({"squat"}), frozenset({"squat"}))
        if hevy
        else None,
        endurance_account_id=src.id,
        recovery_account_id=src.id,
        expenditure_account_id=src.id,
        source_zones={src.id: provider_zone} if provider_zone else {},
    )


def test_unified_week(db: Session) -> None:
    src = account(db)
    hevy = account(db, src.user_id, "hevy")
    lift(
        db,
        hevy,
        0,
        "mixed",
        [
            ("squat", [("normal", 5, True), ("drop", 6, False)]),
            ("assistance", [("warmup", 8, False), (None, 2, False)]),
        ],
    )
    lift(db, hevy, 0, "extra", [("squat", [("normal", 7, False)])])
    lift(db, hevy, 3, "pull", [("assistance", [("normal", 8, False)])])
    lift(db, hevy, 4, "open", [("assistance", [("normal", 5, False)])], ended=False)
    lift(db, hevy, 6, "empty", [])
    first = outing(db, src, 0, "101", "running", "running", 5000, 1800, 1700, 1900)
    later = outing(db, src, 1, "102", "running", "trail_running", 5000, 1600, None, 1700)
    outing(db, src, 1, "103", "running", "running", None, 600, None, None)
    outing(db, src, 2, "104", "squash", "squash", None, 900, None, None)
    outing(db, src, 5, "105", "other", "cycling", 12000, 2700, None, None)
    outing(db, src, 6, "106", "other", None, None, None, None, None)
    instr = issue(src, 0, "running_steps", "incomplete_steps")
    instr.subject = "101"
    db.add_all(
        [
            instr,
            ActivitySplit(
                user_id=src.user_id,
                workout_id=first.workout_id,
                position=0,
                kind="aggregate",
                count=4,
            ),
            ActivityStep(
                user_id=src.user_id,
                workout_id=first.workout_id,
                workout_index=0,
                step_index=0,
                target_zone=2,
            ),
            coverage(src, 0, "running_steps", "partial", None),
            coverage(src, 1, "running_steps", "empty", 0),
            intake(src, 0, 2100),
            intake(src, 2, 0, presence=True),
            energy(src, 0, DailyMetric.TOTAL_ENERGY, 2300),
            weight(src, 0, "70000"),
            recovery(src, 0, DailyMetric.SLEEP, 24000),
            recovery(src, 1, DailyMetric.SLEEP, 26400),
            recovery(src, 0, DailyMetric.LIGHT, 11000),
            recovery(src, 0, DailyMetric.REM, 4800),
            recovery(src, 0, DailyMetric.DEEP, 6000),
            recovery(src, 0, DailyMetric.AWAKE, 1300),
            recovery(src, 0, DailyMetric.OVERNIGHT_HRV, 45),
            recovery(src, 0, DailyMetric.WEEKLY_HRV, 46),
            recovery(src, 1, DailyMetric.WEEKLY_HRV, 47),
            issue(src, 3, "resting_hr", "disputed_day"),
            coverage(src, 0, "sleep", "observed", 5),
            coverage(src, 0, "hrv", "observed", 2),
        ]
    )
    for n, (status, count) in enumerate(
        [("partial", None), ("observed", 2), ("observed", 1), ("empty", 0), ("failed", None)]
    ):
        db.add(coverage(src, n, "activities", status, count))
    db.add(coverage(src, 6, "activities", "observed", 1))
    db.add_all(recovery(src, n, DailyMetric.RESTING_HR, v) for n, v in enumerate([54, 55, 59, 90]))
    db.commit()
    report = read(db, src, hevy)
    (week,) = aggregate_weeks(report, reference_date=PERIOD.stop).weeks
    assert aggregate_weeks(
        replace(report, days=tuple(reversed(report.days))), reference_date=PERIOD.stop
    ).weeks == (week,)
    assert week.fully_requested and week.closed
    s = week.strength
    assert len(s.workouts) == 5 and len(s.workout_dates) == 4
    assert (len(s.confirmed_workouts), len(s.inferred_only_workouts)) == (1, 2)
    assert s.confirmed_dates == (START,) and s.inferred_only_dates == (START + 3 * DAY,)
    assert (len(s.working.confirmed), len(s.working.inferred), s.working.repetitions) == (1, 3, 26)
    assert len(s.working.recorded_reps) == 4 and s.lower_body.repetitions == 18
    assert len(s.warmups) == len(s.unknown_kind) == len(s.unsupported_sets) == 1
    assert len(s.by_movement) == 2 and s.unclassified_exercises
    assert report.days[1].strength.workouts == () and s.acquisition == "daily_enumeration_unknown"
    inferred = next(
        f for f in s.facts if f.execution == "inferred" and f.series.template_id == "squat"
    )
    assert (
        inferred.row.completed_at is None
        and inferred.load_convention == "external_kg"
        and inferred.reference_id
    )
    mixed = sorted(
        (f for f in s.facts if f.external_id == "mixed"),
        key=lambda f: (f.row.exercise_position, f.row.set_position),
    )
    assert [(f.row.exercise_position, f.row.set_position) for f in mixed] == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]
    assert (
        mixed[0].execution == "confirmed" and mixed[0].row.rpe == 7 and mixed[0].row.weight_kg == 60
    )
    assert mixed[0].retrieved_at == NOW and mixed[-1].load_convention == "unclassified"
    assert first.workout_id != later.workout_id
    sports = {(v.sport, v.subtype): v for v in week.endurance.sports}
    run = sports["running", None]
    assert len(sports) == 4 and run.sessions.value == 3 and len(run.dates) == 2
    assert run.distance_m.value == 10000 and len(run.distance_m.supporting_workouts) == 2
    assert run.distance_m.eligible_count == 2 and len(run.distance_m.missing_workouts) == 1
    assert (run.duration_s.value, run.moving_s.value, run.elapsed_s.value) == (4000, 1700, 3600)
    assert (
        run.distance_m.status == "lower_bound"
        and run.longest_observed.workout_id == first.workout_id
    )
    assert "unknown_sport" in run.reasons and "enumerated_identities_not_retained" in run.reasons
    assert (
        sports["other", "cycling"].distance_m.value == 12000
        and sports["squash", None].duration_s.value == 900
    )
    mon = report.days[0].endurance.days[0]
    (fact,) = mon.facts
    assert (
        fact.report_date == START - DAY and not mon.calendar_aligned and fact.provider_date == START
    )
    assert (
        fact.pace == (PaceState.DERIVED, 250)
        and fact.split_summary_rows == fact.instruction_rows == 1
    )
    assert fact.split_positions == (0,) and fact.instruction_positions == ((0, 0),)
    assert (
        fact.fields[0].source_field == "Synthetic.distance"
        and fact.activity_issues == ()
        and fact.instruction_issues
    )
    assert report.days[1].endurance.days[0].instructions.status == "empty"
    assert report.days[1].endurance.sports[0].longest_observed.split_summary_rows is None
    thursday = report.days[3].endurance
    assert thursday.days[0].activities.last_success_count == 0
    assert thursday.sports[0].sessions.status == "empty_at_retrieval"
    assert thursday.sports[0].sessions.value is None
    assert report.days[4].endurance.sports[0].sessions.value is None
    assert report.days[5].endurance.days[0].activities.status == "never_queried"
    summaries = {v.metric: v for v in week.recovery.series}
    sleep = summaries[DailyMetric.SLEEP]
    assert (sleep.median, sleep.minimum, sleep.maximum, len(sleep.facts)) == (
        25200,
        24000,
        26400,
        2,
    )
    assert sleep.dates == (START, START + DAY) and sleep.sample_count == 2
    assert sleep.facts[0].window_start.date() < START and sleep.facts[0].provider_date == START
    resting = summaries[DailyMetric.RESTING_HR]
    assert (resting.median, resting.minimum, resting.maximum, len(resting.facts)) == (55, 54, 59, 3)
    assert summaries[DailyMetric.DEEP].median == 6000 and summaries[DailyMetric.REM].median == 4800
    hrv = [
        c
        for c in week.recovery.cells
        if c.metric in (DailyMetric.OVERNIGHT_HRV, DailyMetric.WEEKLY_HRV) and c.fact
    ]
    assert len(hrv) == 3 and all(
        c.status == "source_only" and c.fact.unit == "source_unit_unverified" for c in hrv
    )
    assert not {DailyMetric.WEEKLY_HRV, DailyMetric.OVERNIGHT_HRV} & summaries.keys()
    assert week.intake.calories.mean_per_eligible_date_kcal == 1050
    assert (
        week.expenditure.total.observed_subtotal_kcal == 2300
        and week.weight.series[0].median_kg == 70
    )
    clipped = read(db, src, hevy, Period(START + 5 * DAY, PERIOD.stop, ZONE))
    (short,) = aggregate_weeks(clipped, reference_date=PERIOD.stop - DAY).weeks
    assert (
        not short.fully_requested
        and not short.closed
        and short.strength.workout_dates == (START + 6 * DAY,)
    )


def test_retained_membership_and_scoped_issues(db: Session) -> None:
    src = account(db)
    kept = outing(db, src, 0, "101", "running", "running", 5000, None, None, None)
    held = outing(db, src, 1, "102", "running", "running", 9000, None, None, None)
    other = outing(db, src, 1, "103", "running", "running", 2000, None, None, None)
    tomb = outing(db, src, 2, "104", "running", "running", 10000, None, None, None)
    db.get(ExternalReference, tomb.reference_id).source_deleted_at = NOW
    i = issue(src, 1, "activities", "contradictory_revision")
    i.subject = "102"
    empty_refresh = coverage(src, 0, "activities", "empty", 0)
    empty_refresh.receipts = {"empty_activity_scan": {"started_at": (NOW - DAY).isoformat()}}
    db.add_all(
        [
            i,
            empty_refresh,
            coverage(src, 1, "activities", "observed", 1),
            coverage(src, 2, "activities", "empty", 0),
            coverage(src, 3, "activities", "failed", 4),
        ]
    )
    db.commit()
    days = read(db, src).days
    assert days[0].endurance.days[0].discrepancies == ("retained_after_empty",)
    assert days[0].endurance.days[0].full_day_empty_exclusion(PERIOD.stop) is not None
    (run,) = days[0].endurance.sports
    assert run.distance_m.status == "observed_only" and run.sessions.supporting_workouts == (
        kept.workout_id,
    )
    assert "enumerated_count_mismatch" in days[1].endurance.sports[0].reasons
    assert days[1].endurance.sports[0].sessions.supporting_workouts == (other.workout_id,)
    assert next(
        f for f in days[1].endurance.days[0].facts if f.workout_id == held.workout_id
    ).activity_issues
    assert days[2].endurance.days[0].facts == ()
    assert days[2].endurance.sports[0].distance_m.status == "empty_at_retrieval"
    assert days[2].endurance.sports[0].distance_m.value is None
    assert (
        days[3].endurance.days[0].activities.last_success_count == 4
        and days[3].endurance.sports[0].sessions.value is None
    )


def test_account_isolation_and_atomic_training_read(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = account(db)
    peer = account(db, src.user_id)
    foreign = account(db)
    hevy = account(db, src.user_id, "hevy")
    own = outing(db, src, 0, "1", "running", "running", 3000, None, None, None)
    sleep = recovery(src, 0, DailyMetric.SLEEP, 24000)
    lift(db, hevy, 0, "lift", [("squat", [("normal", 5, False)])])
    for other in (peer, foreign):
        outing(db, other, 0, "1", "running", "running", 9000, None, None, None)
        db.add(recovery(other, 0, DailyMetric.SLEEP, 32000))
        db.add(issue(other, 0, "activities", "unrelated"))
    db.add(sleep)
    db.commit()
    for key, bad in (
        ("hevy_profile", HevyHistoryProfile(src.id)),
        ("endurance_account_id", hevy.id),
        ("recovery_account_id", foreign.id),
    ):
        with pytest.raises(ValueError, match="invalid source account"):
            longitudinal.query_longitudinal(
                db.get_bind(),
                owner_id=src.user_id,
                period=PERIOD,
                weight_account_id=src.id,
                **{key: bad},
            )
    # Commit a repair after the reader establishes its snapshot but before it reads activity rows.
    original = longitudinal.read_hevy_facts

    def repair(
        session: Session, *, owner_id: UUID, period: Period, profile: HevyHistoryProfile
    ) -> tuple[StrengthFact, ...]:
        assert (
            session.connection().exec_driver_sql("SHOW transaction_read_only").scalar_one() == "on"
        )
        own.distance_m = 4500
        sleep.value = 26000
        db.scalar(
            select(ExternalReference).where(ExternalReference.source_account_id == hevy.id)
        ).source_deleted_at = NOW
        db.add(coverage(src, 0, "activities", "partial", None))
        db.commit()
        return original(session, owner_id=owner_id, period=period, profile=profile)

    with monkeypatch.context() as patch:
        patch.setattr(longitudinal, "read_hevy_facts", repair)
        before = read(db, src, hevy).days[0]
    after = read(db, src, hevy).days[0]
    assert before.strength.workouts and not after.strength.workouts
    assert (
        before.endurance.sports[0].distance_m.value,
        after.endurance.sports[0].distance_m.value,
    ) == (3000, 4500)
    assert (before.recovery.series[0].median, after.recovery.series[0].median) == (24000, 26000)
    assert (
        before.endurance.days[0].activities.status == "never_queried"
        and after.endurance.days[0].activities.status == "partial"
    )


def test_training_read_preserves_records_and_breaks_equal_start_tie(
    db: Session, approved_cycle: adaptive.Cycle
) -> None:
    src = account(db, approved_cycle.owner)
    hevy = account(db, src.user_id, "hevy")
    approved_cycle.record(Slot.SHORT_RUN, 5, Actual(status="completed", run_seconds=1200))
    lift(db, hevy, 0, "lift", [("squat", [("normal", 5, True)])])
    runs = [
        outing(db, src, 1, key, "running", "running", 5000, None, None, None)
        for key in ("11", "12")
    ]
    db.add(recovery(src, 0, DailyMetric.SLEEP, 24000))
    db.commit()

    def fingerprint() -> tuple:
        tables = (
            Workout,
            WorkoutExercise,
            ExerciseSet,
            ExternalReference,
            EnduranceActivity,
            DailyRecoveryObservation,
            TrainingPlan,
            PlanRevision,
            PlanDecision,
            SessionOutcome,
        )
        return tuple(
            tuple(db.execute(select(m.__table__).order_by(*m.__table__.primary_key)))
            for m in tables
        )

    before = fingerprint()
    week = aggregate_weeks(read(db, src, hevy), reference_date=PERIOD.stop).weeks[0]
    assert week.endurance.sports[0].longest_observed.workout_id == min(r.workout_id for r in runs)
    assert fingerprint() == before


def test_empty_coverage_and_separate_recovery_series(db: Session) -> None:
    src = account(db)
    one = outing(db, src, 0, "101", "running", "trail_running", 0, None, None, None)
    link = db.get(ExternalReference, one.reference_id)
    link.sync_metadata = {"fields": {"steps": {"retrieved_at": NOW.isoformat()}}}
    baseline = recovery(src, 0, DailyMetric.SLEEP, 20000)
    revised = recovery(src, 1, DailyMetric.SLEEP, 26000)
    revised.mapping_version = "v2"
    legacy = recovery(src, 2, DailyMetric.SLEEP, 28000)
    legacy.source_field = None
    disputed = issue(src, 0, "sleep", "field_conflict")
    disputed.subject = DailyMetric.DEEP
    db.add_all((baseline, revised, legacy, disputed, recovery(src, 0, DailyMetric.DEEP, 5000)))
    db.commit()
    report = read(db, src)
    first = report.days[0].endurance.sports[0].longest_observed
    assert first.pace == (PaceState.NOT_APPLICABLE, None)
    assert first.instruction_positions == () and first.split_positions is None
    week = aggregate_weeks(report, reference_date=PERIOD.stop).weeks[0]
    assert [(s.metric, s.median, s.sample_count) for s in week.recovery.series] == [
        (DailyMetric.SLEEP, 20000, 1),
        (DailyMetric.SLEEP, 26000, 1),
    ]
    reasons = {c.metric: c.reasons for c in report.days[0].recovery.cells}
    assert reasons[DailyMetric.DEEP] == ("field_conflict",) and reasons[DailyMetric.SLEEP] == ()
    assert (
        next(c for c in report.days[2].recovery.cells if c.metric == DailyMetric.SLEEP).status
        == "source_only"
    )


@pytest.mark.parametrize(
    ("day", "midnight_utc"),
    [
        (date(2025, 3, 9), datetime(2025, 3, 10, 4, tzinfo=UTC)),
        (date(2025, 11, 2), datetime(2025, 11, 3, 5, tzinfo=UTC)),
    ],
)
def test_empty_scan_and_provider_day_closure(
    db: Session, day: date, midnight_utc: datetime
) -> None:
    src = account(db)
    # The report zone differs from the verified Toronto provider calendar.
    period = Period(day, day + DAY, ZoneInfo("UTC"))
    ledger = coverage(src, (day - START).days, "activities", "empty", 0)
    before = midnight_utc - timedelta(seconds=10)
    ledger.receipts = {"empty_activity_scan": {"started_at": before.isoformat()}}
    ledger.attempted_at = ledger.last_success = before + timedelta(seconds=5)
    db.add(ledger)
    db.commit()

    def week(report: LongitudinalReport, cutoff: date) -> Week:
        return aggregate_weeks(report, reference_date=cutoff).weeks[0]

    original = read(db, src, p=period)
    native = original.days[0].endurance.days[0]
    assert native.verified_empty and not native.calendar_aligned
    assert native.activities.last_success_count == 0 and native.activities.retained_count == 0
    open_week = week(original, day)
    closed_week = week(original, day + DAY)
    assert not open_week.closed and closed_week.closed
    assert "source_date_open_at_reference" in open_week.endurance.sports[0].reasons
    assert "scan_started_before_source_date_closed" in closed_week.endurance.sports[0].reasons
    for summary in (original.days[0].endurance, open_week.endurance, closed_week.endurance):
        run = summary.sports[0]
        assert all(
            v.value is None and v.status == "empty_at_retrieval"
            for v in (run.sessions, run.distance_m, run.duration_s, run.moving_s, run.elapsed_s)
        )

    # Even a fresh success timestamp after midnight can belong to a crossing scan.
    ledger.attempted_at = ledger.last_success = midnight_utc + timedelta(seconds=5)
    db.commit()
    crossing = week(read(db, src, p=period), day + DAY).endurance.sports[0]
    assert (
        crossing.sessions.value is None
        and "scan_started_before_source_date_closed" in crossing.reasons
    )

    # Both listings of the next acquisition take place on the closed side of the boundary.
    after = midnight_utc + timedelta(seconds=10)
    ledger.receipts = {"empty_activity_scan": {"started_at": after.isoformat()}}
    ledger.attempted_at = ledger.last_success = after + timedelta(seconds=5)
    db.commit()
    refreshed = read(db, src, p=period)
    for summary in (refreshed.days[0].endurance, week(refreshed, day + DAY).endurance):
        run = summary.sports[0]
        assert all(
            v.value == 0 and v.status == "complete_empty"
            for v in (run.sessions, run.distance_m, run.duration_s, run.moving_s, run.elapsed_s)
        )
    native = refreshed.days[0].endurance.days[0]
    assert replace(native, scan_started_at=midnight_utc).full_day_empty_exclusion(day + DAY) is None
    unknown_policy = replace(native, activities=replace(native.activities, policy="unreviewed"))
    assert unknown_policy.full_day_empty_exclusion(day + DAY) == "unverified_scan_timing"
    assert week(refreshed, day).endurance.sports[0].sessions.value is None
    unknown = week(read(db, src, p=period, provider_zone=None), day + DAY).endurance.sports[0]
    assert unknown.sessions.value is None and "unknown_provider_calendar" in unknown.reasons


def test_weekly_zero_requires_every_empty_scan_to_cover_its_closed_date(db: Session) -> None:
    src = account(db)
    rows = [coverage(src, n, "activities", "empty", 0) for n in range(7)]
    for row in rows:
        row.receipts = {"empty_activity_scan": {"started_at": (NOW - DAY).isoformat()}}
    # Legacy history-v1 stores only the time that success was recorded.
    rows[-1].receipts = {}
    db.add_all(rows)
    db.commit()
    report = read(db, src)
    week = aggregate_weeks(report, reference_date=PERIOD.stop).weeks[0]
    assert week.fully_requested and week.closed
    statuses = [d.endurance.sports[0].sessions.status for d in report.days]
    assert statuses == ["complete_empty"] * 6 + ["empty_at_retrieval"]
    run = week.endurance.sports[0]
    assert run.reasons == ("unverified_scan_timing",)
    assert all(
        v.value is None and v.status == "empty_at_retrieval"
        for v in (run.sessions, run.distance_m, run.duration_s, run.moving_s, run.elapsed_s)
    )

    rows[-1].receipts = {"empty_activity_scan": {"started_at": (NOW - DAY).isoformat()}}
    db.commit()
    complete = aggregate_weeks(read(db, src), reference_date=PERIOD.stop).weeks[0]
    assert complete.endurance.sports[0].distance_m.value == 0
    assert complete.endurance.sports[0].distance_m.status == "complete_empty"

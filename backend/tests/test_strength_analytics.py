from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.orm import Session

from fitness_intelligence.analytics.strength import (
    ExerciseSeries,
    Observation,
    Period,
    analyze_strength,
)
from fitness_intelligence.db.models import (
    ExerciseSet,
    ExternalReference,
    SourceAccount,
    User,
    Workout,
    WorkoutExercise,
)
from fitness_intelligence.db.strength_analytics import query_strength, strength_observations

START = datetime(2024, 12, 30, 12, tzinfo=UTC)
PERIOD = Period(date(2024, 12, 30), date(2025, 1, 20))
MOVEMENT = UUID(int=2)
SERIES = {MOVEMENT: ExerciseSeries("press", external_load=True)}
BASE = Observation(
    UUID(int=1),
    START,
    START,
    MOVEMENT,
    "Press",
    UUID(int=3),
    "normal",
    6,
    Decimal("50.1234"),
    Decimal("8"),
    completed_at=START,
)


def test_progression_and_volume_across_workouts() -> None:
    rows = [
        BASE,
        replace(BASE, set_id=UUID(int=4), kind="drop", repetitions=5),
        replace(BASE, set_id=UUID(int=5), kind="warmup", weight_kg=Decimal(100)),
        replace(BASE, set_id=UUID(int=6), kind="failure", repetitions=10, rpe=None),
        replace(BASE, set_id=UUID(int=7), kind=None),
        replace(
            BASE,
            workout_id=UUID(int=8),
            set_id=UUID(int=9),
            exercise_id=UUID(int=10),
            started_at=datetime(2025, 1, 13, 12, tzinfo=UTC),
            weight_kg=Decimal(55),
        ),
    ]
    series = {**SERIES, UUID(int=10): SERIES[MOVEMENT]}
    report = analyze_strength(reversed(rows), PERIOD, series=series)
    assert report.weekly_activity.rows() == [
        (PERIOD.start, 1, 1, 5, 0, None),
        (date(2025, 1, 6), 0, 0, 0, 0, -1),
        (date(2025, 1, 13), 1, 1, 1, 0, 1),
    ]
    assert report.progression["estimated_1rm_kg"].to_list() == [Decimal("66.83"), Decimal("66")]
    assert report.progression["completion_inferred"].to_list() == [False, False]
    working = report.weekly_volume.row(2, named=True)
    assert working["category"] == "working" and working["completed_sets"] == 3
    assert working["volume_load_kg"] == Decimal("1052.5914")
    assert working["repetitions"] == 21
    assert report.weekly_volume["category"].to_list() == ["unknown", "warmup", "working", "working"]
    effort = analyze_strength(
        rows, PERIOD, series=series, top_only=False, rpe_range=(Decimal(8), Decimal(8))
    )
    assert effort.progression["kind"].to_list() == ["normal", "drop", "normal"]
    assert effort.weekly_volume.equals(report.weekly_volume)


@pytest.mark.parametrize(
    "changes",
    [
        {"repetitions": None},
        {"repetitions": 0},
        {"repetitions": -1},
        {"repetitions": 11},
        {"weight_kg": None},
        {"weight_kg": Decimal(0)},
        {"weight_kg": Decimal(-1)},
        {"weight_kg": Decimal("NaN")},
        {"duration_seconds": Decimal(45)},
        {"distance_m": Decimal(50)},
        {"kind": "warmup"},
        {"kind": "future"},
        {"rpe": Decimal(11)},
        {"completed_at": None},
        {"deleted": True},
    ],
)
def test_ineligible_estimates(changes: dict[str, object]) -> None:
    report = analyze_strength([replace(BASE, **changes)], PERIOD, series=SERIES)
    assert report.progression.is_empty()


def test_completion_evidence_and_missing_metrics() -> None:
    rows = [
        replace(BASE, completed_at=None),
        replace(BASE, completed_at=None, ended_at=None, set_id=UUID(int=4)),
        replace(BASE, completed_at=None, repetitions=None, set_id=UUID(int=5)),
        replace(BASE, repetitions=None, weight_kg=None, set_id=UUID(int=6)),
    ]
    strict = analyze_strength(rows, PERIOD, series=SERIES)
    bucket = strict.weekly_volume.row(0, named=True)
    assert bucket["completed_sets"] == 1
    assert bucket["volume_load_kg"] is None and bucket["repetitions"] is None
    inferred = analyze_strength(rows, PERIOD, series=SERIES, infer_completion=True)
    bucket = inferred.weekly_volume.row(0, named=True)
    assert (
        bucket["completed_sets"] == 2 and bucket["sets_with_load"] == bucket["sets_with_reps"] == 1
    )
    assert bucket["inferred_sets"] == 1
    assert strict.weekly_volume["inferred_sets"].sum() == 0
    assert inferred.progression["completion_inferred"].to_list() == [True]


def test_bodyweight_assistance_and_duplicate_names() -> None:
    rows = [
        BASE,
        replace(BASE, exercise_id=UUID(int=5), set_id=UUID(int=6)),
        replace(BASE, weight_kg=None, exercise_id=UUID(int=7), set_id=UUID(int=8)),
    ]
    report = analyze_strength(
        rows, PERIOD, series={**SERIES, UUID(int=5): ExerciseSeries("assisted")}
    )
    assert report.weekly_activity["exercises_performed"][0] == 3
    assert report.progression["exercise_key"].to_list() == ["series:press"]
    assert report.weekly_volume["sets_with_load"].to_list() == [0, 0, 1]
    assert report.weekly_volume["repetitions"].to_list() == [6, 6, 6]


def test_ties_and_rep_boundaries() -> None:
    row = replace(BASE, repetitions=1, weight_kg=Decimal(30), rpe=None)
    other = replace(row, set_id=UUID(int=99))
    assert analyze_strength([other, row], PERIOD, series=SERIES).progression.select(
        "set_id", "estimated_1rm_kg"
    ).rows() == [(str(BASE.set_id), Decimal(31))]
    assert analyze_strength(
        [row], PERIOD, series=SERIES, rpe_range=(Decimal(7), Decimal(10))
    ).progression.is_empty()


def test_empty_partial_weeks_and_fall_back() -> None:
    period = Period(date(2025, 11, 2), date(2025, 11, 4), ZoneInfo("America/New_York"))
    times = [
        "2025-11-02T03:59:59",
        "2025-11-02T04:00:00",
        "2025-11-02T05:30:00",
        "2025-11-02T06:30:00",
        "2025-11-03T05:00:00",
        "2025-11-04T05:00:00",
    ]
    rows = [
        Observation(UUID(int=i), datetime.fromisoformat(t).replace(tzinfo=UTC), None)
        for i, t in enumerate(times)
    ]
    activity = analyze_strength(rows, period).weekly_activity
    assert activity.rows() == [
        (date(2025, 10, 27), 3, 0, 0, 0, None),
        (date(2025, 11, 3), 1, 0, 0, 0, -2),
    ]
    empty = analyze_strength([], period)
    assert empty.weekly_activity["workouts"].to_list() == [0, 0]
    assert empty.weekly_volume.is_empty() and empty.progression.is_empty()


def test_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="stop"):
        Period(PERIOD.start, PERIOD.start)
    with pytest.raises(ValueError, match="duplicate"):
        analyze_strength([BASE, BASE], PERIOD)
    with pytest.raises(ValueError, match="aware"):
        analyze_strength([replace(BASE, started_at=START.replace(tzinfo=None))], PERIOD)
    with pytest.raises(ValueError, match="RPE"):
        analyze_strength([], PERIOD, rpe_range=(Decimal(10), Decimal(7)))


@pytest.mark.postgres
def test_query_isolation_deletion_supersets_and_local_range(db: Session) -> None:
    owner, other = User(), User()
    db.add_all([owner, other])
    db.flush()

    def workout(person: User, **fields: object) -> Workout:
        row = Workout(
            user_id=person.id,
            title="Synthetic",
            started_at=fields.pop("started_at", START),
            **fields,
        )
        db.add(row)
        db.flush()
        return row

    active = workout(owner)
    empty = workout(owner)
    foreign = workout(other)
    for w in (active, foreign):
        for i in range(2):
            ex = WorkoutExercise(
                user_id=w.user_id,
                workout_id=w.id,
                position=i,
                name="Same name",
                superset_group="pair",
            )
            db.add(ex)
            db.flush()
            db.add(
                ExerciseSet(
                    user_id=w.user_id,
                    exercise_id=ex.id,
                    position=0,
                    completed_at=START,
                    repetitions=3,
                    weight_kg=Decimal(40) if w is active else Decimal(90),
                    kind="normal",
                )
            )
    workout(owner, deleted_at=START)
    workout(owner, started_at=datetime(2024, 12, 30, 7, 59, tzinfo=UTC))
    deleted = workout(owner)
    account = SourceAccount(
        user_id=owner.id, status="active", provider="synthetic", provider_account_id="fixture"
    )
    db.add(account)
    db.flush()
    for i, (w, stamp) in enumerate([(deleted, START), (active, START), (active, None)]):
        db.add(
            ExternalReference(
                user_id=owner.id,
                provider=account.provider,
                source_account_id=account.id,
                external_id=str(i),
                entity_type="workout",
                workout_id=w.id,
                raw_payload={},
                source_deleted_at=stamp,
            )
        )
    db.flush()
    period = Period(PERIOD.start, PERIOD.stop, ZoneInfo("America/Los_Angeles"))

    def read(person: User) -> list[Observation]:
        return list(strength_observations(db, owner_id=person.id, period=period))

    rows = read(owner)
    assert {r.workout_id for r in rows} == {active.id, empty.id}
    assert len(rows) == 3
    assert {r.workout_id for r in read(other)} == {foreign.id}
    assert query_strength(db, owner_id=owner.id, period=period).weekly_activity.row(0) == (
        PERIOD.start,
        2,
        2,
        2,
        0,
        None,
    )

    series = {row.exercise_id: ExerciseSeries("press", True) for row in rows if row.exercise_id}
    grouped = query_strength(db, owner_id=owner.id, period=period, series=series)
    assert grouped.weekly_volume["volume_load_kg"].to_list() == [Decimal(240)]
    assert grouped.progression["estimated_1rm_kg"].to_list() == [Decimal(44)]


def test_known_zero_and_unmeasured_totals() -> None:
    rows = [
        replace(BASE, repetitions=0),
        replace(BASE, weight_kg=Decimal(0), set_id=UUID(int=4)),
        replace(BASE, weight_kg=None, repetitions=None, set_id=UUID(int=5)),
    ]
    report = analyze_strength(rows, PERIOD, series=SERIES)
    bucket = report.weekly_volume.row(0, named=True)
    assert bucket["sets_with_load"] == bucket["sets_with_reps"] == 2
    assert bucket["volume_load_kg"] == 0 and bucket["repetitions"] == 6
    assert report.progression.is_empty()

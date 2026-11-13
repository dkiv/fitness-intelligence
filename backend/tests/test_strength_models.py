import os
from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fitness_intelligence.db.models import (
    ExerciseSet,
    ExternalReference,
    User,
    Workout,
    WorkoutExercise,
)

pytestmark = pytest.mark.postgres


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch) -> Iterator[Session]:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a disposable PostgreSQL database")
    schema = "test_" + uuid4().hex
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
    scoped_url = make_url(url).update_query_dict({"options": f"-csearch_path={schema}"})
    monkeypatch.setenv("DATABASE_URL", scoped_url.render_as_string(hide_password=False))
    isolated = create_engine(scoped_url)
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    try:
        command.upgrade(config, "head")
        with Session(isolated) as session:
            yield session
    finally:
        isolated.dispose()
        with engine.begin() as connection:
            connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        engine.dispose()


def seed(db: Session) -> tuple[User, User, Workout, WorkoutExercise, ExerciseSet]:
    owner, other = User(), User()
    db.add_all([owner, other])
    db.flush()
    workout = Workout(user_id=owner.id, title="Synthetic session", started_at=datetime.now(UTC))
    db.add(workout)
    db.flush()
    exercise = WorkoutExercise(user_id=owner.id, workout_id=workout.id, name="Squat", position=0)
    db.add(exercise)
    db.flush()
    exercise_set = ExerciseSet(user_id=owner.id, exercise_id=exercise.id, position=0)
    db.add(exercise_set)
    db.commit()
    return owner, other, workout, exercise, exercise_set


def test_relationships_ordering_units_and_optional_fields(db: Session) -> None:
    owner, other, workout, exercise, exercise_set = seed(db)
    db.add_all(
        [
            WorkoutExercise(user_id=owner.id, workout_id=workout.id, position=2, name="Row"),
            WorkoutExercise(user_id=owner.id, workout_id=workout.id, position=1, name="Press"),
            ExerciseSet(user_id=owner.id, exercise_id=exercise.id, position=2),
            ExerciseSet(
                user_id=owner.id,
                exercise_id=exercise.id,
                position=1,
                weight_kg=Decimal("42.1250"),
                repetitions=8,
                rpe=Decimal("8.5"),
                duration_seconds=Decimal("35.5"),
                distance_m=Decimal("10.25"),
                source_measurements={"weight": 92.87, "weight_unit": "lb"},
            ),
        ]
    )
    db.commit()
    db.expire_all()
    assert workout.user == owner
    assert owner.workouts == [workout]
    assert other.workouts == []
    assert exercise.user == owner and exercise_set.user == owner
    assert [item.position for item in workout.exercises] == [0, 1, 2]
    assert [item.position for item in exercise.sets] == [0, 1, 2]
    assert exercise_set.weight_kg is None and exercise_set.repetitions is None
    assert exercise_set.rpe is None and exercise_set.completed_at is None
    assert exercise.sets[1].weight_kg == Decimal("42.1250")
    assert exercise.sets[1].source_measurements["weight_unit"] == "lb"
    assert workout.started_at.utcoffset().total_seconds() == 0
    assert db.scalars(select(Workout).where(Workout.user_id == other.id)).all() == []


@pytest.mark.parametrize("target", ["exercise", "set", "reference", "missing_user", "null_user"])
def test_invalid_ownership(db: Session, target: str) -> None:
    owner, other, workout, exercise, exercise_set = seed(db)
    records = {
        "exercise": WorkoutExercise(user_id=other.id, workout_id=workout.id, position=1, name="X"),
        "set": ExerciseSet(user_id=other.id, exercise_id=exercise.id, position=1),
        "reference": ExternalReference(
            user_id=other.id,
            provider="synthetic",
            entity_type="set",
            external_id="one",
            set_id=exercise_set.id,
            raw_payload={},
        ),
        "missing_user": Workout(user_id=uuid4(), title="X", started_at=datetime.now(UTC)),
        "null_user": Workout(user_id=None, title="X", started_at=datetime.now(UTC)),
    }
    db.add(records[target])
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


@pytest.mark.parametrize(
    "field,value",
    [
        ("position", -1),
        ("repetitions", -1),
        ("weight_kg", -1),
        ("distance_m", -1),
        ("duration_seconds", -1),
        ("rpe", -1),
        ("rpe", 11),
    ],
)
def test_invalid_set_quantities(db: Session, field: str, value: int) -> None:
    owner, _, _, exercise, _ = seed(db)
    item = ExerciseSet(user_id=owner.id, exercise_id=exercise.id, position=1)
    setattr(item, field, value)
    db.add(item)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


@pytest.mark.parametrize("level", ["exercise", "set"])
def test_duplicate_positions(db: Session, level: str) -> None:
    owner, _, workout, exercise, _ = seed(db)
    item = (
        WorkoutExercise(user_id=owner.id, workout_id=workout.id, name="X", position=0)
        if level == "exercise"
        else ExerciseSet(user_id=owner.id, exercise_id=exercise.id, position=0)
    )
    db.add(item)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


@pytest.mark.parametrize("entity_type", ["workout", "exercise", "set"])
def test_external_identity_and_sync(db: Session, entity_type: str) -> None:
    owner, other, workout, exercise, exercise_set = seed(db)
    target = {"workout": workout, "exercise": exercise, "set": exercise_set}[entity_type]
    target_key = {"workout": "workout_id", "exercise": "exercise_id", "set": "set_id"}[entity_type]

    def reference(user_id: UUID, provider: str = "synthetic") -> ExternalReference:
        return ExternalReference(
            user_id=user_id,
            provider=provider,
            entity_type=entity_type,
            external_id="stable-1",
            raw_payload={"synthetic": True},
            **{target_key: target.id},
        )

    first = reference(owner.id)
    db.add(first)
    db.commit()
    assert first.user == owner and first in owner.external_references
    assert first.first_imported_at.tzinfo is not None
    first.source_updated_at = datetime.now(UTC)
    first.source_deleted_at = datetime.now(UTC)
    first.source_version = "2"
    first.last_synced_at = datetime.now(UTC)
    db.add(reference(owner.id, "another-provider"))
    db.commit()
    db.add(reference(owner.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    # Identical source IDs are legal for different owners with their own target.
    second_workout = Workout(user_id=other.id, title="Other", started_at=datetime.now(UTC))
    db.add(second_workout)
    db.flush()
    db.add(
        ExternalReference(
            user_id=other.id,
            provider="synthetic",
            entity_type="workout",
            external_id="stable-1",
            workout_id=second_workout.id,
            raw_payload={},
        )
    )
    db.commit()


@pytest.mark.parametrize("case", ["missing", "multiple", "wrong_type", "empty_provider"])
def test_external_target_constraints(db: Session, case: str) -> None:
    owner, _, workout, exercise, _ = seed(db)
    item = ExternalReference(
        user_id=owner.id,
        provider="synthetic",
        entity_type="workout",
        external_id="one",
        workout_id=workout.id,
        raw_payload={},
    )
    if case == "missing":
        item.workout_id = None
    elif case == "multiple":
        item.exercise_id = exercise.id
    elif case == "wrong_type":
        item.entity_type = "set"
    else:
        item.provider = ""
    db.add(item)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_m1_downgrade_preserves_users(db: Session) -> None:
    owner, _, _, _, _ = seed(db)
    identity = owner.id
    db.close()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.downgrade(config, "0001")
    assert "workouts" not in inspect(db.bind).get_table_names()
    assert db.scalar(select(User.id).where(User.id == identity)) == identity
    db.close()
    command.upgrade(config, "head")
    command.check(config)
    assert db.scalar(select(User.id).where(User.id == identity)) == identity


def test_workout_time_constraint(db: Session) -> None:
    owner, _, _, _, _ = seed(db)
    db.add(
        Workout(
            user_id=owner.id,
            title="Invalid time",
            started_at=datetime(2026, 1, 2, tzinfo=UTC),
            ended_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


@pytest.mark.parametrize("target", ["workout", "exercise"])
def test_reference_owner_matches_target(db: Session, target: str) -> None:
    _, other, workout, exercise, _ = seed(db)
    target_id = workout.id if target == "workout" else exercise.id
    db.add(
        ExternalReference(
            user_id=other.id,
            provider="synthetic",
            entity_type=target,
            external_id="one",
            raw_payload={},
            **{target + "_id": target_id},
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_source_tombstone_retains_identity_and_blocks_hard_delete(db: Session) -> None:
    owner, _, workout, _, _ = seed(db)
    item = ExternalReference(
        user_id=owner.id,
        provider="synthetic",
        entity_type="workout",
        external_id="stable",
        workout_id=workout.id,
        raw_payload={"title": "Synthetic session"},
    )
    db.add(item)
    db.commit()
    imported_at = item.first_imported_at
    item.source_deleted_at = datetime.now(UTC)
    item.last_synced_at = datetime.now(UTC)
    db.commit()
    db.expire_all()
    assert item.first_imported_at == imported_at
    assert item.source_deleted_at is not None
    assert item.raw_payload == {"title": "Synthetic session"}
    assert db.scalar(select(Workout).where(Workout.user_id == owner.id)) == workout
    db.delete(workout)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

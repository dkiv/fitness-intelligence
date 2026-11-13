import copy
import json
from datetime import UTC
from decimal import Decimal

import pytest
from pydantic import ValidationError

from fitness_intelligence.adapters.hevy.mapping import map_workout
from fitness_intelligence.adapters.hevy.schemas import (
    EventPage,
    HevyWorkout,
    WorkoutPage,
    parse_workout,
)


def snapshot() -> dict:
    return dict(
        id="synthetic-workout",
        title="Sensitive synthetic title",
        description="Private text",
        routine_id=None,
        start_time="2026-01-01T12:00:00+02:00",
        end_time=None,
        created_at="2026-01-01T12:01:00Z",
        updated_at="2026-01-01T12:02:00Z",
        exercises=[
            dict(
                index=5,
                title="Synthetic press",
                notes=None,
                exercise_template_id="T1",
                superset_id=0,
                sets=[
                    dict(
                        index=7,
                        type="dropset",
                        weight_kg=0,
                        reps=8.0,
                        distance_meters=None,
                        duration_seconds=None,
                        rpe=9.5,
                        custom_metric=2.25,
                    )
                ],
            )
        ],
    )


def test_mapping_null_zero_decimal_units_privacy_and_timestamps() -> None:
    data = snapshot()
    data["api_key"] = "synthetic-excluded"
    result = map_workout(parse_workout(json.dumps(data)))
    exercise = result.workout.exercises[0]
    item = exercise.sets[0]
    assert result.workout.started_at.hour == 10
    assert result.workout.started_at.tzinfo == UTC
    assert result.workout.ended_at is None
    assert exercise.position == item.position == 0
    assert exercise.superset_group == "0"
    assert item.kind == "drop" and item.repetitions == 8
    assert item.weight_kg == Decimal("0.0000") and item.distance_m is None
    assert item.rpe == Decimal("9.50") and item.completed_at is None and item.notes is None
    assert item.source_measurements["custom_metric"] == "2.25"
    assert item.source_measurements["custom_metric_unit"] == "unknown"
    retained = json.dumps(result.raw_payload)
    assert "Sensitive" not in retained and "Private" not in retained
    assert "api_key" not in retained and "Synthetic press" not in retained
    assert result.raw_payload["start_time"].endswith("+02:00")
    assert result.external_id == "synthetic-workout"


@pytest.mark.parametrize(
    "field", ["end_time", "description", "routine_id", "exercises", "updated_at"]
)
def test_missing_workout_properties(field: str) -> None:
    data = snapshot()
    del data[field]
    with pytest.raises(ValidationError):
        HevyWorkout.model_validate(data)


@pytest.mark.parametrize(
    "field",
    [
        "type",
        "reps",
        "weight_kg",
        "rpe",
        "custom_metric",
        "duration_seconds",
        "distance_meters",
        "index",
    ],
)
def test_missing_set_properties(field: str) -> None:
    data = snapshot()
    del data["exercises"][0]["sets"][0][field]
    with pytest.raises(ValidationError):
        HevyWorkout.model_validate(data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("reps", 8.1),
        ("reps", True),
        ("index", -1),
        ("index", 1.5),
        ("index", "1"),
        ("reps", 2147483648),
        ("rpe", 10.01),
        ("rpe", -1),
        ("weight_kg", -1),
        ("weight_kg", "2"),
        ("weight_kg", True),
        ("weight_kg", float("inf")),
        ("weight_kg", float("nan")),
        ("weight_kg", Decimal("99999999.99991")),
        ("distance_meters", Decimal("10000000000")),
    ],
)
def test_invalid_measurements(field: str, value: object) -> None:
    data = snapshot()
    data["exercises"][0]["sets"][0][field] = value
    with pytest.raises(ValidationError):
        HevyWorkout.model_validate(data)


@pytest.mark.parametrize("value", ["2026-01-01T10:00:00", "bad", "2026-01-01", 123, None])
def test_invalid_timestamp(value: object) -> None:
    data = snapshot()
    data["start_time"] = value
    with pytest.raises(ValidationError):
        HevyWorkout.model_validate(data)


@pytest.mark.parametrize(
    "kind,expected",
    [
        (None, None),
        ("normal", "normal"),
        ("warmup", "warmup"),
        ("failure", "failure"),
        ("dropset", "drop"),
        ("new-type", None),
    ],
)
def test_kinds(kind: str | None, expected: str | None) -> None:
    data = snapshot()
    data["exercises"][0]["sets"][0]["type"] = kind
    result = map_workout(HevyWorkout.model_validate(data))
    assert result.workout.exercises[0].sets[0].kind == expected
    assert ("unknown_set_type" in result.warnings) == (kind == "new-type")
    assert result.raw_payload["exercises"][0]["sets"][0]["type"] == kind


@pytest.mark.parametrize("rpe", [0, 9.5, 10])
def test_read_rpe(rpe: float) -> None:
    data = snapshot()
    data["exercises"][0]["sets"][0]["rpe"] = rpe
    assert map_workout(HevyWorkout.model_validate(data)).workout.exercises[0].sets[
        0
    ].rpe == Decimal(str(rpe))


def test_rounding_ordering_duplicates_and_hash() -> None:
    data = snapshot()
    first = data["exercises"][0]
    second = copy.deepcopy(first)
    second["index"] = 1
    first["sets"].append({**first["sets"][0], "index": 2, "weight_kg": Decimal("1.23445")})
    data["exercises"].append(second)
    result = map_workout(HevyWorkout.model_validate(data))
    assert result.workout.exercises[1].sets[0].weight_kg == Decimal("1.2344")
    assert result.warnings == ("exercise_order_mismatch", "set_order_mismatch")
    data["exercises"].reverse()
    assert map_workout(HevyWorkout.model_validate(data)).content_hash == result.content_hash
    data["title"] = "Changed"
    assert map_workout(HevyWorkout.model_validate(data)).content_hash != result.content_hash
    data["exercises"][1]["sets"][1]["index"] = 7
    with pytest.raises(ValidationError):
        HevyWorkout.model_validate(data)


def test_empty_pages_and_events() -> None:
    assert WorkoutPage(page=1, page_count=0, workouts=[]).workouts == []
    page = EventPage.model_validate(
        dict(
            page=1,
            page_count=1,
            events=[
                dict(type="updated", workout=snapshot()),
                dict(type="deleted", id="unseen"),
                dict(type="deleted", id="known", deleted_at="2026-01-02T00:00:00Z"),
            ],
        )
    )
    assert page.events[1].deleted_at is None
    with pytest.raises(ValidationError):
        EventPage.model_validate(dict(page=1, page_count=1, events=[dict(type="other")]))


def test_json_nonfinite_size_and_error_privacy() -> None:
    data = json.dumps(snapshot()).replace('"weight_kg": 0', '"weight_kg": NaN')
    with pytest.raises(ValueError, match="invalid Hevy snapshot"):
        parse_workout(data)
    with pytest.raises(ValueError, match="size limit"):
        parse_workout(" " * 4_000_001)


def test_unknown_fields_are_excluded_with_bounded_warning() -> None:
    data = snapshot()
    data["profile"] = {"name": "Synthetic private name"}
    result = map_workout(HevyWorkout.model_validate(data))
    assert result.warnings == ("unknown_source_fields",)
    assert "profile" not in result.raw_payload


def test_duplicate_exercises_empty_children_and_time_order() -> None:
    data = snapshot()
    data["exercises"].append(copy.deepcopy(data["exercises"][0]))
    with pytest.raises(ValidationError):
        HevyWorkout.model_validate(data)
    data["exercises"] = []
    assert map_workout(HevyWorkout.model_validate(data)).workout.exercises == ()
    data["end_time"] = "2026-01-01T09:00:00Z"
    with pytest.raises(ValidationError):
        HevyWorkout.model_validate(data)


def test_direct_decimal_json_and_depth_limit() -> None:
    data = json.dumps(snapshot()).replace('"weight_kg": 0', '"weight_kg": 1.23455')
    result = map_workout(parse_workout(data))
    item = result.workout.exercises[0].sets[0]
    assert item.weight_kg == Decimal("1.2346")
    assert item.source_measurements["weight_kg"] == "1.23455"
    with pytest.raises(ValueError, match="invalid Hevy snapshot"):
        parse_workout("[" * 40 + "0" + "]" * 40)

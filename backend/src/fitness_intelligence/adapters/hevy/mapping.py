"""Deterministic mapping of a validated source snapshot; no IDs, I/O or clocks."""

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal
from hashlib import sha256
from typing import Any

from fitness_intelligence.domain.strength import StrengthExercise, StrengthSet, StrengthWorkout

from .schemas import HevyExercise, HevySet, HevyWorkout, utc

KINDS = {"normal": "normal", "warmup": "warmup", "failure": "failure", "dropset": "drop"}


def quantity(value: Decimal | None, places: int = 4) -> Decimal | None:
    return (
        None if value is None else value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_EVEN)
    )


def map_set(source: HevySet, position: int) -> StrengthSet:
    measurements = {
        key: None if value is None else str(value)
        for key, value in source.model_dump().items()
        if key
        in {"weight_kg", "reps", "distance_meters", "duration_seconds", "rpe", "custom_metric"}
    }
    measurements.update(
        weight_unit="kg", distance_unit="m", duration_unit="s", custom_metric_unit="unknown"
    )
    return StrengthSet(
        position,
        KINDS.get(source.type),
        source.reps,
        quantity(source.weight_kg),
        quantity(source.distance_meters),
        quantity(source.duration_seconds),
        quantity(source.rpe, 2),
        measurements,
    )


def map_exercise(source: HevyExercise, position: int) -> StrengthExercise:
    return StrengthExercise(
        position,
        source.title,
        source.notes,
        None if source.superset_id is None else str(source.superset_id),
        tuple(
            map_set(item, i)
            for i, item in enumerate(sorted(source.sets, key=lambda item: item.index))
        ),
    )


@dataclass(frozen=True)
class MappedWorkout:
    external_id: str
    workout: StrengthWorkout
    source_created_at: datetime
    source_updated_at: datetime
    raw_payload: dict[str, Any]
    content_hash: str
    warnings: tuple[str, ...]


def map_workout(source: HevyWorkout) -> MappedWorkout:
    warnings: set[str] = set()
    if any(
        getattr(item, "_has_unknown_fields", False)
        for item in (
            source,
            *source.exercises,
            *(entry for exercise in source.exercises for entry in exercise.sets),
        )
    ):
        warnings.add("unknown_source_fields")
    exercises = sorted(source.exercises, key=lambda item: item.index)
    if exercises != source.exercises:
        warnings.add("exercise_order_mismatch")
    projection = source.model_dump(mode="json", exclude={"title", "description", "exercises"})
    projected_exercises: list[dict[str, Any]] = []
    for exercise in exercises:
        sets = sorted(exercise.sets, key=lambda item: item.index)
        if sets != exercise.sets:
            warnings.add("set_order_mismatch")
        if any(item.type is not None and item.type not in KINDS for item in sets):
            warnings.add("unknown_set_type")
        projected_exercises.append(
            {
                "index": exercise.index,
                "exercise_template_id": exercise.exercise_template_id,
                "superset_id": exercise.superset_id,
                "sets": [item.model_dump(mode="json") for item in sets],
            }
        )
    projection["exercises"] = projected_exercises
    # Hash includes canonical text, but retained provenance excludes it.
    content = {
        **projection,
        "title": source.title,
        "description": source.description,
        "exercise_text": [(item.title, item.notes) for item in exercises],
    }
    digest = sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return MappedWorkout(
        source.id,
        StrengthWorkout(
            source.title,
            source.description,
            utc(source.start_time),
            None if source.end_time is None else utc(source.end_time),
            tuple(map_exercise(item, i) for i, item in enumerate(exercises)),
        ),
        utc(source.created_at),
        utc(source.updated_at),
        projection,
        digest,
        tuple(sorted(warnings)),
    )

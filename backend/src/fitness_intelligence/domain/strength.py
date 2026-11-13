"""Provider-independent normalized inputs, with no persistence side effects."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class StrengthSet:
    position: int
    kind: str | None
    repetitions: int | None
    weight_kg: Decimal | None
    distance_m: Decimal | None
    duration_seconds: Decimal | None
    rpe: Decimal | None
    source_measurements: dict[str, str | None]
    completed_at: datetime | None = None
    notes: str | None = None


@dataclass(frozen=True)
class StrengthExercise:
    position: int
    name: str
    notes: str | None
    superset_group: str | None
    sets: tuple[StrengthSet, ...]


@dataclass(frozen=True)
class StrengthWorkout:
    title: str
    notes: str | None
    started_at: datetime
    ended_at: datetime | None
    exercises: tuple[StrengthExercise, ...]

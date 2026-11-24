"""Manual-entry prescriptions. Durations and rest allowances are in seconds."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class Target[T: (int, Decimal)]:
    low: T
    nominal: T
    high: T

    def __post_init__(self) -> None:
        values = (self.low, self.nominal, self.high)
        if any(isinstance(v, Decimal) and not v.is_finite() for v in values):
            raise ValueError("target endpoints must be finite")
        if not 0 <= self.low <= self.nominal <= self.high:
            raise ValueError("target must have ordered, nonnegative endpoints")

    def has_integer_endpoints(self) -> bool:
        return all(type(value) is int for value in (self.low, self.nominal, self.high))


def fixed[T: (int, Decimal)](value: T) -> Target[T]:
    return Target(value, value, value)


@dataclass(frozen=True)
class SetGroup:
    kind: Literal["warmup", "working"]
    count: int
    reps: Target[int]
    external_kg: Target[Decimal]
    max_rpe: Decimal | None
    max_rest_seconds: int | None  # Between sets in this group, when specified.
    effort_cue: str | None = None

    def __post_init__(self) -> None:
        if type(self.count) is not int or not self.reps.has_integer_endpoints():
            raise ValueError("set counts and rep endpoints must be integers")
        if (
            self.count < 1
            or self.reps.low < 1
            or (self.max_rest_seconds is not None and self.max_rest_seconds < 0)
        ):
            raise ValueError("sets and reps must be positive and rest nonnegative")
        if self.max_rpe is not None and not (self.max_rpe.is_finite() and 0 <= self.max_rpe <= 10):
            raise ValueError("RPE must be finite and within 0–10")


@dataclass(frozen=True)
class Exercise:
    movement: str
    label: str
    equipment: str
    groups: tuple[SetGroup, ...]


@dataclass(frozen=True)
class StrengthSession:
    exercises: tuple[Exercise, ...]
    reserved_seconds: int  # Includes warm-up, rests and transitions.

    @property
    def working_sets(self) -> int:
        return sum(g.count for e in self.exercises for g in e.groups if g.kind == "working")


@dataclass(frozen=True)
class RunStep:
    purpose: Literal["warmup", "work", "recovery", "cooldown"]
    seconds: Target[int]
    rpe: Target[Decimal]

    def __post_init__(self) -> None:
        if not self.seconds.has_integer_endpoints() or self.seconds.low <= 0 or self.rpe.high > 10:
            raise ValueError("run steps require positive duration and RPE within 0–10")


@dataclass(frozen=True)
class Intervals:
    """Execute every listed step on every repeat, including a listed final recovery."""

    repeats: int
    steps: tuple[RunStep, ...]

    def __post_init__(self) -> None:
        if type(self.repeats) is not int or self.repeats < 1 or not self.steps:
            raise ValueError("intervals require a positive repeat count and at least one step")


@dataclass(frozen=True)
class RunSession:
    segments: tuple[RunStep | Intervals, ...]

    def __post_init__(self) -> None:
        if not self.segments:
            raise ValueError("a run requires at least one step")

    @property
    def duration_seconds(self) -> Target[int]:
        low = nominal = high = 0
        for segment in self.segments:
            repeats, steps = (
                (segment.repeats, segment.steps)
                if isinstance(segment, Intervals)
                else (1, (segment,))
            )
            for step in steps:
                low += repeats * step.seconds.low
                nominal += repeats * step.seconds.nominal
                high += repeats * step.seconds.high
        return Target(low, nominal, high)

    @property
    def reserved_seconds(self) -> int:
        return self.duration_seconds.high

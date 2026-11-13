"""Complete-snapshot read contract based on the reviewed Hevy OpenAPI design."""

import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictStr, model_validator


def integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("expected integral number")
    number = Decimal(str(value))
    if (
        not number.is_finite()
        or number != number.to_integral_value()
        or not 0 <= number <= 2147483647
    ):
        raise ValueError("integer outside supported range")
    return int(number)


def number(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("expected numeric measurement")
    result = Decimal(str(value))
    if not result.is_finite() or result < 0 or result.adjusted() > 20:
        raise ValueError("measurement outside supported range")
    return result


def timestamp(value: Any) -> str:
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("expected ISO timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp requires offset")
    return value


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


Integer = Annotated[int, BeforeValidator(integer)]
Number = Annotated[Decimal, BeforeValidator(number)]
Timestamp = Annotated[str, BeforeValidator(timestamp)]
Identity = Annotated[StrictStr, Field(min_length=1, max_length=1024)]


class SourceModel(BaseModel):
    model_config = ConfigDict(extra="ignore", hide_input_in_errors=True, frozen=True)

    @model_validator(mode="wrap")
    @classmethod
    def detect_unknown(cls, value: Any, handler: Any) -> Any:
        result = handler(value)
        object.__setattr__(
            result,
            "_has_unknown_fields",
            isinstance(value, dict) and bool(value.keys() - cls.model_fields.keys()),
        )
        return result


class HevySet(SourceModel):
    index: Integer
    type: StrictStr | None
    weight_kg: Number | None
    reps: Integer | None
    distance_meters: Number | None
    duration_seconds: Number | None
    rpe: Number | None
    custom_metric: Number | None

    @model_validator(mode="after")
    def bounds(self) -> "HevySet":
        for value, maximum in (
            (self.weight_kg, Decimal("99999999.9999")),
            (self.distance_meters, Decimal("9999999999.9999")),
            (self.duration_seconds, Decimal("9999999999.9999")),
            (self.rpe, Decimal(10)),
        ):
            if value is not None and value > maximum:
                raise ValueError("measurement exceeds canonical range")
        return self


def unique_indexes(items: list[Any]) -> None:
    if len({item.index for item in items}) != len(items):
        raise ValueError("duplicate source indexes")


class HevyExercise(SourceModel):
    index: Integer
    title: StrictStr
    notes: StrictStr | None
    exercise_template_id: Identity
    superset_id: Integer | None
    sets: list[HevySet] = Field(max_length=10000)

    @model_validator(mode="after")
    def ordering(self) -> "HevyExercise":
        unique_indexes(self.sets)
        return self


class HevyWorkout(SourceModel):
    id: Identity
    title: StrictStr
    description: StrictStr | None
    routine_id: Identity | None
    start_time: Timestamp
    end_time: Timestamp | None
    created_at: Timestamp
    updated_at: Timestamp
    exercises: list[HevyExercise] = Field(max_length=10000)

    @model_validator(mode="after")
    def complete(self) -> "HevyWorkout":
        unique_indexes(self.exercises)
        if self.end_time is not None and utc(self.end_time) < utc(self.start_time):
            raise ValueError("workout ends before start")
        if utc(self.updated_at) < utc(self.created_at):
            raise ValueError("source update precedes creation")
        return self


class UpdatedEvent(SourceModel):
    type: Literal["updated"]
    workout: HevyWorkout


class DeletedEvent(SourceModel):
    type: Literal["deleted"]
    id: Identity
    # Missing deletion time is explicitly unresolved, never synthesized.
    deleted_at: Timestamp | None = None


class WorkoutPage(SourceModel):
    page: Integer = Field(ge=1)
    page_count: Integer
    workouts: list[HevyWorkout]


class EventPage(SourceModel):
    page: Integer = Field(ge=1)
    page_count: Integer
    events: list[Annotated[UpdatedEvent | DeletedEvent, Field(discriminator="type")]]


def invalid_constant(value: str) -> None:
    raise ValueError("nonfinite JSON number")


def parse_workout(payload: str) -> HevyWorkout:
    if len(payload.encode("utf-8")) > 4_000_000:
        raise ValueError("source snapshot exceeds size limit")
    try:
        data = json.loads(payload, parse_float=Decimal, parse_constant=invalid_constant)

        def check_depth(item: Any, depth: int = 0) -> None:
            if depth > 32:
                raise ValueError("source nesting limit")
            if isinstance(item, dict):
                for child in item.values():
                    check_depth(child, depth + 1)
            elif isinstance(item, list):
                for child in item:
                    check_depth(child, depth + 1)

        check_depth(data)
        return HevyWorkout.model_validate(data)
    except (ValueError, RecursionError):
        raise ValueError("invalid Hevy snapshot") from None

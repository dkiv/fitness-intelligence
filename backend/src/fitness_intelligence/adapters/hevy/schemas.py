"""Complete-snapshot read contract based on the reviewed Hevy OpenAPI design."""

import json
import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal, Self

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


# Strict calendar ISO form; reject all fractions longer than six digits, even trailing zeros.
TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-][0-9]{2}:[0-9]{2})"
)


def utc(value: str) -> datetime:
    if not isinstance(value, str) or TIMESTAMP.fullmatch(value) is None:
        raise ValueError("expected offset-aware ISO timestamp with microsecond precision or less")
    if value[-1] != "Z" and (int(value[-5:-3]) > 23 or int(value[-2:]) > 59):
        raise ValueError("invalid timestamp offset")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except (ValueError, OverflowError):
        raise ValueError("timestamp outside supported UTC range") from None


def timestamp(value: Any) -> str:
    utc(value)
    return value


Integer = Annotated[int, BeforeValidator(integer)]
Number = Annotated[Decimal, BeforeValidator(number)]
Timestamp = Annotated[str, BeforeValidator(timestamp)]
Identity = Annotated[StrictStr, Field(min_length=1, max_length=1024)]


class SourceModel(BaseModel):
    model_config = ConfigDict(extra="ignore", hide_input_in_errors=True, frozen=True)

    @classmethod
    def model_validate_json(cls, json_data: str | bytes | bytearray, **kwargs: Any) -> Self:
        # Prevent the inherited Pydantic JSON decoder from introducing binary floats.
        return cls.model_validate(decode_response(json_data), **kwargs)

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


MAX_RESPONSE_BYTES = 4_000_000
MAX_RESPONSE_DEPTH = 32


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def decode_response(payload: str | bytes | bytearray) -> dict[str, Any]:
    """Decode one UTF-8 JSON object without losing numeric precision."""
    try:
        if not isinstance(payload, (str, bytes, bytearray)):
            raise ValueError("unsupported response type")
        encoded = payload.encode("utf-8") if isinstance(payload, str) else payload
        if len(encoded) > MAX_RESPONSE_BYTES:
            raise ValueError("source response exceeds size limit")
        data = json.loads(
            encoded.decode("utf-8"),
            parse_float=Decimal,
            parse_int=Decimal,
            parse_constant=invalid_constant,
            object_pairs_hook=unique_object,
        )

        def check_depth(item: Any, depth: int = 0) -> None:
            if depth > MAX_RESPONSE_DEPTH:
                raise ValueError("source nesting limit")
            if isinstance(item, dict):
                for child in item.values():
                    check_depth(child, depth + 1)
            elif isinstance(item, list):
                for child in item:
                    check_depth(child, depth + 1)

        check_depth(data)
        if not isinstance(data, dict):
            raise ValueError("response must be an object")
        return data
    except (ValueError, ArithmeticError, RecursionError):
        # Keep source values out of public decoding errors.
        raise ValueError(
            "invalid Hevy snapshot (JSON structure, size limit or numeric value)"
        ) from None


def parse_workout(payload: str | bytes | bytearray) -> HevyWorkout:
    return HevyWorkout.model_validate_json(payload)


def parse_workout_page(payload: str | bytes | bytearray) -> WorkoutPage:
    return WorkoutPage.model_validate_json(payload)


def parse_event_page(payload: str | bytes | bytearray) -> EventPage:
    return EventPage.model_validate_json(payload)

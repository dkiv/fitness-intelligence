"""Synthetic serialized-response regressions for the mapping foundation."""

import copy
import json
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError
from test_hevy_mapping import snapshot

from fitness_intelligence.adapters.hevy.mapping import map_workout, semantic_number
from fitness_intelligence.adapters.hevy.schemas import (
    EventPage,
    HevyWorkout,
    WorkoutPage,
    decode_response,
    parse_event_page,
    parse_workout,
    parse_workout_page,
)

KINDS = ("detail", "workouts", "events")


def wrap(payload: str, kind: str) -> str:
    if kind == "detail":
        return payload
    if kind == "workouts":
        return '{"page":1,"page_count":1,"workouts":[' + payload + "]}"
    return '{"page":1,"page_count":1,"events":[{"type":"updated","workout":' + payload + "}]}"


def parse(payload: str | bytes, kind: str, direct: bool = False) -> Any:
    parsers = {"detail": parse_workout, "workouts": parse_workout_page, "events": parse_event_page}
    models = {"detail": HevyWorkout, "workouts": WorkoutPage, "events": EventPage}
    result = models[kind].model_validate_json(payload) if direct else parsers[kind](payload)
    if kind == "workouts":
        return result.workouts[0]
    if kind == "events":
        return result.events[0].workout
    return result


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("direct", [False, True])
@pytest.mark.parametrize(
    "literal,expected",
    [
        ("1.23445000000000001", "1.2345"),
        ("1.23444999999999999", "1.2344"),
        ("1.23445", "1.2344"),
        ("1.23455", "1.2346"),
    ],
)
def test_decimal_boundary_across_json_entries(
    kind: str, direct: bool, literal: str, expected: str
) -> None:
    payload = json.dumps(snapshot()).replace('"weight_kg": 0', '"weight_kg": ' + literal)
    source = parse(wrap(payload, kind).encode(), kind, direct)
    result = map_workout(source)
    item = result.workout.exercises[0].sets[0]
    assert item.weight_kg == Decimal(expected)
    assert item.source_measurements["weight_kg"] == literal
    assert result.raw_payload["exercises"][0]["sets"][0]["weight_kg"] == literal


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("field,original", [("index", "7"), ("reps", "8.0")])
@pytest.mark.parametrize("literal", ["7.00000000000000001", "7.99999999999999999"])
def test_fractional_integer_boundaries(kind: str, field: str, original: str, literal: str) -> None:
    payload = json.dumps(snapshot()).replace(f'"{field}": {original}', f'"{field}": {literal}')
    with pytest.raises(ValidationError):
        parse(wrap(payload, kind), kind)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("direct", [False, True])
@pytest.mark.parametrize(
    "invalid",
    [
        "null",
        "[]",
        "3",
        '"text"',
        "true",
        "{",
        '{"x":NaN}',
        '{"x":Infinity}',
        '{"x":-Infinity}',
        '{"x":1,"x":2}',
        '{"x":01}',
        '{"x":1e}',
    ],
)
def test_invalid_json_and_structures(kind: str, direct: bool, invalid: str) -> None:
    with pytest.raises(ValueError):
        parse(invalid, kind, direct)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("direct", [False, True])
def test_byte_and_depth_limits(kind: str, direct: bool) -> None:
    payload = wrap(json.dumps(snapshot()), kind)
    # Multibyte characters verify that the bound measures bytes, not code points.
    oversized = payload[:-1] + ',"extra":"' + "é" * 2_000_000 + '"}'
    with pytest.raises(ValueError, match="size limit"):
        parse(oversized, kind, direct)
    nested = payload[:-1] + ',"extra":' + "[" * 33 + "0" + "]" * 33 + "}"
    with pytest.raises(ValueError):
        parse(nested, kind, direct)
    # A valid source with shallow unknown data still works.
    assert parse(payload, kind, direct).id == "synthetic-workout"


def test_decoder_exact_numbers_and_supported_inputs() -> None:
    data = decode_response(bytearray(b'{"integer":20,"decimal":20.0000}'))
    assert type(data["integer"]) is Decimal and type(data["decimal"]) is Decimal
    assert str(data["decimal"]) == "20.0000"
    for payload in (b"\xff", None, {}, "\ud800"):
        with pytest.raises(ValueError):
            decode_response(payload)


@pytest.mark.parametrize("field", ["start_time", "end_time", "created_at", "updated_at"])
@pytest.mark.parametrize(
    "value",
    [
        "0001-01-01T00:00:00+01:00",
        "9999-12-31T23:59:59-01:00",
        "2026-01-01T12:00:00.1234567Z",
        "2026-01-01T12:00:00.1234560Z",
        "2026-01-01T12:00:00.0000000+02:00",
    ],
)
def test_timestamp_range_and_precision(field: str, value: str) -> None:
    data = snapshot()
    data[field] = value
    with pytest.raises(ValidationError):
        parse_workout(json.dumps(data))


def test_deleted_event_timestamp_policy() -> None:
    for value in ("0001-01-01T00:00:00+01:00", "2026-01-01T12:00:00.1234567Z"):
        payload = dict(
            page=1, page_count=1, events=[dict(type="deleted", id="synthetic", deleted_at=value)]
        )
        with pytest.raises(ValidationError):
            parse_event_page(json.dumps(payload))
    page = parse_event_page('{"page":1,"page_count":1,"events":[{"type":"deleted","id":"x"}]}')
    assert page.events[0].deleted_at is None


def digest(data: dict) -> str:
    return map_workout(HevyWorkout.model_validate(data)).content_hash


@pytest.mark.parametrize("exponent", [1_000, 1_000_000])
def test_semantic_number_does_not_expand_exponents(exponent: int) -> None:
    assert semantic_number(Decimal(f"1e-{exponent}")) == f"1e-{exponent}"
    assert semantic_number(Decimal(f"10e-{exponent + 1}")) == f"1e-{exponent}"


@pytest.mark.parametrize("kind", KINDS)
def test_tiny_custom_metric_hash_is_bounded_exact_and_preserves_provenance(kind: str) -> None:
    def mapped(literal: str) -> Any:
        payload = json.dumps(snapshot()).replace(
            '"custom_metric": 2.25', '"custom_metric": ' + literal
        )
        return map_workout(parse(wrap(payload, kind), kind))

    result = mapped("1e-1000000")
    assert result.content_hash == mapped("10e-1000001").content_hash
    assert result.content_hash != mapped("2e-1000000").content_hash
    assert result.content_hash != mapped("0").content_hash
    assert result.content_hash != mapped("null").content_hash
    assert result.raw_payload["exercises"][0]["sets"][0]["custom_metric"] == "1E-1000000"
    assert result.workout.exercises[0].sets[0].source_measurements["custom_metric"] == "1E-1000000"


def test_semantic_number_preserves_precision_beyond_decimal_context() -> None:
    value = "123456789012345678901234567890123456789"
    assert semantic_number(Decimal(value + "e-100")) == value + "e-100"
    assert semantic_number(Decimal(value + "0e-101")) == value + "e-100"
    assert semantic_number(Decimal("-0.000")) == "0"


@pytest.mark.parametrize("literal", ["20", "20.0", "20.0000", "2e1"])
def test_numeric_hash_equivalence_preserves_provenance(literal: str) -> None:
    payload = json.dumps(snapshot()).replace('"weight_kg": 0', '"weight_kg": ' + literal)
    result = map_workout(parse_workout(payload))
    baseline = json.dumps(snapshot()).replace('"weight_kg": 0', '"weight_kg": 20')
    assert result.content_hash == map_workout(parse_workout(baseline)).content_hash
    assert result.workout.exercises[0].sets[0].source_measurements["weight_kg"] == str(
        Decimal(literal)
    )


@pytest.mark.parametrize(
    "field,values",
    [
        ("weight_kg", ("1.2344401", "1.2344499")),
        ("distance_meters", ("1.2344401", "1.2344499")),
        ("duration_seconds", ("1.2344401", "1.2344499")),
        ("rpe", ("7.501", "7.504")),
        ("custom_metric", ("20.0", "20.0000")),
    ],
)
def test_hash_supported_precision(field: str, values: tuple[str, str]) -> None:
    data = snapshot()
    hashes = []
    for value in values:
        data["exercises"][0]["sets"][0][field] = Decimal(value)
        hashes.append(digest(data))
    assert hashes[0] == hashes[1]


@pytest.mark.parametrize("field", ["start_time", "end_time", "created_at", "updated_at"])
def test_hash_timestamp_equivalence(field: str) -> None:
    data = snapshot()
    hashes = []
    for value in (
        "2026-01-01T12:01:00Z",
        "2026-01-01T14:01:00.000000+02:00",
        "2026-01-01T07:01:00-05:00",
    ):
        data[field] = value
        hashes.append(digest(data))
    assert len(set(hashes)) == 1


@pytest.mark.parametrize(
    "field", ["weight_kg", "distance_meters", "duration_seconds", "rpe", "custom_metric", "reps"]
)
def test_hash_null_zero_and_actual_change(field: str) -> None:
    data = snapshot()
    hashes = []
    for value in (None, 0, 1):
        data["exercises"][0]["sets"][0][field] = value
        hashes.append(digest(data))
    assert len(set(hashes)) == 3


def test_hash_preserves_text_types_and_child_order() -> None:
    original = snapshot()
    exercise = original["exercises"][0]
    exercise["sets"].append({**exercise["sets"][0], "index": 8, "reps": 9})
    original["exercises"].append({**copy.deepcopy(exercise), "index": 6, "title": "Other"})
    baseline = digest(original)
    for mutation in ("exercise_order", "set_order", "unknown_type", "text", "custom_precision"):
        data = copy.deepcopy(original)
        exercise = data["exercises"][0]
        if mutation == "exercise_order":
            exercise["index"], data["exercises"][1]["index"] = 6, 5
        elif mutation == "set_order":
            exercise["sets"][0]["index"], exercise["sets"][1]["index"] = 8, 7
        elif mutation == "unknown_type":
            exercise["sets"][0]["type"] = "new-type"
        elif mutation == "text":
            exercise["notes"] = "Synthetic change"
        else:
            exercise["sets"][0]["custom_metric"] = Decimal("2.25000000000000001")
        assert digest(data) != baseline


@pytest.mark.parametrize("kind", KINDS)
def test_exact_limits_and_empty_pages(kind: str) -> None:
    payload = wrap(json.dumps(snapshot()), kind)
    assert (
        parse(payload + " " * (4_000_000 - len(payload.encode())), kind).id == "synthetic-workout"
    )
    assert parse(payload[:-1] + ',"extra":' + "[" * 31 + "0" + "]" * 31 + "}", kind)
    assert parse_workout_page('{"page":1,"page_count":0,"workouts":[]}').workouts == []
    assert parse_event_page('{"page":1,"page_count":0,"events":[]}').events == []


@pytest.mark.parametrize("offset", ["+00:60", "+24:00", "-01:99"])
def test_invalid_timestamp_offsets(offset: str) -> None:
    data = snapshot()
    data["start_time"] = "2026-01-01T12:00:00" + offset
    with pytest.raises(ValidationError):
        parse_workout(json.dumps(data))


def test_unknown_types_and_microseconds_remain_significant() -> None:
    data = snapshot()
    hashes = []
    for kind in (None, "unknown-a", "unknown-b"):
        data["exercises"][0]["sets"][0]["type"] = kind
        hashes.append(digest(data))
    assert len(set(hashes)) == 3
    data["updated_at"] = "2026-01-01T12:02:00.000001Z"
    assert digest(data) != hashes[-1]

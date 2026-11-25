"""Version 1 JSONB boundary for synthetic E1 plans. No ORM objects or provider data on the wire."""

import json
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, Literal
from zoneinfo import ZoneInfo

from pydantic import TypeAdapter

from fitness_intelligence.planning.planner import Fact, Finding, Slot, WeekPlan, WeekReview
from fitness_intelligence.planning.planner import Session as PlannedSession
from fitness_intelligence.planning.press_block import Availability, PressBlock, PressDose


class InvalidSnapshot(ValueError):
    """Unknown schema, noncanonical JSON, or an invalid prescription."""


@dataclass(frozen=True)
class PlanningContext:
    availability: Availability
    review: WeekReview | None = None


@dataclass(frozen=True)
class Generate:
    number: Literal[1, 2]
    thursday: PressDose | None = None


@dataclass(frozen=True)
class Move:
    slot: Slot
    day: date
    start: time


@dataclass(frozen=True)
class EvidenceRef:
    release_id: str
    claim_id: str

    def __post_init__(self) -> None:
        if not all(s.strip() and len(s) <= 128 for s in (self.release_id, self.claim_id)):
            raise ValueError("invalid evidence identifier")


@dataclass(frozen=True)
class Candidate:
    request: Generate | Move
    week: WeekPlan
    evidence: tuple[EvidenceRef, ...]


CONTEXT = TypeAdapter(PlanningContext)
BLOCK = TypeAdapter(PressBlock)
CANDIDATE = TypeAdapter(Candidate)


def _fact(value: Fact) -> object:
    # A finding can legitimately contain the literal string "30" or a measured Decimal("30").
    # Field types disambiguate ordinary prescription values. Heterogeneous facts need a tag.
    if isinstance(value, (Decimal, date, time)):
        return {f"${type(value).__name__.lower()}": _value(value)}
    return value


def _read_scalar(obj: dict[str, Any]) -> Any:
    if obj.keys() == {"$decimal"}:
        return Decimal(obj["$decimal"])
    if obj.keys() == {"$date"}:
        return date.fromisoformat(obj["$date"])
    if obj.keys() == {"$time"}:
        return time.fromisoformat(obj["$time"])
    return obj


def _value(value: Any) -> Any:
    if isinstance(value, Finding):
        return {
            "rule": value.rule,
            "slots": list(value.slots),
            "facts": [[k, _fact(v)] for k, v in value.facts],
        }
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _value(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, tuple):
        return [_value(item) for item in value]
    if isinstance(value, frozenset):
        return sorted(_value(item) for item in value)
    if isinstance(value, ZoneInfo):
        return value.key
    if isinstance(value, datetime):
        if value.utcoffset() is None:
            raise InvalidSnapshot("expected an aware instant")
        return value.astimezone(UTC).isoformat()
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        if not value.is_finite() or abs(value.adjusted()) > 32 or len(value.as_tuple().digits) > 64:
            raise InvalidSnapshot("quantity exceeds snapshot precision")
        if not value:
            return "0"
        whole, point, fraction = format(value, "f").partition(".")
        return (whole + point + fraction.rstrip("0")).rstrip(".")
    return value


def snapshot(value: PlanningContext | PressBlock | Candidate) -> dict[str, Any]:
    return {"schema_version": 1, "data": _value(value)}


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read[T: (PlanningContext, PressBlock, Candidate)](
    adapter: TypeAdapter[T], raw: dict[str, Any]
) -> T:
    """Require an exact wire round trip, including field names, scalars, ordering and version."""
    try:
        if raw.get("schema_version") != 1:
            raise InvalidSnapshot("unknown snapshot version")
        values = json.loads(canonical(raw["data"]), object_hook=_read_scalar)
        result = adapter.validate_python(values)
        if isinstance(result, PressBlock) and not (
            result.version.strip() and result.objective.strip() and result.goals
        ):
            raise InvalidSnapshot("block version, objective and goals are required")
        if canonical(snapshot(result)) != canonical(raw):
            raise InvalidSnapshot("unexpected field, version or noncanonical value")
    except (KeyError, TypeError, ValueError, ArithmeticError, RecursionError, AttributeError):
        raise InvalidSnapshot("invalid version 1 planning snapshot") from None
    return result


def calendar(week: WeekPlan | None) -> dict[tuple[int, Slot], PlannedSession]:
    """Stable slot identity is scoped to a week of this block."""
    sessions = {}
    while week is not None:
        number = week.inputs.number
        prior = week.inputs.previous
        if (number, prior.inputs.number if prior else None) not in ((1, None), (2, 1)):
            raise InvalidSnapshot("invalid predecessor week")
        if prior and prior.inputs.block != week.inputs.block:
            raise InvalidSnapshot("block continuity failure")
        dates = tuple(week.inputs.start + timedelta(days=i) for i in range(7))
        if tuple(d.day for d in week.days) != dates:
            raise InvalidSnapshot("expected seven contiguous local dates")
        seen = set()
        for day in week.days:
            for session in day.sessions:
                if session.day != day.day or session.slot in seen:
                    raise InvalidSnapshot("misplaced or duplicate session")
                seen.add(session.slot)
                sessions[number, session.slot] = session
        if seen != set(Slot):
            raise InvalidSnapshot("incomplete E1 schedule")
        week = prior
    return sessions

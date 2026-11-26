"""Scoped synthetic observations and the exact field choices shown to the athlete."""

import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, field_validator, model_validator

from .familiar import RPE, Key, LoadConvention, Positive, Record, Text, unique
from .familiar_outcomes import Nonnegative, Quantity, StepExecution

type StepField = Annotated[
    str, Field(pattern=r"^step\.[1-9][0-9]*\.(status|elapsed_seconds|achieved_rpe)$")
]
type Name = (
    Literal[
        "completion",
        "reps",
        "kg",
        "outing",
        "elapsed_seconds",
        "moving_seconds",
        "distance_metres",
        "completed_work_repetitions",
    ]
    | StepField
)
type Value = bool | int | Decimal | Literal["completed", "partial", "not-performed"]
type Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


def digest(record: Record) -> str:
    wire = json.dumps(record.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(wire.encode()).hexdigest()


class SourceFact(Record):
    owner: UUID
    account: UUID
    workout: UUID
    reference: UUID | None  # Canonical external reference, where supplied by the projection.
    occurred_at: AwareDatetime  # Workout start, retained separately from confirmation time.
    revision: Text | None = None
    mapping: Text
    comparison: Text
    deleted: bool = False
    reference_active: bool = True

    @field_validator("occurred_at")
    @classmethod
    def utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


class StrengthFact(SourceFact):
    provider: Literal["synthetic-hevy"] = "synthetic-hevy"
    exercise: UUID
    member: UUID  # Canonical ExerciseSet.id
    movement: Key
    variation: Key
    equipment: Key
    load_convention: LoadConvention
    group: Key
    kind: Literal["working", "warmup"]
    ordinal: Positive
    reps: Nonnegative | None
    kg: Quantity | None
    provenance: Literal["provider-timestamp", "historically-inferred", "unknown"]
    completed_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def source_values(self) -> Self:
        if (self.completed_at is not None) != (self.provenance == "provider-timestamp"):
            raise ValueError("completion timestamp and original provenance disagree")
        if self.load_convention == "bodyweight" and self.kg not in (0, None):
            raise ValueError("bodyweight convention has zero external load")
        return self

    @property
    def eligible(self) -> dict[Name, Value]:
        values: dict[Name, Value] = {"completion": True}
        if self.reps is not None:
            values["reps"] = self.reps
        if self.kg is not None:
            values["kg"] = self.kg
        return values


class RunningFact(SourceFact):
    provider: Literal["synthetic-garmin"] = "synthetic-garmin"
    role: Key
    provenance: Literal["activity-summary", "unknown"]
    elapsed_seconds: Nonnegative | None = None
    moving_seconds: Nonnegative | None = None
    distance_metres: Quantity | None = None
    completed_work_repetitions: Nonnegative | None = None
    instructions: tuple[Text, ...] = ()
    # Only independently reported achieved steps, with expanded index and purpose.
    achieved_steps: tuple[StepExecution, ...] = ()

    @property
    def member(self) -> UUID:
        return self.workout  # EnduranceActivity's canonical primary key.

    @model_validator(mode="after")
    def scoped_steps(self) -> Self:
        unique((s.index for s in self.achieved_steps), "achieved step")
        return self

    @property
    def eligible(self) -> dict[Name, Value]:
        values: dict[Name, Value] = {"outing": True}
        for field in (
            "elapsed_seconds",
            "moving_seconds",
            "distance_metres",
            "completed_work_repetitions",
        ):
            if (value := getattr(self, field)) is not None:
                values[field] = value
        for step in self.achieved_steps:
            prefix = f"step.{step.index}."
            if step.status != "unknown":
                values[prefix + "status"] = step.status
            if step.elapsed_seconds is not None:
                values[prefix + "elapsed_seconds"] = step.elapsed_seconds
            if step.achieved_rpe is not None:
                values[prefix + "achieved_rpe"] = step.achieved_rpe
        return values


type Fact = Annotated[StrengthFact | RunningFact, Field(discriminator="provider")]


def index_facts(owner: UUID, account: UUID, facts: tuple[Fact, ...]) -> dict[UUID, Fact]:
    result = {}
    ordinals = set()
    workouts = {}
    references = {}
    exercises = {}
    for fact in facts:
        if (fact.owner, fact.account) != (owner, account):
            raise ValueError("wrong observation owner or source account")
        if fact.member in result:
            raise ValueError("duplicate canonical member")
        workout_scope = fact.provider, fact.occurred_at, fact.deleted
        if workouts.setdefault(fact.workout, workout_scope) != workout_scope:
            raise ValueError("inconsistent workout identity")
        if fact.reference is not None:
            identity = fact.workout, fact.reference_active
            if references.setdefault(fact.reference, identity) != identity:
                raise ValueError("inconsistent source reference")
        if isinstance(fact, StrengthFact):
            if exercises.setdefault(fact.exercise, fact.workout) != fact.workout:
                raise ValueError("exercise child belongs to a different workout")
            ordinal = fact.workout, fact.exercise, fact.group, fact.ordinal
            if ordinal in ordinals:
                raise ValueError("duplicate exercise group ordinal")
            ordinals.add(ordinal)
        result[fact.member] = fact
    if len({f.provider for f in facts}) > 1:
        raise ValueError("a source account belongs to one provider")
    return result


class Offer(Record):
    member: UUID
    source_digest: Digest
    fields: tuple[Name, ...]

    @classmethod
    def for_fact(cls, fact: Fact) -> Self:
        return cls(
            member=fact.member, source_digest=digest(fact), fields=tuple(sorted(fact.eligible))
        )


class Display(Record):
    schema_version: Literal[1] = 1
    owner: UUID
    account: UUID
    members: Annotated[tuple[Fact, ...], Field(min_length=1)]

    offers: tuple[Offer, ...]

    @model_validator(mode="after")
    def scoped(self) -> Self:
        index_facts(self.owner, self.account, self.members)
        if self.offers != tuple(Offer.for_fact(m) for m in self.members):
            raise ValueError("offered fields or source digest differ from display")
        if any(f.deleted or not f.reference_active for f in self.members):
            raise ValueError("deleted or inactive source cannot be displayed for confirmation")
        if tuple(sorted(self.members, key=display_order)) != self.members:
            raise ValueError("display members must have canonical order")
        return self

    @property
    def digest(self) -> str:
        return digest(self)


def display_order(fact: Fact) -> tuple:
    child = (fact.exercise, fact.group, fact.ordinal) if isinstance(fact, StrengthFact) else ()
    return fact.occurred_at, fact.workout, child, fact.member


def preview(owner: UUID, account: UUID, facts: tuple[Fact, ...]) -> Display:
    members = tuple(sorted(facts, key=display_order))
    return Display(
        owner=owner,
        account=account,
        members=members,
        offers=tuple(Offer.for_fact(m) for m in members),
    )


class AthleteReport(Record):
    """Independent report on this member, never copied from its instructions."""

    reps: Nonnegative | None = None
    kg: Quantity | None = None  # Same displayed load convention.
    set_rpe: RPE | None = None
    session_rpe: RPE | None = None
    tolerance: Text | None = None

    @model_validator(mode="after")
    def nonempty(self) -> Self:
        if all(value is None for value in self.model_dump().values()):
            raise ValueError("empty athlete report")
        return self


class Answer(Record):
    member: UUID
    disposition: Literal["confirm", "exclude", "uncertain", "withdraw"]
    fields: tuple[Name, ...] = ()
    reported: AthleteReport | None = None
    supersedes: UUID | None = None  # Previous command ID for this particular member.
    outcome: UUID | None = None  # Explicit E421 manual assertion.

    @field_validator("fields")
    @classmethod
    def mask(cls, value: tuple[Name, ...]) -> tuple[Name, ...]:
        unique(value, "confirmed field")
        return tuple(sorted(value))

    def validate_member(self, fact: Fact) -> None:
        if self.disposition != "confirm":
            if self.fields or self.reported or self.outcome:
                raise ValueError("unconfirmed member cannot assert fields, reports or attribution")
            if self.disposition == "withdraw" and self.supersedes is None:
                raise ValueError("withdrawal must identify an existing assertion")
            return
        if not self.fields and not self.reported:
            raise ValueError("select fields or supply an independent report")
        if not set(self.fields) <= fact.eligible.keys():
            raise ValueError("field absent or ineligible on displayed member")
        if self.reported:
            r = self.reported
            if isinstance(fact, StrengthFact):
                if r.session_rpe is not None:
                    raise ValueError("session RPE is outside set scope")
                if fact.load_convention == "bodyweight" and r.kg not in (0, None):
                    raise ValueError("incompatible reported load convention")
            elif any(x is not None for x in (r.reps, r.kg, r.set_rpe)):
                raise ValueError("set report is outside outing scope")
            if any(getattr(r, k) is not None and k in self.fields for k in ("reps", "kg")):
                raise ValueError("choose either displayed or independently reported value")


class Intent(Record):
    schema_version: Literal[1] = 1
    display: Display
    displayed_digest: Digest
    answers: tuple[Answer, ...]

    @model_validator(mode="after")
    def exact_scope(self) -> Self:
        if self.displayed_digest != self.display.digest:
            raise ValueError("display digest differs")
        if tuple(a.member for a in self.answers) != tuple(f.member for f in self.display.members):
            raise ValueError("answer each displayed member exactly once in display order")
        for fact, answer in zip(self.display.members, self.answers, strict=True):
            answer.validate_member(fact)
        return self


def prepare(
    display: Display, fields: tuple[Name, ...], *, exceptions: tuple[Answer, ...] = ()
) -> Intent:
    """Apply one chosen field mask across the displayed batch, with explicit member exceptions."""
    unique((answer.member for answer in exceptions), "member exception")
    by_member = {answer.member: answer for answer in exceptions}
    if by_member.keys() - {fact.member for fact in display.members}:
        raise ValueError("exception outside displayed batch")
    answers = tuple(
        by_member.get(fact.member)
        or Answer(member=fact.member, disposition="confirm", fields=fields)
        for fact in display.members
    )
    return Intent(display=display, displayed_digest=display.digest, answers=answers)


class Receipt(Record):
    command: UUID
    actor: UUID
    recorded_at: AwareDatetime
    intent_digest: Digest
    intent: Intent


class Attribution(Record):
    outcome: UUID
    cycle: UUID
    week: int
    occurrence: UUID
    origin_revision: UUID
    effective_head: UUID
    occurred_at: AwareDatetime
    current: bool


class Assertion(Record):
    command: UUID
    recorded_at: AwareDatetime
    source: Fact
    source_digest: Digest
    answer: Answer
    link: Attribution | None


class Support(Record):
    member: UUID
    history: tuple[Assertion, ...]  # Root to current member answer.
    state: Literal["confirmed", "excluded", "uncertain", "withdrawn", "stale"]
    reason: str | None
    confirmed: dict[Name, Value]
    unconfirmed: tuple[Name, ...]
    independent_report: AthleteReport | None

    @property
    def effective_link(self) -> Attribution | None:
        link = self.history[-1].link
        return link if self.state == "confirmed" and link and link.current else None

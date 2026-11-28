"""Immutable contracts for the synthetic familiar-dose planner (E4.1)."""

from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Annotated, Literal, Self
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

from .prescriptions import Target

type Key = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")]
type Text = Annotated[str, Field(min_length=1, max_length=512)]
type Positive = Annotated[int, Field(gt=0)]
type Seconds = Annotated[int, Field(ge=0, le=86400)]
type Minute = Annotated[int, Field(ge=0, lt=1440)]
type Sport = Literal["strength", "running"]
type LoadConvention = Literal["total-external-kg", "per-hand-kg", "bodyweight"]
type FamiliarRule = Literal["synthetic.familiar.hold.v1", "synthetic.familiar.hold.v2"]
RULE: FamiliarRule = "synthetic.familiar.hold.v2"
type RPE = Annotated[Decimal, Field(ge=0, le=10, allow_inf_nan=False)]


class Record(BaseModel):
    model_config = ConfigDict(
        frozen=True, strict=True, extra="forbid", revalidate_instances="always"
    )


def unique[T](values: Iterable[T], label: str) -> None:
    items = tuple(values)
    if len(set(items)) != len(items):
        raise ValueError(f"duplicate {label}")


class Effort(Record):
    scale: Literal["set-rpe-0-10", "run-step-rpe-0-10"]
    target: Target[Decimal]
    cap: RPE

    @model_validator(mode="after")
    def valid_target(self) -> Self:
        if self.target.high > self.cap:
            raise ValueError("effort target exceeds execution cap")
        return self


class SetTarget(Record):
    ordinal: Positive
    reps: Target[int]
    load: Target[Decimal]
    execution_seconds: Positive  # Reservation for the highest permitted rep/load endpoints.
    rest_after_seconds: Seconds

    @model_validator(mode="after")
    def positive_reps(self) -> Self:
        if self.reps.low < 1:
            raise ValueError("sets require a positive rep target")
        return self


class Group(Record):
    key: Key
    kind: Literal["warmup", "working"]
    effort: Effort
    sets: Annotated[tuple[SetTarget, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.effort.scale != "set-rpe-0-10" or tuple(s.ordinal for s in self.sets) != tuple(
            range(1, len(self.sets) + 1)
        ):
            raise ValueError("strength groups require set effort and consecutive ordinals")
        return self


class Exercise(Record):
    movement: Key
    variation: Key
    equipment: Key
    load_convention: LoadConvention
    load_step_kg: Annotated[Decimal, Field(gt=0)] | None = None
    transition_seconds: Seconds
    groups: Annotated[tuple[Group, ...], Field(min_length=1)]
    notes: str = ""

    @model_validator(mode="after")
    def valid_groups(self) -> Self:
        unique((g.key for g in self.groups), "exercise group")
        if self.load_convention == "bodyweight" and any(
            s.load.high for g in self.groups for s in g.sets
        ):
            raise ValueError("bodyweight convention has zero external load")
        if self.load_convention != "bodyweight":
            if self.load_step_kg is None or any(
                value % self.load_step_kg != 0
                for g in self.groups
                for s in g.sets
                for value in (s.load.low, s.load.nominal, s.load.high)
            ):
                raise ValueError("load endpoints must fit the equipment increment")
        return self


class Strength(Record):
    sport: Literal["strength"] = "strength"
    role: Key
    preparation_seconds: Seconds
    exercises: Annotated[tuple[Exercise, ...], Field(min_length=1)]
    notes: str = ""

    @model_validator(mode="after")
    def movements(self) -> Self:
        unique(((e.movement, e.variation) for e in self.exercises), "movement variation")
        if not self.minimum_exposure:
            raise ValueError("strength session requires a working set")
        return self

    @property
    def minimum_exposure(self) -> int:
        return sum(len(g.sets) for e in self.exercises for g in e.groups if g.kind == "working")

    @property
    def reserved_seconds(self) -> int:
        return self.preparation_seconds + sum(
            e.transition_seconds
            + sum(s.execution_seconds + s.rest_after_seconds for g in e.groups for s in g.sets)
            for e in self.exercises
        )


class Step(Record):
    purpose: Literal["warmup", "work", "recovery", "cooldown"]
    seconds: Target[int]
    effort: Effort

    @model_validator(mode="after")
    def running_step(self) -> Self:
        if self.seconds.low < 1 or self.effort.scale != "run-step-rpe-0-10":
            raise ValueError("running steps require positive seconds and running effort")
        return self


class Repeat(Record):
    count: Annotated[int, Field(ge=2, le=100)]
    work: Step
    between: Step
    final_recovery: Step | None = None

    @model_validator(mode="after")
    def purposes(self) -> Self:
        if (
            self.work.purpose != "work"
            or self.between.purpose != "recovery"
            or (self.final_recovery and self.final_recovery.purpose != "recovery")
        ):
            raise ValueError("invalid work/recovery order")
        return self

    def expand(self) -> tuple[Step, ...]:
        tail = (self.final_recovery,) if self.final_recovery else ()
        return (self.work, self.between) * (self.count - 1) + (self.work,) + tail


class Running(Record):
    sport: Literal["running"] = "running"
    role: Literal["easy", "long", "controlled", "faster"]
    time_basis: Literal["elapsed-seconds"] = "elapsed-seconds"
    preparation_seconds: Seconds
    segments: Annotated[tuple[Step | Repeat, ...], Field(min_length=1)]
    notes: str = ""

    @property
    def steps(self) -> tuple[Step, ...]:
        return tuple(
            step
            for seg in self.segments
            for step in (seg.expand() if isinstance(seg, Repeat) else (seg,))
        )

    @model_validator(mode="after")
    def structure(self) -> Self:
        purposes = tuple(step.purpose for step in self.steps)
        if "work" not in purposes or "warmup" in purposes[1:] or "cooldown" in purposes[:-1]:
            raise ValueError("expected ordered warm-up, work and cool-down")
        core = tuple(p for p in purposes if p not in ("warmup", "cooldown"))
        if core[0] != "work" or any(a == b for a, b in zip(core, core[1:], strict=False)):
            raise ValueError("work and recovery must alternate")
        if self.role in ("easy", "long") and core != ("work",):
            raise ValueError("continuous running requires one work step")
        return self

    @property
    def duration(self) -> Target[int]:
        steps = self.steps
        return Target(
            sum(s.seconds.low for s in steps),
            sum(s.seconds.nominal for s in steps),
            sum(s.seconds.high for s in steps),
        )

    @property
    def minimum_exposure(self) -> int:
        return self.duration.low

    @property
    def reserved_seconds(self) -> int:
        return self.preparation_seconds + self.duration.high


type Prescription = Annotated[Strength | Running, Field(discriminator="sport")]


class Template(Record):
    key: Key
    prescription: Prescription


class Objective(Record):
    sport: Sport
    rank: Positive
    outcome: Text


class EffortEvidence(Record):
    """Independent athlete report in the containing set or run step's 0–10 RPE scale."""

    observed_rpe: RPE | None = None
    confirmed_target: Target[Decimal] | None = None
    confirmed_cap: RPE | None = None

    @model_validator(mode="after")
    def instruction_bounds(self) -> Self:
        ceiling = self.confirmed_cap if self.confirmed_cap is not None else 10
        if self.confirmed_target is not None and self.confirmed_target.high > ceiling:
            raise ValueError("confirmed effort target exceeds its scale or confirmed cap")
        return self


class ActualSet(Record):
    movement: Key
    variation: Key
    equipment: Key
    convention: LoadConvention
    group: Key
    kind: Literal["warmup", "working"]
    ordinal: Positive
    reps: Positive
    kg: Annotated[Decimal, Field(ge=0, allow_inf_nan=False)]

    effort: EffortEvidence | None = Field(default=None, exclude_if=lambda value: value is None)

    # Optional jointly confirmed, previously performed upper endpoints on this same template.
    familiar_max_reps: Positive | None = None
    familiar_max_kg: Annotated[Decimal, Field(ge=0)] | None = None


class ActualStep(Record):
    purpose: Literal["warmup", "work", "recovery", "cooldown"]
    elapsed_seconds: Positive
    effort: EffortEvidence | None = Field(default=None, exclude_if=lambda value: value is None)
    familiar_max_seconds: Positive | None = None


class Observation(Record):
    support: Key
    provenance: Literal["synthetic-athlete-report", "synthetic-inference"]
    template: Key
    role: Key
    day: date
    confirmed: bool
    manageable: bool | None
    sets: tuple[ActualSet, ...] = ()
    steps: tuple[ActualStep, ...] = ()

    @model_validator(mode="after")
    def typed_work(self) -> Self:
        if bool(self.sets) == bool(self.steps):
            raise ValueError("record one observed sport per session")
        return self


class Window(Record):
    weekday: Annotated[int, Field(ge=0, le=6)]
    start_minute: Minute
    end_minute: Annotated[int, Field(gt=0, le=1440)]
    equipment: tuple[Key, ...]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.start_minute >= self.end_minute:
            raise ValueError("empty availability window")
        return self


class FixedStart(Record):
    template: Key
    day: date
    minute: Minute
    fold: Literal[0, 1] | None = None


class Event(Record):
    start: AwareDatetime
    end: AwareDatetime

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end.timestamp() <= self.start.timestamp():
            raise ValueError("empty event")
        return self


class Spacing(Record):
    first: Key
    second: Key
    elapsed_seconds: Positive  # Symmetric minimum start-to-start interval.


class Interruption(Record):
    template: Key
    since: date
    reason: Text


class Context(Record):
    interruptions: tuple[Interruption, ...] = Field(default=(), exclude_if=lambda x: not x)
    zone: str
    objectives: Annotated[tuple[Objective, ...], Field(min_length=2)]
    preferred_weekdays: tuple[Annotated[int, Field(ge=0, le=6)], ...] = ()
    windows: tuple[Window, ...]
    unavailable_dates: tuple[date, ...] = ()
    excluded_tasks: tuple[Key, ...] = ()
    fixed: tuple[FixedStart, ...] = ()
    events: tuple[Event, ...] = ()
    history_start: date  # Beginning of one explicitly selected representative seven-day period.
    observations: tuple[Observation, ...]

    @model_validator(mode="after")
    def consistency(self) -> Self:
        try:
            ZoneInfo(self.zone)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("unknown IANA planning zone") from exc
        if {g.sport for g in self.objectives} != {"strength", "running"}:
            raise ValueError("rank objectives for both sports")
        unique((i.template for i in self.interruptions), "interrupted template")
        unique(self.preferred_weekdays, "preferred weekday")
        unique((o.support for o in self.observations), "observation support")
        if any(
            not self.history_start <= o.day < self.history_start + timedelta(days=7)
            for o in self.observations
        ):
            raise ValueError("observation outside representative week")
        return self

    def rank(self, sport: Sport) -> int:
        return min(g.rank for g in self.objectives if g.sport == sport)

    @property
    def emphasis(self) -> str:
        strength, running = self.rank("strength"), self.rank("running")
        if strength == running:
            return "balanced"
        return "strength" if strength < running else "running"


class Protection(Record):
    sport: Sport
    task: Key
    protocol: Text
    desired_direction: Literal["maintain", "improve"]


class Commitment(Record):
    sport: Sport
    role: Key
    sessions: Positive
    minimum_per_session: Positive  # Working sets for strength, elapsed seconds for running.


class DevelopingGroup(Record):
    template: Key
    movement: Key
    variation: Key
    group: Key
    burden: Literal["upper", "lower", "unclassified"] = "unclassified"
    # Omit both endpoints for fixed reps. The envelope is distinct from execution flexibility.
    rep_range: tuple[Positive, Positive] | None = None
    followup_template: Key | None = None
    set_seconds: Positive  # Approved worst-case execution allowance over this envelope.


class CoreProfile(Record):
    version: Literal["synthetic.core.v1"] = "synthetic.core.v1"
    joint: Literal["J-DEFAULT"] = "J-DEFAULT"
    groups: tuple[DevelopingGroup, ...] = ()
    easy_template: Key | None = None
    easy_followup: Key | None = None
    weekly_seconds: Positive | None = None
    daily_seconds: Positive | None = None

    @model_validator(mode="after")
    def developing_tasks(self) -> Self:
        unique((g.movement for g in self.groups), "developing movement")
        if not self.groups and not self.easy_template:
            raise ValueError("select at least one developing task")
        return self


class Block(Record):
    adaptation: CoreProfile | None = Field(default=None, exclude_if=lambda x: x is None)
    key: Key
    start: date
    phases: Annotated[tuple[Text, ...], Field(min_length=1, max_length=52)]
    templates: Annotated[tuple[Template, ...], Field(min_length=2, max_length=16)]
    protections: Annotated[tuple[Protection, ...], Field(min_length=1)]
    commitments: Annotated[tuple[Commitment, ...], Field(min_length=1)]
    spacing: tuple[Spacing, ...] = ()

    @model_validator(mode="after")
    def template_keys(self) -> Self:
        unique((t.key for t in self.templates), "session template")
        keys = {t.key for t in self.templates}
        if {t.prescription.sport for t in self.templates} != {"strength", "running"}:
            raise ValueError("hybrid baseline requires both sports")
        if any(s.first not in keys or s.second not in keys for s in self.spacing):
            raise ValueError("spacing names unknown template")
        if profile := self.adaptation:
            by_key = {t.key: t.prescription for t in self.templates}
            followups = [g.followup_template for g in profile.groups] + [profile.easy_followup]
            if any(k is not None and k not in by_key for k in followups):
                raise ValueError("restoration follow-up must name a block template")
            runs = [p for p in by_key.values() if isinstance(p, Running)]
            nominal = sum(p.duration.nominal for p in runs)
            if sum(p.duration.high for p in runs) > nominal + min(600, nominal // 10) or any(
                p.role == "long" and p.duration.high > p.duration.nominal + 600 for p in runs
            ):
                raise ValueError("initial running endpoints exceed the core exposure envelope")
            for g in profile.groups:
                p = by_key.get(g.template)
                targets = (
                    [
                        s
                        for ex in p.exercises
                        if (ex.movement, ex.variation) == (g.movement, g.variation)
                        for group in ex.groups
                        if group.kind == "working" and group.key == g.group
                        for s in group.sets
                    ]
                    if isinstance(p, Strength)
                    else []
                )
                if not targets or any(
                    s.execution_seconds > g.set_seconds
                    or s.reps.low != s.reps.high
                    or s.load.low != s.load.high
                    or (g.rep_range and not g.rep_range[0] <= s.reps.nominal <= g.rep_range[1])
                    for s in targets
                ):
                    raise ValueError(
                        "developing group requires fixed familiar targets within its envelope"
                    )
            if profile.easy_template:
                p = by_key.get(profile.easy_template)
                if (
                    not isinstance(p, Running)
                    or p.role != "easy"
                    or len(p.steps) != 1
                    or p.duration.low != p.duration.high
                ):
                    raise ValueError("easy operator requires one fixed continuous easy work step")
        return self


class ProposeBlock(Record):
    kind: Literal["propose-block"] = "propose-block"


class FamiliarWeek(Record):
    choice: Literal["hold", "strength", "running"] | None = Field(
        default=None, exclude_if=lambda x: x is None
    )
    kind: Literal["familiar-week"] = "familiar-week"
    number: Positive


class Session(Record):
    occurrence: UUID
    template: Key
    day: date
    start_utc: AwareDatetime
    prescription: Prescription

    @field_validator("start_utc")
    @classmethod
    def utc_instant(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @property
    def end(self) -> datetime:
        return self.start_utc + timedelta(seconds=self.prescription.reserved_seconds)


class Day(Record):
    day: date
    sessions: tuple[Session, ...]


class WeekRef(Record):
    number: Positive
    revision: UUID


class Candidate(Record):
    rules: FamiliarRule = RULE
    mode: Literal["synthetic-research-preview"] = "synthetic-research-preview"
    request: ProposeBlock | FamiliarWeek
    cycle: UUID
    block_key: Key
    block_revision: UUID | None  # None on initial block proposal; receipt supplies its version.
    prior_weeks: tuple[WeekRef, ...]
    days: tuple[Day, ...]
    supports: tuple[Key, ...]

"""Manual athlete attestations for the two detailed weeks of synthetic cycle A."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .planner import Exposure, Session, Slot, WeekPlan, WeekReview
from .prescriptions import RunSession, RunStep, StrengthSession

type Status = Literal["completed", "partial", "missed", "unknown"]
type Effort = Annotated[Decimal, Field(ge=0, le=10, allow_inf_nan=False)]
type Positive = Annotated[int, Field(strict=True, gt=0)]


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", revalidate_instances="always")


class WorkingSet(Frozen):
    """Ordinal within the prescribed working group. Warmups have no working ordinal."""

    ordinal: Positive
    rpe: Effort | None = None
    reps: Positive | None = None
    external_kg: Annotated[Decimal, Field(ge=0, allow_inf_nan=False)] | None = None


class Actual(Frozen):
    provenance: Literal["athlete-manual"] = "athlete-manual"
    status: Status
    # Athlete confirms movement AND equipment for this slot. Titles are never matched.
    confirmed_barbell_press: bool = False
    working_sets: tuple[WorkingSet, ...] = ()
    inferred_sets: Annotated[int, Field(strict=True, ge=0)] = 0
    manageable: bool | None = None
    run_seconds: Positive | None = None
    run_rpe: Effort | None = None
    deviation: str | None = None
    feedback: str | None = None

    @model_validator(mode="after")
    def check(self) -> Self:
        if len({s.ordinal for s in self.working_sets}) != len(self.working_sets):
            raise ValueError("each confirmed working set needs a distinct ordinal")
        if self.working_sets and not self.confirmed_barbell_press:
            raise ValueError("confirm the prescribed movement and equipment before confirming sets")
        if self.status in ("missed", "unknown") and (
            self.working_sets
            or self.inferred_sets
            or self.run_seconds
            or self.run_rpe is not None
            or self.manageable is not None
            or self.confirmed_barbell_press
        ):
            raise ValueError("a missed or unknown outcome cannot attest performance")
        return self

    def validate_slot(self, session: Session) -> None:
        p = session.prescription
        if isinstance(p, RunSession):
            if (
                self.working_sets
                or self.confirmed_barbell_press
                or self.inferred_sets
                or self.manageable is not None
            ):
                raise ValueError("press evidence requires a strength slot")
        elif self.run_seconds is not None or self.run_rpe is not None:
            raise ValueError("run evidence requires a running slot")
        elif any(s.ordinal > p.working_sets for s in self.working_sets):
            raise ValueError("working set ordinal outside the prescribed group")


class SlotOutcome(Frozen):
    slot: Slot
    elapsed: bool
    observation_id: UUID | None = None
    supersedes_id: UUID | None = None
    revision_id: UUID | None = None
    prescribed: Session | None = None
    workout_id: UUID | None = None
    occurred_at: datetime | None = None
    recorded_at: datetime | None = None
    supported: bool = True
    actual: Actual | None = None

    @property
    def status(self) -> Status:
        return self.actual.status if self.supported and self.actual else "unknown"

    def deviations(self, session: Session) -> tuple[str, ...]:
        a, p = self.actual, session.prescription
        if a is None:
            return ()
        differences = [a.deviation] if a.deviation else []
        if isinstance(p, StrengthSession):
            group = next(g for g in p.exercises[0].groups if g.kind == "working")
            for s in a.working_sets:
                if s.reps is not None and not group.reps.low <= s.reps <= group.reps.high:
                    differences.append(f"set {s.ordinal} reported {s.reps} reps")
                if (
                    s.external_kg is not None
                    and not group.external_kg.low <= s.external_kg <= group.external_kg.high
                ):
                    differences.append(f"set {s.ordinal} reported {s.external_kg} kg")
        elif a.run_seconds is not None and a.run_seconds != p.duration_seconds.nominal:
            differences.append(
                f"reported {a.run_seconds} s vs {p.duration_seconds.nominal} s planned"
            )
        if isinstance(p, RunSession) and a.run_rpe is not None:
            # Cycle A prescribes the same effort range throughout each easy run.
            if all(
                isinstance(step, RunStep) and not step.rpe.low <= a.run_rpe <= step.rpe.high
                for step in p.segments
            ):
                differences.append(f"reported run RPE {a.run_rpe} outside the prescribed range")
        return tuple(differences)

    def exposure(self, session: Session) -> Exposure:
        actual = self.actual
        if actual is None or self.status == "unknown":
            return Exposure()
        return Exposure(
            self.status == "completed"
            and self.prescribed is not None
            and self.prescribed.prescription == session.prescription
            and not self.deviations(session),
            tuple(s.rpe for s in sorted(actual.working_sets, key=lambda s: s.ordinal)),
            actual.inferred_sets,
        )


class WeeklyOutcomes(Frozen):
    as_of: datetime
    slots: tuple[SlotOutcome, ...]

    def counts(self) -> dict[Status, int]:
        counts: dict[Status, int] = dict(completed=0, partial=0, missed=0, unknown=0)
        for slot in self.slots:
            if slot.elapsed:
                counts[slot.status] += 1
        return counts

    @property
    def known_coverage(self) -> tuple[int, int]:
        counts = self.counts()
        elapsed = sum(counts.values())
        return elapsed - counts["unknown"], elapsed

    @property
    def completion_among_known(self) -> tuple[int, int]:
        known, _ = self.known_coverage
        return self.counts()["completed"], known

    def review(self, week: WeekPlan) -> WeekReview:
        by_slot = {s.slot: s for s in self.slots}
        press = (by_slot[Slot.FIRST_PRESS], by_slot[Slot.SECOND_PRESS])
        feedback = tuple(s.actual.manageable if s.actual and s.supported else None for s in press)
        return WeekReview(
            week.inputs.block.version,
            week.inputs.start,
            self.as_of,
            *(s.exposure(week.session(s.slot)) for s in press),
            False if False in feedback else (True if all(feedback) else None),
        )

"""Manual actuals for approved synthetic familiar weeks. Only reported fields are evidence."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from . import familiar as f
from .outcomes import Status
from .prescriptions import Target

type Nonnegative = Annotated[int, Field(ge=0)]
type Quantity = Annotated[Decimal, Field(ge=0, allow_inf_nan=False)]
type PartStatus = Literal["completed", "partial", "not-performed", "unknown"]


class SetExecution(f.Record):
    movement: f.Key
    variation: f.Key
    equipment: f.Key
    group: f.Key
    kind: Literal["warmup", "working"]
    ordinal: f.Positive
    status: PartStatus
    reps: Nonnegative | None = None
    kg: Quantity | None = None
    load_convention: f.LoadConvention | None = None
    achieved_rpe: f.RPE | None = None

    @property
    def key(self) -> tuple[str, str, str, str, str, int]:
        return self.movement, self.variation, self.equipment, self.group, self.kind, self.ordinal

    @model_validator(mode="after")
    def measured_fields(self) -> Self:
        if self.kg is not None and self.load_convention is None:
            raise ValueError("reported kilograms require their actual load convention")
        if self.load_convention == "bodyweight" and self.kg not in (None, 0):
            raise ValueError("bodyweight convention has zero external load")
        if self.status in ("unknown", "not-performed") and any(
            x is not None for x in (self.reps, self.kg, self.achieved_rpe)
        ):
            raise ValueError("unperformed set cannot attest actual work")
        return self


class StepExecution(f.Record):
    index: f.Positive  # One-based in the canonical expansion, including recoveries.
    purpose: Literal["warmup", "work", "recovery", "cooldown"]
    status: PartStatus
    elapsed_seconds: Nonnegative | None = None
    achieved_rpe: f.RPE | None = None

    @model_validator(mode="after")
    def measured_fields(self) -> Self:
        if self.status in ("unknown", "not-performed") and (
            self.elapsed_seconds is not None or self.achieved_rpe is not None
        ):
            raise ValueError("unperformed step cannot attest actual work")
        return self


class ManualExecution(f.Record):
    schema_version: Literal[2] = 2
    provenance: Literal["synthetic-athlete-report"] = "synthetic-athlete-report"
    status: Status
    manageable: bool | None = None
    feedback: f.Text | None = None

    @property
    def performed(self) -> bool:
        return self.status in ("completed", "partial")

    @model_validator(mode="after")
    def tolerance_requires_work(self) -> Self:
        if self.manageable is not None and not self.performed:
            raise ValueError("unperformed session cannot attest tolerance")
        return self


def _difference[T: (int, Decimal)](label: str, actual: T | None, target: Target[T]) -> list[str]:
    if actual is not None and not target.low <= actual <= target.high:
        return [f"{label} {actual} outside {target.low}–{target.high} (nominal {target.nominal})"]
    return []


def _effort(label: str, actual: Decimal | None, effort: f.Effort) -> list[str]:
    differences = _difference(f"{label} RPE", actual, effort.target)
    if actual is not None and actual > effort.cap:
        differences.append(f"{label} RPE {actual} exceeded cap {effort.cap}")
    return differences


class StrengthExecution(ManualExecution):
    sport: Literal["strength"] = "strength"
    sets: tuple[SetExecution, ...] = ()

    @model_validator(mode="after")
    def scoped_sets(self) -> Self:
        f.unique((s.key for s in self.sets), "reported set ordinal")
        if self.sets and not self.performed:
            raise ValueError("unperformed session cannot attest sets")
        return self

    def differences(self, session: f.Session) -> tuple[str, ...]:
        p = session.prescription
        if not isinstance(p, f.Strength):
            raise ValueError("strength report requires a strength occurrence")
        planned = {
            (e.movement, e.variation, e.equipment, g.key, g.kind, s.ordinal): (e, g, s)
            for e in p.exercises
            for g in e.groups
            for s in g.sets
        }
        differences = []
        for actual in self.sets:
            if actual.key not in planned:
                raise ValueError("reported set has no matching exercise, group and ordinal")
            exercise, group, target = planned[actual.key]
            label = f"{exercise.movement}/{exercise.variation}/{group.key} set {actual.ordinal}"
            if actual.status in ("partial", "not-performed"):
                differences.append(f"{label} {actual.status}")
            differences.extend(_difference(f"{label} reps", actual.reps, target.reps))
            if actual.load_convention in (None, exercise.load_convention):
                differences.extend(_difference(f"{label} kg", actual.kg, target.load))
            else:
                differences.append(
                    f"{label} load convention {actual.load_convention} vs "
                    f"{exercise.load_convention} prescribed"
                )
            differences.extend(_effort(label, actual.achieved_rpe, group.effort))
        return tuple(differences)


class RunExecution(ManualExecution):
    sport: Literal["running"] = "running"
    role: f.Key
    confirmed_outing: bool
    elapsed_seconds: Nonnegative | None = None
    moving_seconds: Nonnegative | None = None
    distance_metres: Quantity | None = None
    completed_work_repetitions: Nonnegative | None = None
    session_rpe: f.RPE | None = None
    steps: tuple[StepExecution, ...] = ()

    @model_validator(mode="after")
    def confirmed_work(self) -> Self:
        f.unique((s.index for s in self.steps), "expanded step")
        if self.confirmed_outing != self.performed:
            raise ValueError("completed or partial running requires a confirmed outing")
        if not self.performed and (
            self.steps
            or any(
                x is not None
                for x in (
                    self.elapsed_seconds,
                    self.moving_seconds,
                    self.distance_metres,
                    self.completed_work_repetitions,
                    self.session_rpe,
                )
            )
        ):
            raise ValueError("unperformed session cannot attest running measurements")
        if self.elapsed_seconds is not None and (
            (self.moving_seconds or 0) > self.elapsed_seconds
            or sum(s.elapsed_seconds or 0 for s in self.steps) > self.elapsed_seconds
        ):
            raise ValueError("reported work exceeds outing elapsed time")
        if self.completed_work_repetitions is not None and self.completed_work_repetitions < sum(
            s.purpose == "work" and s.status == "completed" for s in self.steps
        ):
            raise ValueError("count is below the explicitly completed work steps")
        return self

    def differences(self, session: f.Session) -> tuple[str, ...]:
        p = session.prescription
        if not isinstance(p, f.Running) or p.role != self.role:
            raise ValueError("running report requires the prescribed running role")
        differences = _difference("outing elapsed seconds", self.elapsed_seconds, p.duration)
        expanded = p.steps
        count = sum(s.purpose == "work" for s in expanded)
        if self.completed_work_repetitions is not None and self.completed_work_repetitions != count:
            differences.append(
                f"{self.completed_work_repetitions} work repetitions vs {count} prescribed"
            )
        for actual in self.steps:
            if actual.index > len(expanded) or expanded[actual.index - 1].purpose != actual.purpose:
                raise ValueError("reported step has no matching expanded index and purpose")
            step = expanded[actual.index - 1]
            label = f"step {actual.index} ({step.purpose})"
            if actual.status in ("partial", "not-performed"):
                differences.append(f"{label} {actual.status}")
            differences.extend(
                _difference(f"{label} seconds", actual.elapsed_seconds, step.seconds)
            )
            differences.extend(_effort(label, actual.achieved_rpe, step.effort))
        return tuple(differences)


type Execution = Annotated[StrengthExecution | RunExecution, Field(discriminator="sport")]


class Assertion(f.Record):
    id: UUID
    command_id: UUID
    supersedes_id: UUID | None
    occurred_at: datetime
    recorded_at: datetime
    effective_head: UUID
    actual: Execution

    def differences(self, session: f.Session) -> tuple[str, ...]:
        differences = self.actual.differences(session)
        if self.actual.performed and self.occurred_at != session.start_utc:
            return (
                f"Occurred {self.occurred_at.isoformat()} "
                f"vs scheduled {session.start_utc.isoformat()}",
                *differences,
            )
        return differences


class OccurrenceReview(f.Record):
    prescribed: f.Session
    elapsed: bool
    history: tuple[Assertion, ...]  # Root to effective tip, including superseded reports.

    @property
    def effective(self) -> Assertion | None:
        return self.history[-1] if self.history else None

    @property
    def status(self) -> Status:
        return self.effective.actual.status if self.effective else "unknown"

    @property
    def differences(self) -> tuple[str, ...]:
        return self.effective.differences(self.prescribed) if self.effective else ()


class WeekExecution(f.Record):
    owner: UUID
    cycle: UUID
    block_key: str
    block_revision: UUID
    week: int
    origin_revision: UUID
    calendar_head: UUID
    as_of: datetime
    sessions: tuple[OccurrenceReview, ...]

    def counts(self) -> dict[Status, int]:
        counts: dict[Status, int] = dict(completed=0, partial=0, missed=0, unknown=0)
        for s in self.sessions:
            if s.elapsed:
                counts[s.status] += 1
        return counts

    @property
    def known_coverage(self) -> Decimal | None:
        elapsed = sum(s.elapsed for s in self.sessions)
        return Decimal(elapsed - self.counts()["unknown"]) / elapsed if elapsed else None

    @property
    def completion_among_known(self) -> Decimal | None:
        counts = self.counts()
        known = counts["completed"] + counts["partial"] + counts["missed"]
        return Decimal(counts["completed"]) / known if known else None

    @property
    def reported_sets(self) -> tuple[SetExecution, ...]:
        """Effective, actually performed sets. A partially executed set can carry real reps."""
        return tuple(
            s
            for session in self.sessions
            if session.effective and isinstance(session.effective.actual, StrengthExecution)
            for s in session.effective.actual.sets
            if s.status in ("completed", "partial")
        )

    @property
    def reported_outings(self) -> tuple[RunExecution, ...]:
        return tuple(
            session.effective.actual
            for session in self.sessions
            if session.effective
            and isinstance(session.effective.actual, RunExecution)
            and session.effective.actual.confirmed_outing
        )


def _report_lines(actual: Execution) -> list[str]:
    lines = [f"  {actual.status} · {actual.provenance}"]
    if actual.manageable is not None:
        lines.append(f"  Manageable · {'yes' if actual.manageable else 'no'}")
    if actual.feedback:
        lines.append(f"  Feedback · {actual.feedback}")
    if isinstance(actual, StrengthExecution):
        for item in actual.sets:
            details = [
                f"{item.movement}/{item.variation} ({item.equipment})",
                f"{item.kind} {item.group} set {item.ordinal}",
                item.status,
            ]
            if item.reps is not None:
                details.append(f"{item.reps} reps")
            if item.kg is not None:
                details.append(f"{item.kg} kg ({item.load_convention})")
            if item.achieved_rpe is not None:
                details.append(f"set RPE {item.achieved_rpe}")
            lines.append("  " + " · ".join(details))
    elif actual.confirmed_outing:
        details = [f"Confirmed {actual.role} outing"]
        for name, value in (
            ("elapsed s", actual.elapsed_seconds),
            ("moving s", actual.moving_seconds),
            ("distance m", actual.distance_metres),
            ("session RPE", actual.session_rpe),
            ("completed work repetitions", actual.completed_work_repetitions),
        ):
            if value is not None:
                details.append(f"{name} {value}")
        lines.append("  " + " · ".join(details))
        if not actual.steps:
            lines.append("  Step-level execution unreported")
        for step in actual.steps:
            details = [f"step {step.index} ({step.purpose})", step.status]
            if step.elapsed_seconds is not None:
                details.append(f"{step.elapsed_seconds} s")
            if step.achieved_rpe is not None:
                details.append(f"step RPE {step.achieved_rpe}")
            lines.append("  " + " · ".join(details))
    return lines


def render_execution_review(review: WeekExecution) -> str:
    """Deterministic human-readable summary; each assertion retains its exact typed actuals."""
    counts = review.counts()
    elapsed = sum(counts.values())
    known = elapsed - counts["unknown"]
    working = [s for s in review.reported_sets if s.kind == "working"]
    reps = [s.reps for s in working if s.reps is not None]
    outings = review.reported_outings
    durations = [run.elapsed_seconds for run in outings if run.elapsed_seconds is not None]
    coverage = f"{known}/{elapsed}" if elapsed else "unknown (no elapsed sessions)"
    completion = f"{counts['completed']}/{known}" if known else "unknown (no known outcomes)"
    lines = [
        f"Synthetic execution · {review.block_key} week {review.week} · {review.as_of.isoformat()}",
        f"Origin {review.origin_revision} · calendar head {review.calendar_head}",
        f"Elapsed {elapsed} · upcoming {len(review.sessions) - elapsed} · "
        + " · ".join(f"{k} {v}" for k, v in counts.items()),
        f"Known coverage {coverage} · completed among known {completion}",
        f"Reported strength · {len(working)} working sets with actual work "
        f"({sum(s.status == 'partial' for s in working)} partial) · "
        f"{sum(reps) if reps else 'unknown'} reps reported across {len(reps)} sets",
        f"Reported running · {len(outings)} confirmed outings · "
        f"{sum(durations) if durations else 'unknown'} elapsed seconds "
        f"across {len(durations)} outings",
        "Comparable outcome direction · unassessed",
    ]
    for occurrence in review.sessions:
        session = occurrence.prescribed
        lines.append(
            f"{session.day} {session.template} {session.occurrence} · "
            f"{occurrence.status if occurrence.elapsed else 'upcoming'}"
        )
        for report in occurrence.history:
            label = "effective" if report == occurrence.effective else "superseded"
            lines.append(
                f"  {label} {report.id} · occurred {report.occurred_at.isoformat()} · "
                f"recorded {report.recorded_at.isoformat()} · head {report.effective_head}"
            )
            lines.extend(_report_lines(report.actual))
            lines.extend(f"  {difference}" for difference in report.differences(session))
    return "\n".join(lines)

"""Owner-scoped execution reads and writes. PlanCommands acquires the owner and cycle locks."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, aliased

from fitness_intelligence.planning.outcomes import Actual, SlotOutcome, WeeklyOutcomes
from fitness_intelligence.planning.planner import Slot, WeekPlan

from .models import ExternalReference, Workout
from .plan_models import PlanRevision, SessionOutcome
from .plan_snapshot import CANDIDATE, calendar, read


class OutcomeConflict(ValueError):
    """An execution, correction or command conflicts with existing history."""


def _latest(owner: UUID) -> Select[tuple[SessionOutcome]]:
    successor = aliased(SessionOutcome)
    return select(SessionOutcome).where(
        SessionOutcome.user_id == owner,
        ~select(successor.id)
        .where(successor.user_id == owner, successor.supersedes_id == SessionOutcome.id)
        .exists(),
    )


def _workout(db: Session, owner: UUID, workout_id: UUID, occurred: datetime) -> bool:
    # Lock the parent against deletion, edits and new references, then its current references.
    workout = db.execute(
        select(Workout.started_at, Workout.deleted_at)
        .where(Workout.user_id == owner, Workout.id == workout_id)
        .with_for_update()
    ).one()
    references = db.scalars(
        select(ExternalReference.source_deleted_at)
        .where(ExternalReference.user_id == owner, ExternalReference.workout_id == workout_id)
        .with_for_update(read=True)
    ).all()
    return (
        workout.started_at == occurred
        and workout.deleted_at is None
        and (not references or None in references)
    )


def record(
    db: Session,
    owner: UUID,
    plan: UUID,
    revision: UUID,
    week: int,
    slot: Slot,
    actual: Actual,
    occurred: datetime,
    now: datetime,
    command: UUID,
    supersedes: UUID | None,
    workout: UUID | None,
) -> UUID:
    if occurred.utcoffset() is None or occurred > now:
        raise ValueError("observation requires an elapsed aware instant")
    actual = Actual.model_validate(actual)
    payload = actual.model_dump(mode="json")
    existing = db.scalar(
        select(SessionOutcome).where(
            SessionOutcome.user_id == owner, SessionOutcome.command_id == command
        )
    )
    if existing:
        if (
            existing.plan_id,
            existing.revision_id,
            existing.week,
            existing.slot,
            existing.actual,
            existing.occurred_at,
            existing.supersedes_id,
            existing.workout_id,
        ) != (plan, revision, week, slot, payload, occurred, supersedes, workout):
            raise OutcomeConflict("outcome command already used for different intent")
        return existing.id

    effective = db.scalar(select(func.e3_effective_revision(owner, plan, occurred)))
    if effective != revision:
        raise OutcomeConflict("prescription was not in force at the observation instant")
    raw = db.scalars(
        select(PlanRevision.snapshot).where(
            PlanRevision.user_id == owner, PlanRevision.plan_id == plan, PlanRevision.id == revision
        )
    ).one()
    head = read(CANDIDATE, raw).week
    session = calendar(head).get((week, slot))
    if session is None:
        raise ValueError("unknown prescription slot")
    zone = head.inputs.availability.zone
    start = head.inputs.block.start + timedelta(weeks=week - 1)
    if not start <= occurred.astimezone(zone).date() < start + timedelta(weeks=1):
        raise ValueError("execution must be attributed within its planning week")
    if actual.status in ("missed", "unknown") and occurred != datetime.combine(
        session.day, session.start, zone
    ):
        raise ValueError("use the scheduled instant for an unperformed slot")
    actual.validate_slot(session)
    current = db.scalar(
        _latest(owner).where(
            SessionOutcome.plan_id == plan, SessionOutcome.week == week, SessionOutcome.slot == slot
        )
    )
    if (current.id if current else None) != supersedes:
        raise OutcomeConflict("correction must identify the current slot observation")
    if workout is not None:
        if actual.status in ("missed", "unknown") or not _workout(db, owner, workout, occurred):
            raise OutcomeConflict("workout does not support this execution")
    if actual.status in ("completed", "partial"):
        duplicate = SessionOutcome.occurred_at == occurred
        if workout is not None:
            duplicate = or_(duplicate, SessionOutcome.workout_id == workout)
        if (
            db.scalar(
                _latest(owner).where(
                    duplicate,
                    SessionOutcome.actual["status"].as_string().in_(("completed", "partial")),
                    SessionOutcome.id.is_distinct_from(supersedes),
                )
            )
            is not None
        ):
            raise OutcomeConflict("execution already attributed to an active observation")
    row = SessionOutcome(
        user_id=owner,
        plan_id=plan,
        revision_id=revision,
        week=week,
        slot=slot,
        occurred_at=occurred,
        recorded_at=now,
        command_id=command,
        supersedes_id=supersedes,
        workout_id=workout,
        actual=payload,
    )
    db.add(row)
    db.flush()
    return row.id


def week_outcomes(
    db: Session, owner: UUID, plan: UUID, week: WeekPlan, as_of: datetime
) -> WeeklyOutcomes:
    rows = {
        row.slot: row
        for row in db.scalars(
            _latest(owner).where(
                SessionOutcome.plan_id == plan, SessionOutcome.week == week.inputs.number
            )
        )
    }
    prescriptions = {
        revision: calendar(read(CANDIDATE, raw).week)
        for revision, raw in db.execute(
            select(PlanRevision.id, PlanRevision.snapshot).where(
                PlanRevision.user_id == owner,
                PlanRevision.plan_id == plan,
                PlanRevision.id.in_({row.revision_id for row in rows.values()}),
            )
        )
    }
    slots = []
    for slot in Slot:
        s = week.session(slot)
        scheduled = datetime.combine(s.day, s.start, week.inputs.availability.zone)
        row = rows.get(slot)
        if row is None:
            slots.append(SlotOutcome(slot=slot, elapsed=scheduled <= as_of))
            continue
        supported = row.workout_id is None or _workout(db, owner, row.workout_id, row.occurred_at)
        slots.append(
            SlotOutcome(
                slot=slot,
                elapsed=True,
                observation_id=row.id,
                supersedes_id=row.supersedes_id,
                revision_id=row.revision_id,
                prescribed=prescriptions[row.revision_id][row.week, slot],
                workout_id=row.workout_id,
                occurred_at=row.occurred_at.astimezone(UTC),
                recorded_at=row.recorded_at.astimezone(UTC),
                actual=Actual.model_validate(row.actual),
                supported=supported,
            )
        )
    return WeeklyOutcomes(as_of=as_of, slots=tuple(slots))

"""Owner-scoped execution reads and writes. PlanCommands acquires the owner and cycle locks."""

from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import TypeAdapter
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, aliased

from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning import familiar_outcomes as fo
from fitness_intelligence.planning.outcomes import Actual, SlotOutcome, WeeklyOutcomes
from fitness_intelligence.planning.planner import Slot, WeekPlan

from . import familiar_snapshot as v2
from .models import ExternalReference, Workout
from .plan_models import AthleteContext, PlanRevision, SessionOutcome
from .plan_snapshot import CANDIDATE, calendar, canonical, read


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


def _legacy_attribution(
    db: Session,
    owner: UUID,
    plan: UUID,
    revision: UUID,
    week: int,
    slot: Slot,
    actual: Actual,
    occurred: datetime,
) -> None:
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


def _familiar_week(
    db: Session, owner: UUID, plan: UUID, head: UUID, number: int
) -> tuple[UUID, f.Candidate, ZoneInfo]:
    """Resolve the originating revision from the effective head's sealed, flat calendar."""

    def revision(key: UUID) -> PlanRevision:
        return db.scalars(
            select(PlanRevision).where(
                PlanRevision.user_id == owner, PlanRevision.plan_id == plan, PlanRevision.id == key
            )
        ).one()

    row = revision(head)
    effective = v2.read(f.Candidate, row.snapshot)
    if not isinstance(effective.request, f.FamiliarWeek):
        raise OutcomeConflict("week has no approved prescription in the effective calendar")
    candidate = effective
    if effective.request.number != number:
        ref = next((r for r in effective.prior_weeks if r.number == number), None)
        if ref is None:
            raise OutcomeConflict("week has no approved prescription in the effective calendar")
        row = revision(ref.revision)
        candidate = v2.read(f.Candidate, row.snapshot)
    if (
        candidate.cycle != plan
        or candidate.block_revision != effective.block_revision
        or candidate.block_revision is None
        or candidate.block_key != effective.block_key
        or not isinstance(candidate.request, f.FamiliarWeek)
        or candidate.request.number != number
    ):
        raise OutcomeConflict("invalid originating prescription reference")
    raw = db.scalars(
        select(AthleteContext.snapshot).where(
            AthleteContext.user_id == owner, AthleteContext.id == row.context_id
        )
    ).one()
    return row.id, candidate, ZoneInfo(v2.read(f.Context, raw).zone)


def _familiar_attribution(
    db: Session,
    owner: UUID,
    plan: UUID,
    effective: UUID,
    origin: UUID,
    week: int,
    occurrence: UUID,
    actual: fo.Execution,
    occurred: datetime,
) -> None:
    resolved, candidate, zone = _familiar_week(db, owner, plan, effective, week)
    if resolved != origin:
        raise OutcomeConflict("originating week revision differs from the effective calendar")
    session = next(
        (s for d in candidate.days for s in d.sessions if s.occurrence == occurrence), None
    )
    if session is None:
        raise OutcomeConflict("unknown logical occurrence in originating week")
    if not candidate.days[0].day <= occurred.astimezone(zone).date() <= candidate.days[-1].day:
        raise ValueError("execution must be attributed within its planning week")
    if not actual.performed and occurred != session.start_utc:
        raise ValueError("use the scheduled instant for an unperformed occurrence")
    actual.differences(session)  # Validate identity while accepting performed work outside targets.


def record(
    db: Session,
    owner: UUID,
    plan: UUID,
    revision: UUID,
    week: int,
    slot: Slot | UUID,
    actual: Actual | fo.Execution,
    occurred: datetime,
    now: datetime,
    command: UUID,
    supersedes: UUID | None,
    workout: UUID | None,
) -> UUID:
    if occurred.utcoffset() is None:
        raise ValueError("observation requires an elapsed aware instant")
    occurred = occurred.astimezone(UTC)
    if occurred > now:
        raise ValueError("observation requires an elapsed aware instant")
    if type(week) is not int or week < 1:
        raise ValueError("expected a positive week number")
    actual = type(actual).model_validate(actual)
    generalized = isinstance(slot, UUID)
    slot_key = str(slot)
    payload = actual.model_dump(mode="json")
    existing = db.scalar(
        select(SessionOutcome).where(
            SessionOutcome.user_id == owner, SessionOutcome.command_id == command
        )
    )
    if existing:
        if (
            existing.plan_id,
            existing.origin_revision_id if generalized else existing.revision_id,
            existing.week,
            existing.slot,
            existing.actual,
            existing.occurred_at,
            existing.supersedes_id,
            existing.workout_id,
        ) != (plan, revision, week, slot_key, payload, occurred, supersedes, workout):
            raise OutcomeConflict("outcome command already used for different intent")
        return existing.id

    effective = db.scalar(select(func.e3_effective_revision(owner, plan, occurred)))
    if effective is None:
        raise OutcomeConflict("prescription was not in force at the observation instant")
    if isinstance(slot, UUID) and isinstance(actual, (fo.StrengthExecution, fo.RunExecution)):
        _familiar_attribution(db, owner, plan, effective, revision, week, slot, actual, occurred)
    elif isinstance(slot, Slot) and isinstance(actual, Actual):
        if effective != revision:
            raise OutcomeConflict("prescription was not in force at the observation instant")
        _legacy_attribution(db, owner, plan, revision, week, slot, actual, occurred)
    else:
        raise ValueError("execution family differs from slot type")
    current = db.scalar(
        _latest(owner).where(
            SessionOutcome.plan_id == plan,
            SessionOutcome.week == week,
            SessionOutcome.slot == slot_key,
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
        revision_id=effective,
        outcome_version=2 if generalized else 1,
        origin_revision_id=revision if generalized else None,
        week=week,
        slot=slot_key,
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


_EXECUTION = TypeAdapter(fo.Execution)


def familiar_assertion(row: SessionOutcome) -> fo.Assertion:
    return fo.Assertion(
        id=row.id,
        command_id=row.command_id,
        supersedes_id=row.supersedes_id,
        occurred_at=row.occurred_at.astimezone(UTC),
        recorded_at=row.recorded_at.astimezone(UTC),
        effective_head=row.revision_id,
        actual=_EXECUTION.validate_json(canonical(row.actual)),
    )


def familiar_week_outcomes(
    db: Session, owner: UUID, plan: UUID, week: int, as_of: datetime
) -> fo.WeekExecution:
    head = db.scalar(select(func.e3_effective_revision(owner, plan, as_of)))
    if head is None or type(week) is not int or week < 1:
        raise OutcomeConflict("week has no approved prescription at review time")
    origin, candidate, _ = _familiar_week(db, owner, plan, head, week)
    rows = db.scalars(
        select(SessionOutcome).where(
            SessionOutcome.user_id == owner,
            SessionOutcome.plan_id == plan,
            SessionOutcome.outcome_version == 2,
            SessionOutcome.origin_revision_id == origin,
            SessionOutcome.week == week,
            SessionOutcome.recorded_at <= as_of,
        )
    )
    # Follow explicit successors. Recording instants can tie during a rehearsal.
    chains: dict[str, dict[UUID | None, fo.Assertion]] = {}
    for row in rows:
        assertion = familiar_assertion(row)
        chains.setdefault(row.slot, {})[row.supersedes_id] = assertion
    sessions = []
    for day in candidate.days:
        for session in day.sessions:
            chain = chains.get(str(session.occurrence), {})
            history = []
            assertion = chain.get(None)
            while assertion is not None:
                history.append(assertion)
                assertion = chain.get(assertion.id)
            sessions.append(
                fo.OccurrenceReview(
                    prescribed=session,
                    elapsed=bool(history) or session.start_utc <= as_of,
                    history=tuple(history),
                )
            )
    assert candidate.block_revision is not None
    return fo.WeekExecution(
        owner=owner,
        cycle=plan,
        block_key=candidate.block_key,
        block_revision=candidate.block_revision,
        week=week,
        origin_revision=origin,
        calendar_head=head,
        as_of=as_of,
        sessions=tuple(sessions),
    )

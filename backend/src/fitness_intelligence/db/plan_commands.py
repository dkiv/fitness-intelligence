"""Internal commands. The operator binds the owner outside the request, before opening a session.

Call within a short Session.begin() transaction. The caller owns commit and rollback.
"""

import os
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fitness_intelligence.planning.planner import (
    RULES,
    Conflicts,
    Slot,
    WeekInputs,
    WeekPlan,
    generate_week,
    propose_move,
)
from fitness_intelligence.planning.planner import Session as PlannedSession
from fitness_intelligence.planning.press_block import PressBlock

from .models import User
from .plan_models import AthleteContext, PlanDecision, PlanRevision, TrainingPlan
from .plan_snapshot import (
    BLOCK,
    CANDIDATE,
    CONTEXT,
    Candidate,
    EvidenceRef,
    Generate,
    InvalidSnapshot,
    Move,
    PlanningContext,
    calendar,
    canonical,
    read,
    snapshot,
)


class StalePlan(ValueError):
    """The expected head, context, or effective schedule changed."""


class DecisionConflict(ValueError):
    """The receipt or terminal decision already belongs to another intent."""


class InfeasiblePlan(ValueError):
    def __init__(self, result: Conflicts) -> None:
        self.conflicts = result
        super().__init__("proposal violates planner constraints")


type Choice = Literal["approve", "decline"]


@dataclass(frozen=True)
class SlotChange:
    week: int
    slot: Slot
    before: PlannedSession | None
    after: PlannedSession | None


@dataclass(frozen=True)
class Receipt:
    revision_id: UUID
    choice: str
    command_id: UUID
    decided_at: datetime
    reason: str | None


@dataclass(frozen=True)
class Preview:
    revision_id: UUID
    base_id: UUID | None
    head_id: UUID | None
    context_id: UUID
    current_context_id: UUID
    current_context: PlanningContext
    candidate: Candidate
    changes: tuple[SlotChange, ...]
    decision: Receipt | None


def _changes(before: WeekPlan | None, after: WeekPlan) -> tuple[SlotChange, ...]:
    old, new = calendar(before), calendar(after)
    return tuple(
        SlotChange(*key, old.get(key), new.get(key))
        for key in sorted(old.keys() | new.keys())
        if old.get(key) != new.get(key)
    )


def _generate(
    request: Generate | Move, context: PlanningContext, block: PressBlock, base: WeekPlan | None
) -> WeekPlan:
    if base and context.availability.zone != base.inputs.availability.zone:
        raise StalePlan("a cycle must retain its approved planning zone")
    if isinstance(request, Move):
        if base is None:
            raise ValueError("a move requires an approved week")
        if base.inputs.number == 2 and context.review != base.inputs.review:
            raise StalePlan("regenerate with the updated feedback before moving this slot")
        result = propose_move(base, context.availability, request.slot, request.day, request.start)
    else:
        if base and request.number < base.inputs.number:
            raise ValueError("only the latest detailed week can be revised")
        previous = None
        if request.number == 2:
            if base is None:
                raise ValueError("week two requires an approved first week")
            previous = base if base.inputs.number == 1 else base.inputs.previous
        result = generate_week(
            WeekInputs(
                block,
                context.availability,
                request.number,
                previous,
                context.review if request.number == 2 else None,
                request.thursday,
            )
        )
    if isinstance(result, Conflicts):
        raise InfeasiblePlan(result)
    return result


def _effective_dates(before: WeekPlan | None, after: WeekPlan, today: date) -> None:
    for change in _changes(before, after):
        for session in (change.before, change.after):
            if session and session.day <= today:
                raise StalePlan("a changed session's local day has already started")

    prior = after.inputs.previous
    if prior is None or prior.days[-1].day < today:
        return
    # Week two retains the entire first prescription. A change to a still-relevant first-week
    # constraint needs a fresh first-week review before adding another week.
    old, new = prior.inputs.availability, after.inputs.availability
    boundary = after.inputs.start
    relevant_days = (prior.inputs.start + timedelta(days=i) for i in range(8))
    if (
        old.equipment != new.equipment
        or old.excluded_movements != new.excluded_movements
        or any(old.window(d) != new.window(d) for d in relevant_days if today <= d <= boundary)
    ):
        raise StalePlan("a retained week's constraints changed")


class PlanCommands:
    def __init__(self, session: Session) -> None:
        binding = os.environ.get("FITNESS_PLANNING_OWNER_ID")
        if not binding:
            raise PermissionError("trusted local planning owner binding required")
        self._owner = UUID(binding)
        self._db = session

    def _lock_owner(self) -> None:
        self._db.execute(select(User.id).where(User.id == self._owner).with_for_update()).one()

    def _context(self) -> AthleteContext | None:
        return self._db.scalar(
            select(AthleteContext)
            .where(AthleteContext.user_id == self._owner)
            .order_by(AthleteContext.sequence.desc())
            .limit(1)
        )

    def capture_context(self, context: PlanningContext, *, expected_context: UUID | None) -> UUID:
        self._lock_owner()
        old = self._context()
        if (old.id if old else None) != expected_context:
            raise StalePlan("context revision changed")
        payload = snapshot(context)
        read(CONTEXT, payload)
        row = AthleteContext(
            user_id=self._owner, sequence=old.sequence + 1 if old else 1, snapshot=payload
        )
        self._db.add(row)
        self._db.flush()
        return row.id

    def create_cycle(self, block: PressBlock) -> UUID:
        self._lock_owner()
        payload = snapshot(block)
        read(BLOCK, payload)
        row = TrainingPlan(user_id=self._owner, block=payload)
        self._db.add(row)
        self._db.flush()
        return row.id

    def _plan(self, plan_id: UUID, *, lock: bool) -> TrainingPlan:
        stmt = select(TrainingPlan).where(
            TrainingPlan.user_id == self._owner, TrainingPlan.id == plan_id
        )
        if lock:
            stmt = stmt.with_for_update()
        return self._db.scalars(stmt.execution_options(populate_existing=True)).one()

    def _revision(self, plan_id: UUID, revision_id: UUID) -> PlanRevision:
        return self._db.scalars(
            select(PlanRevision).where(
                PlanRevision.user_id == self._owner,
                PlanRevision.plan_id == plan_id,
                PlanRevision.id == revision_id,
            )
        ).one()

    def _base(self, plan_id: UUID, base_id: UUID | None) -> WeekPlan | None:
        if base_id is None:
            return None
        return read(CANDIDATE, self._revision(plan_id, base_id).snapshot).week

    def _today(self, context: PlanningContext) -> date:
        now = self._db.execute(select(func.clock_timestamp())).scalar_one()
        return now.astimezone(context.availability.zone).date()

    def submit(
        self,
        plan_id: UUID,
        expected_head: UUID | None,
        request: Generate | Move,
        *,
        evidence: tuple[EvidenceRef, ...] = (),
    ) -> UUID:
        self._lock_owner()
        plan = self._plan(plan_id, lock=True)
        if expected_head != plan.head_id:
            raise StalePlan("approved head changed")
        ctx = self._context()
        if ctx is None:
            raise ValueError("capture the planning context first")
        context = read(CONTEXT, ctx.snapshot)
        base = self._base(plan.id, expected_head)
        week = _generate(request, context, read(BLOCK, plan.block), base)
        _effective_dates(base, week, self._today(context))
        payload = snapshot(Candidate(request, week, evidence))
        read(CANDIDATE, payload)
        revision = PlanRevision(
            user_id=self._owner,
            plan_id=plan.id,
            base_id=expected_head,
            context_id=ctx.id,
            snapshot=payload,
        )
        self._db.add(revision)
        self._db.flush()
        return revision.id

    def _decision(self, plan_id: UUID, revision_id: UUID) -> PlanDecision | None:
        return self._db.scalar(
            select(PlanDecision).where(
                PlanDecision.user_id == self._owner,
                PlanDecision.plan_id == plan_id,
                PlanDecision.revision_id == revision_id,
            )
        )

    @staticmethod
    def _receipt(row: PlanDecision) -> Receipt:
        return Receipt(
            row.revision_id, row.choice, row.command_id, row.decided_at.astimezone(UTC), row.reason
        )

    def preview(self, plan_id: UUID, revision_id: UUID) -> Preview:
        self._lock_owner()
        return self._preview(self._plan(plan_id, lock=False), revision_id)

    def _preview(self, plan: TrainingPlan, revision_id: UUID) -> Preview:
        revision = self._revision(plan.id, revision_id)
        candidate = read(CANDIDATE, revision.snapshot)
        ctx = self._context()
        assert ctx is not None
        decision = self._decision(plan.id, revision_id)
        return Preview(
            revision_id,
            revision.base_id,
            plan.head_id,
            revision.context_id,
            ctx.id,
            read(CONTEXT, ctx.snapshot),
            candidate,
            _changes(self._base(plan.id, revision.base_id), candidate.week),
            self._receipt(decision) if decision else None,
        )

    def current(self, plan_id: UUID) -> Preview | None:
        self._lock_owner()
        plan = self._plan(plan_id, lock=False)
        return self._preview(plan, plan.head_id) if plan.head_id else None

    def decide(
        self,
        plan_id: UUID,
        revision_id: UUID,
        *,
        expected_head: UUID | None,
        choice: Choice,
        command_id: UUID,
        reason: str | None = None,
    ) -> Receipt:
        if choice not in ("approve", "decline"):
            raise ValueError("unknown decision")
        self._lock_owner()
        plan = self._plan(plan_id, lock=True)
        revision = self._revision(plan.id, revision_id)
        existing = self._db.scalar(
            select(PlanDecision).where(
                PlanDecision.user_id == self._owner, PlanDecision.command_id == command_id
            )
        )
        if existing:
            if (
                existing.plan_id,
                existing.revision_id,
                revision.base_id,
                existing.choice,
                existing.reason,
            ) != (plan_id, revision_id, expected_head, choice, reason):
                raise DecisionConflict("command ID already used for different intent")
            return self._receipt(existing)
        if self._decision(plan_id, revision_id):
            raise DecisionConflict("candidate already decided")
        if expected_head != revision.base_id or expected_head != plan.head_id:
            raise StalePlan("approved head changed")
        if choice == "approve":
            ctx = self._context()
            if ctx is None or ctx.id != revision.context_id:
                raise StalePlan("planning context changed")
            context = read(CONTEXT, ctx.snapshot)
            base = self._base(plan_id, expected_head)
            candidate = read(CANDIDATE, revision.snapshot)
            if candidate.week.rule_version != RULES:
                raise StalePlan("planner rule version changed")
            week = _generate(candidate.request, context, read(BLOCK, plan.block), base)
            if canonical(
                snapshot(Candidate(candidate.request, week, candidate.evidence))
            ) != canonical(revision.snapshot):
                raise InvalidSnapshot("stored prescription differs from planner output")
            _effective_dates(base, week, self._today(context))
        row = PlanDecision(
            user_id=self._owner,
            plan_id=plan.id,
            revision_id=revision_id,
            choice=choice,
            command_id=command_id,
            reason=reason,
        )
        self._db.add(row)
        self._db.flush()  # PostgreSQL advances the approved head in this statement.
        self._db.expire(plan)
        return self._receipt(row)

"""Internal commands. The operator binds the owner outside the request, before opening a session.

Call within a short Session.begin() transaction. The caller owns commit and rollback.
"""

import json
import os
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning import rationale
from fitness_intelligence.planning.familiar_calendar import validate_retained
from fitness_intelligence.planning.outcomes import Actual, WeeklyOutcomes
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
from fitness_intelligence.planning.rationale import Rationale

from . import execution
from . import familiar_snapshot as v2
from .models import User
from .plan_models import AthleteContext, PlanDecision, PlanRevision, SessionOutcome, TrainingPlan
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
        details = []
        for finding in result.findings:
            facts = ", ".join(f"{key}={value}" for key, value in finding.facts)
            details.append(f"{finding.rule} ({', '.join(finding.slots)}) · {facts}")
        super().__init__("\n".join(details))


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
    rationale: Rationale | None
    evidence_alerts: tuple[str, ...]


@dataclass(frozen=True)
class FamiliarPreview:
    revision_id: UUID
    base_id: UUID | None
    head_id: UUID | None
    context_id: UUID
    current_context_id: UUID
    sealed_context: f.Context
    block: f.Block
    candidate: f.Candidate
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
        if base.inputs.number == 2:
            original = base.inputs.review
            review = context.review
            if (
                review is None
                or original is None
                or replace(review, as_of=original.as_of) != original
            ):
                raise StalePlan("regenerate with the updated feedback before moving this slot")
            base = replace(base, inputs=replace(base.inputs, review=review))
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

    def capture_context(
        self, context: PlanningContext | f.Context, *, expected_context: UUID | None
    ) -> UUID:
        self._lock_owner()
        old = self._context()
        if (old.id if old else None) != expected_context:
            raise StalePlan("context revision changed")
        if isinstance(context, f.Context):
            v2.require_preview_owner(self._owner)
            payload = v2.snapshot(context)
            sealed = v2.read(f.Context, payload)
            today = self._now().astimezone(ZoneInfo(sealed.zone)).date()
            if sealed.history_start + timedelta(days=7) > today:
                raise ValueError("representative history week must be complete at capture")
        else:
            if self._owner == v2.PREVIEW_OWNER:
                raise PermissionError("dedicated generalized preview owner")
            payload = snapshot(context)
            read(CONTEXT, payload)
        row = AthleteContext(
            user_id=self._owner, sequence=old.sequence + 1 if old else 1, snapshot=payload
        )
        self._db.add(row)
        self._db.flush()
        return row.id

    def create_cycle(self, block: PressBlock | f.Block) -> UUID:
        self._lock_owner()
        if isinstance(block, f.Block):
            v2.require_preview_owner(self._owner)
            payload = v2.snapshot(block)
            v2.read(f.Block, payload)
        else:
            if self._owner == v2.PREVIEW_OWNER:
                raise PermissionError("dedicated generalized preview owner")
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
        plan = self._db.scalars(stmt.execution_options(populate_existing=True)).one()
        version = plan.block.get("schema_version")
        if type(version) is not int or version not in (1, 2):
            raise InvalidSnapshot("unsupported cycle schema version")
        if version == 2:
            v2.require_preview_owner(self._owner)
        return plan

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

    def _now(self) -> datetime:
        return self._db.execute(select(func.clock_timestamp())).scalar_one().astimezone(UTC)

    def _today(self, context: PlanningContext) -> date:
        return self._now().astimezone(context.availability.zone).date()

    def record_outcome(
        self,
        plan_id: UUID,
        revision_id: UUID,
        week: int,
        slot: Slot,
        actual: Actual,
        *,
        occurred_at: datetime,
        command_id: UUID,
        supersedes_id: UUID | None = None,
        workout_id: UUID | None = None,
    ) -> UUID:
        self._lock_owner()
        plan = self._plan(plan_id, lock=True)
        if plan.block.get("schema_version") != 1:
            raise ValueError("generalized execution attribution is unsupported")
        return execution.record(
            self._db,
            self._owner,
            plan_id,
            revision_id,
            week,
            slot,
            actual,
            occurred_at,
            self._now(),
            command_id,
            supersedes_id,
            workout_id,
        )

    def weekly_review(self, plan_id: UUID, week: int) -> WeeklyOutcomes:
        """Current observations across revisions, against the approved logical week."""
        self._lock_owner()
        plan = self._plan(plan_id, lock=True)
        if plan.block.get("schema_version") != 1:
            raise ValueError("generalized execution review is unsupported")
        current = self._base(plan_id, plan.head_id)
        if current and current.inputs.number != week:
            current = current.inputs.previous
        if current is None or current.inputs.number != week:
            raise ValueError("week has no approved prescription")
        return execution.week_outcomes(self._db, self._owner, plan_id, current, self._now())

    def _outcomes(
        self, plan_id: UUID, request: Generate | Move, base: WeekPlan | None, as_of: datetime
    ) -> WeeklyOutcomes | None:
        number = (
            request.number if isinstance(request, Generate) else (base.inputs.number if base else 1)
        )
        if number != 2 or base is None:
            return None
        prior = base if base.inputs.number == 1 else base.inputs.previous
        assert prior is not None
        return execution.week_outcomes(self._db, self._owner, plan_id, prior, as_of)

    def _review_context(
        self, context: PlanningContext, outcomes: WeeklyOutcomes | None, base: WeekPlan | None
    ) -> PlanningContext:
        review = None
        if outcomes and base:
            prior = base if base.inputs.number == 1 else base.inputs.previous
            assert prior is not None
            review = outcomes.review(prior)
        return replace(context, review=review)

    def _check_recorded_slots(self, plan_id: UUID, base: WeekPlan | None, week: WeekPlan) -> None:
        # An athlete may explicitly perform a future slot early within the week.
        recorded = set(
            self._db.execute(
                select(SessionOutcome.week, SessionOutcome.slot).where(
                    SessionOutcome.user_id == self._owner, SessionOutcome.plan_id == plan_id
                )
            )
        )
        if any((c.week, c.slot) in recorded for c in _changes(base, week)):
            raise StalePlan("a changed slot already has execution history")

    def citing(self, claim_revision: str) -> tuple[UUID, ...]:
        """Owner-scoped historical and pending E3 proposals citing an exact claim revision."""
        self._lock_owner()
        rows = self._db.execute(
            select(PlanRevision.id, PlanRevision.rationale)
            .where(PlanRevision.user_id == self._owner, PlanRevision.rationale.is_not(None))
            .order_by(PlanRevision.id)
        )
        return tuple(
            key
            for key, raw in rows
            if raw and Rationale.model_validate_json(json.dumps(raw)).cites_claim(claim_revision)
        )

    def _familiar_candidate(
        self,
        plan: TrainingPlan,
        base_id: UUID | None,
        ctx: AthleteContext,
        request: f.ProposeBlock | f.FamiliarWeek,
        *,
        today: date | None,
        rule: f.FamiliarRule = f.RULE,
    ) -> f.Candidate:
        v2.require_preview_owner(self._owner)
        block = v2.read(f.Block, plan.block)
        context = v2.read(f.Context, ctx.snapshot)
        block_revision = None
        weeks: list[v2.ApprovedWeek] = []
        if base_id is not None:
            base = self._revision(plan.id, base_id)
            head = v2.read(f.Candidate, base.snapshot)
            block_revision = head.block_revision or base.id
            opening = self._revision(plan.id, block_revision)
            initial = self._familiar_context(opening.context_id)
            if (initial.zone, initial.objectives, initial.history_start, initial.observations) != (
                context.zone,
                context.objectives,
                context.history_start,
                context.observations,
            ):
                raise StalePlan("block objectives, planning zone or initial baseline changed")
            for ref in head.prior_weeks:
                previous = self._revision(plan.id, ref.revision)
                known = v2.read(f.Candidate, previous.snapshot)
                weeks.append(v2.ApprovedWeek(ref, known.days))
            if isinstance(head.request, f.FamiliarWeek):
                weeks.append(
                    v2.ApprovedWeek(
                        f.WeekRef(number=head.request.number, revision=base.id), head.days
                    )
                )
            if today is not None and base.context_id != ctx.id:
                for week in weeks:
                    try:
                        validate_retained(
                            plan.id, block, context, week.ref.number, week.days, today
                        )
                    except ValueError as exc:
                        raise StalePlan(str(exc)) from exc
        candidate = v2.build(
            plan.id, block, context, request, block_revision, tuple(weeks), rule=rule
        )
        if today is not None:
            try:
                v2.check_dates(candidate, block, today)
            except ValueError as exc:
                raise StalePlan(str(exc)) from exc
        return candidate

    def replay_familiar(self, plan_id: UUID, revision_id: UUID) -> f.Candidate:
        """Regenerate from the sealed context and original approved base."""
        self._lock_owner()
        plan = self._plan(plan_id, lock=False)
        revision = self._revision(plan_id, revision_id)
        saved = v2.read(f.Candidate, revision.snapshot)
        ctx = self._db.scalars(
            select(AthleteContext).where(
                AthleteContext.id == revision.context_id, AthleteContext.user_id == self._owner
            )
        ).one()
        replay = self._familiar_candidate(
            plan, revision.base_id, ctx, saved.request, today=None, rule=saved.rules
        )
        if canonical(v2.snapshot(replay)) != canonical(revision.snapshot):
            raise InvalidSnapshot("generalized historical replay mismatch")
        return replay

    def _familiar_context(self, context_id: UUID) -> f.Context:
        row = self._db.scalars(
            select(AthleteContext).where(
                AthleteContext.user_id == self._owner, AthleteContext.id == context_id
            )
        ).one()
        return v2.read(f.Context, row.snapshot)

    def submit(
        self,
        plan_id: UUID,
        expected_head: UUID | None,
        request: Generate | Move | f.ProposeBlock | f.FamiliarWeek,
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
        if evidence:
            raise ValueError("scientific references must come from catalog retrieval")
        if plan.block.get("schema_version") == 2:
            if not isinstance(request, (f.ProposeBlock, f.FamiliarWeek)):
                raise ValueError("unsupported generalized planning request")
            context_v2 = v2.read(f.Context, ctx.snapshot)
            today = self._now().astimezone(ZoneInfo(context_v2.zone)).date()
            candidate = self._familiar_candidate(plan, expected_head, ctx, request, today=today)
            payload = v2.snapshot(candidate)
            v2.read(f.Candidate, payload)
            why = None
        else:
            if not isinstance(request, (Generate, Move)):
                raise ValueError("unsupported legacy planning request")
            context = read(CONTEXT, ctx.snapshot)
            base = self._base(plan.id, expected_head)
            as_of = self._now()
            outcomes = self._outcomes(plan_id, request, base, as_of)
            context = self._review_context(context, outcomes, base)
            explanation = Rationale.retrieve(outcomes, rationale.current_catalog())
            selection = explanation.selection
            evidence = tuple(
                EvidenceRef(selection.release_id, key) for key in explanation.claim_keys
            )
            week = _generate(request, context, read(BLOCK, plan.block), base)
            self._check_recorded_slots(plan_id, base, week)
            _effective_dates(base, week, self._today(context))
            payload = snapshot(Candidate(request, week, evidence))
            read(CANDIDATE, payload)
            why = explanation.model_dump(mode="json")
        revision = PlanRevision(
            user_id=self._owner,
            plan_id=plan.id,
            base_id=expected_head,
            context_id=ctx.id,
            snapshot=payload,
            rationale=why,
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

    def preview(self, plan_id: UUID, revision_id: UUID) -> Preview | FamiliarPreview:
        self._lock_owner()
        return self._preview(self._plan(plan_id, lock=False), revision_id)

    def _preview(self, plan: TrainingPlan, revision_id: UUID) -> Preview | FamiliarPreview:
        revision = self._revision(plan.id, revision_id)
        if plan.block.get("schema_version") == 2:
            v2.require_preview_owner(self._owner)
            ctx = self._context()
            assert ctx is not None
            decision = self._decision(plan.id, revision.id)
            return FamiliarPreview(
                revision.id,
                revision.base_id,
                plan.head_id,
                revision.context_id,
                ctx.id,
                self._familiar_context(revision.context_id),
                v2.read(f.Block, plan.block),
                v2.read(f.Candidate, revision.snapshot),
                self._receipt(decision) if decision else None,
            )
        candidate = read(CANDIDATE, revision.snapshot)
        ctx = self._context()
        assert ctx is not None
        decision = self._decision(plan.id, revision_id)
        why = self._rationale(revision)
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
            why,
            why.eligibility() if why else (),
        )

    @staticmethod
    def _rationale(revision: PlanRevision) -> Rationale | None:
        if revision.rationale is None:
            return None
        return Rationale.model_validate_json(json.dumps(revision.rationale))

    def current(self, plan_id: UUID) -> Preview | FamiliarPreview | None:
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
            if plan.block.get("schema_version") == 2:
                candidate_v2 = v2.read(f.Candidate, revision.snapshot)
                if candidate_v2.rules != f.RULE:
                    raise StalePlan("familiar effort rule changed; submit a fresh proposal")
                context_v2 = v2.read(f.Context, ctx.snapshot)
                today = self._now().astimezone(ZoneInfo(context_v2.zone)).date()
                replay = self._familiar_candidate(
                    plan, expected_head, ctx, candidate_v2.request, today=today
                )
                decision_day = self._now().astimezone(ZoneInfo(context_v2.zone)).date()
                if decision_day != today:
                    try:
                        v2.check_dates(replay, v2.read(f.Block, plan.block), decision_day)
                    except ValueError as exc:
                        raise StalePlan(str(exc)) from exc
                if canonical(v2.snapshot(replay)) != canonical(revision.snapshot):
                    raise InvalidSnapshot("stored generalized prescription differs from replay")
            else:
                self._approve_legacy(plan, revision, ctx)
        row = PlanDecision(
            user_id=self._owner,
            plan_id=plan.id,
            revision_id=revision_id,
            choice=choice,
            command_id=command_id,
            reason=reason,
            decided_at=self._now(),
        )
        self._db.add(row)
        self._db.flush()  # PostgreSQL advances the approved head in this statement.
        self._db.expire(plan)
        return self._receipt(row)

    def _approve_legacy(
        self, plan: TrainingPlan, revision: PlanRevision, ctx: AthleteContext
    ) -> None:
        plan_id, expected_head = plan.id, revision.base_id
        context = read(CONTEXT, ctx.snapshot)
        base = self._base(plan_id, expected_head)
        candidate = read(CANDIDATE, revision.snapshot)
        if candidate.week.rule_version != RULES:
            raise StalePlan("planner rule version changed")
        why = self._rationale(revision)
        if why is None:
            if candidate.week.inputs.number == 2 or candidate.evidence:
                raise StalePlan("legacy proposal requires a fresh execution and evidence review")
        else:
            if not why.verify_selection():
                raise StalePlan("pinned scientific selection cannot be reproduced")
            refs = tuple(EvidenceRef(why.selection.release_id, key) for key in why.claim_keys)
            if refs != candidate.evidence:
                raise StalePlan("scientific reference differs from retrieval")
            if alerts := why.eligibility():
                raise StalePlan("Ineligible rationale reference · " + " / ".join(alerts))
            as_of = why.outcomes.as_of if why.outcomes else self._now()
            outcomes = self._outcomes(plan_id, candidate.request, base, as_of)
            if outcomes != why.outcomes:
                raise StalePlan("execution review changed; submit a fresh proposal")
            context = self._review_context(context, outcomes, base)
        week = _generate(candidate.request, context, read(BLOCK, plan.block), base)
        self._check_recorded_slots(plan_id, base, week)
        if canonical(snapshot(Candidate(candidate.request, week, candidate.evidence))) != canonical(
            revision.snapshot
        ):
            raise InvalidSnapshot("stored prescription differs from planner output")
        _effective_dates(base, week, self._today(context))

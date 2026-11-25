"""E2 golden repository cases. Each test runs real migrations in a disposable PostgreSQL schema."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import delete, func, select, text, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from fitness_intelligence.db import plan_commands
from fitness_intelligence.db.models import User
from fitness_intelligence.db.plan_commands import (
    Choice,
    DecisionConflict,
    InfeasiblePlan,
    PlanCommands,
    StalePlan,
)
from fitness_intelligence.db.plan_models import (
    AthleteContext,
    PlanDecision,
    PlanRevision,
    TrainingPlan,
)
from fitness_intelligence.db.plan_snapshot import (
    CANDIDATE,
    Candidate,
    EvidenceRef,
    Generate,
    InvalidSnapshot,
    Move,
    PlanningContext,
    read,
    snapshot,
)
from fitness_intelligence.db.review import render_review
from fitness_intelligence.planning.outcomes import Actual, WorkingSet
from fitness_intelligence.planning.planner import (
    Exposure,
    Slot,
    WeekInputs,
    WeekReview,
    generate_week,
)
from fitness_intelligence.planning.press_block import Availability, PressBlock

pytestmark = pytest.mark.postgres
BLOCK = PressBlock()
CONTEXT = PlanningContext(Availability())
FIRST = Generate(1)
SECOND = Generate(2)


@dataclass(frozen=True)
class Cycle:
    commands: PlanCommands
    owner: UUID
    plan: UUID
    context: UUID


@pytest.fixture
def cycle(db: Session, monkeypatch: pytest.MonkeyPatch) -> Cycle:
    monkeypatch.setattr(PlanCommands, "_today", lambda *_: BLOCK.start - timedelta(days=1))
    owner = User()
    db.add(owner)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(owner.id))
    cmd = PlanCommands(db)
    context = cmd.capture_context(CONTEXT, expected_context=None)
    result = Cycle(cmd, owner.id, cmd.create_cycle(BLOCK), context)
    db.commit()
    return result


def approve(cycle: Cycle, proposal: UUID, base: UUID | None = None) -> None:
    cycle.commands.decide(
        cycle.plan, proposal, expected_head=base, choice="approve", command_id=uuid4()
    )


def first_approved(cycle: Cycle) -> UUID:
    proposal = cycle.commands.submit(cycle.plan, None, FIRST)
    approve(cycle, proposal)
    return proposal


@pytest.mark.parametrize("feedback,sets", [(None, 5), (True, 6)])
def test_two_week_approval_move_decline_and_historical_read(
    db: Session, cycle: Cycle, feedback: bool | None, sets: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    cmd, plan = cycle.commands, cycle.plan
    first = cmd.submit(plan, None, FIRST)
    first_preview = cmd.preview(plan, first)
    assert cmd.current(plan) is None and len(first_preview.changes) == 4
    monkeypatch.setattr(PlanCommands, "_now", lambda *_: datetime(2027, 1, 2, tzinfo=UTC))
    approve(cycle, first)
    monkeypatch.setattr(PlanCommands, "_today", lambda *_: BLOCK.start + timedelta(days=6))
    review = WeekReview(
        BLOCK.version,
        BLOCK.start,
        datetime(2027, 1, 9, 16, tzinfo=UTC),
        Exposure(True, (Decimal(6),) * 3),
        Exposure(True, (Decimal(7),) * 2),
        feedback,
    )
    monkeypatch.setattr(PlanCommands, "_now", lambda *_: review.as_of)
    for slot, count, effort in ((Slot.FIRST_PRESS, 3, 6), (Slot.SECOND_PRESS, 2, 7)):
        session = first_preview.candidate.week.session(slot)
        cmd.record_outcome(
            plan,
            first,
            1,
            slot,
            Actual(
                status="completed",
                confirmed_barbell_press=True,
                manageable=feedback,
                working_sets=tuple(WorkingSet(ordinal=i + 1, rpe=effort) for i in range(count)),
            ),
            occurred_at=datetime.combine(session.day, session.start, CONTEXT.availability.zone),
            command_id=uuid4(),
        )
    context = cmd.capture_context(CONTEXT, expected_context=cycle.context)
    refs = (EvidenceRef("synthetic-release", "synthetic-claim"),)
    with pytest.raises(ValueError, match="catalog retrieval"):
        cmd.submit(plan, first, SECOND, evidence=refs)
    second = cmd.submit(plan, first, SECOND)
    preview = cmd.preview(plan, second)
    week = preview.candidate.week
    assert first_preview.candidate.week == generate_week(WeekInputs(BLOCK, CONTEXT.availability, 1))
    assert week == generate_week(
        WeekInputs(BLOCK, CONTEXT.availability, 2, first_preview.candidate.week, review)
    )
    assert cmd.current(plan).revision_id == first
    assert (week.press_sets, week.running_seconds) == (sets, 2700)
    assert week.inputs.review == review and week.inputs.previous == first_preview.candidate.week
    assert week.inputs.block == BLOCK and preview.candidate.evidence == ()
    assert {c.week for c in preview.changes} == {2} and len(preview.changes) == 4
    approve(cycle, second, first)

    sat = week.session(Slot.LONG_RUN)
    sun = sat.day + timedelta(days=1)
    changed = replace(CONTEXT.availability, overrides=((sat.day, None),))
    cmd.capture_context(PlanningContext(changed, review), expected_context=context)
    move = Move(Slot.LONG_RUN, sun, time(9))
    declined = cmd.submit(plan, second, move)
    (delta,) = cmd.preview(plan, declined).changes
    assert delta.before == sat and delta.after == replace(sat, day=sun)
    decline_id = uuid4()
    arguments = dict(expected_head=second, choice="decline", command_id=decline_id, reason="retain")
    db.execute(text("SET LOCAL TIME ZONE 'America/Toronto'"))
    receipt = cmd.decide(plan, declined, **arguments)
    assert receipt.choice == "decline" and receipt.decided_at.utcoffset() == timedelta(0)
    assert cmd.current(plan).candidate.week == week
    assert "Current availability conflict · long-run" in render_review(cmd.current(plan))
    moved = cmd.submit(plan, second, move)
    approve(cycle, moved, second)
    db.commit()
    with Session(db.get_bind()) as fresh:
        commands = PlanCommands(fresh)
        assert commands.decide(plan, declined, **arguments) == receipt
        assert commands.current(plan).candidate.week.session(Slot.LONG_RUN) == delta.after
        assert commands.preview(plan, second).candidate == preview.candidate
        assert commands.preview(plan, first).candidate == first_preview.candidate
        assert commands.preview(plan, declined).decision == receipt


def test_command_receipt_checks_entire_intent_before_head(db: Session, cycle: Cycle) -> None:
    cmd, plan = cycle.commands, cycle.plan
    revision = cmd.submit(plan, None, FIRST)
    alternate = cmd.submit(plan, None, FIRST)
    command = uuid4()
    args = dict(expected_head=None, choice="approve", command_id=command, reason="reviewed")
    receipt = cmd.decide(plan, revision, **args)
    newer = cmd.submit(plan, revision, SECOND)
    approve(cycle, newer, revision)
    assert cmd.decide(plan, revision, **args) == receipt
    for change in (dict(choice="decline"), dict(reason=None), dict(expected_head=newer)):
        with pytest.raises(DecisionConflict):
            cmd.decide(plan, revision, **(args | change))
    with pytest.raises(DecisionConflict):
        cmd.decide(plan, alternate, **args)
    with pytest.raises(DecisionConflict):
        cmd.decide(plan, revision, **(args | dict(command_id=uuid4())))
    assert db.scalar(select(func.count()).select_from(PlanDecision)) == 2


def test_context_change_stale_and_hard_conflict(db: Session, cycle: Cycle) -> None:
    cmd, plan = cycle.commands, cycle.plan
    base = first_approved(cycle)
    pending = cmd.submit(plan, base, SECOND)
    restricted = PlanningContext(
        replace(CONTEXT.availability, excluded_movements=frozenset({"press"}))
    )
    cmd.capture_context(restricted, expected_context=cycle.context)
    with pytest.raises(StalePlan, match="context"):
        approve(cycle, pending, base)
    with pytest.raises(StalePlan, match="context"):
        cmd.capture_context(CONTEXT, expected_context=cycle.context)
    with pytest.raises(InfeasiblePlan) as conflict:
        cmd.submit(plan, base, SECOND)
    assert "movement-restriction" in {f.rule for f in conflict.value.conflicts.findings}
    assert cmd.current(plan).current_context == restricted
    assert cmd.current(plan).revision_id == base and cmd.preview(plan, pending).decision is None


def test_elapsed_day_rechecked_at_approval(cycle: Cycle, monkeypatch: pytest.MonkeyPatch) -> None:
    revision = cycle.commands.submit(cycle.plan, None, FIRST)
    monkeypatch.setattr(PlanCommands, "_today", lambda *_: BLOCK.start)
    with pytest.raises(StalePlan, match="already started"):
        approve(cycle, revision)
    assert cycle.commands.current(cycle.plan) is None


@pytest.mark.parametrize("race", ["first", "successors", "approve-decline", "retry"])
def test_concurrent_decisions(db: Session, cycle: Cycle, race: str) -> None:
    base = None if race == "first" else first_approved(cycle)
    request = FIRST if base is None else SECOND
    one = cycle.commands.submit(cycle.plan, base, request)
    two = (
        one
        if race in ("approve-decline", "retry")
        else cycle.commands.submit(cycle.plan, base, request)
    )
    db.commit()
    gate = Barrier(2)
    engine = db.get_bind()
    command = uuid4()

    def decide(revision: UUID, choice: Choice, command_id: UUID) -> str:
        with Session(engine) as independent, independent.begin():
            cmd = PlanCommands(independent)
            gate.wait(timeout=10)
            try:
                return cmd.decide(
                    cycle.plan, revision, expected_head=base, choice=choice, command_id=command_id
                ).choice
            except StalePlan:
                return "stale"
            except DecisionConflict:
                return "decided"

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(decide, one, "approve", command)
        b = pool.submit(
            decide,
            two,
            "decline" if race == "approve-decline" else "approve",
            command if race == "retry" else uuid4(),
        )
        outcomes = sorted([a.result(timeout=15), b.result(timeout=15)])
    if race == "approve-decline":
        assert outcomes in (["approve", "decided"], ["decided", "decline"])
    else:
        assert outcomes == (["approve", "approve"] if race == "retry" else ["approve", "stale"])
    head = cycle.commands.current(cycle.plan).revision_id
    assert head in (one, two) if "approve" in outcomes else head == base
    assert db.scalar(select(func.count()).select_from(PlanDecision)) == (1 if base is None else 2)


def test_approval_failure_rolls_back_receipt_and_head(db: Session, cycle: Cycle) -> None:
    base = first_approved(cycle)
    revision = cycle.commands.submit(cycle.plan, base, SECOND)
    db.commit()
    # Fail inside the head switch, after inserting the receipt. Rollback also removes the fault.
    db.execute(
        text("""CREATE FUNCTION reject_switch() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN RAISE EXCEPTION 'injected failure' USING ERRCODE = '23514'; END $$""")
    )
    db.execute(
        text("""CREATE TRIGGER reject_switch BEFORE UPDATE ON training_plans
        FOR EACH ROW EXECUTE FUNCTION reject_switch()""")
    )
    args = dict(expected_head=base, choice="approve", command_id=uuid4())
    with pytest.raises(IntegrityError, match="injected failure"):
        cycle.commands.decide(cycle.plan, revision, **args)
    db.rollback()
    with Session(db.get_bind()) as fresh, fresh.begin():
        cmd = PlanCommands(fresh)
        assert cmd.current(cycle.plan).revision_id == base
        assert cmd.preview(cycle.plan, revision).decision is None
        cmd.decide(cycle.plan, revision, **args)
        assert cmd.current(cycle.plan).revision_id == revision


def test_owner_and_plan_boundaries(
    db: Session, cycle: Cycle, monkeypatch: pytest.MonkeyPatch
) -> None:
    cmd, plan = cycle.commands, cycle.plan
    approved = first_approved(cycle)
    other_plan = cmd.create_cycle(BLOCK)
    other_owner = User()
    db.add(other_owner)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(other_owner.id))
    other = PlanCommands(db)
    ctx = other.capture_context(CONTEXT, expected_context=None)
    foreign_plan = other.create_cycle(BLOCK)
    for service, wrong_plan in ((other, plan), (cmd, other_plan), (cmd, foreign_plan)):
        with pytest.raises(NoResultFound):
            service.preview(wrong_plan, approved)
        with pytest.raises(NoResultFound):
            service.decide(
                wrong_plan, approved, expected_head=None, choice="approve", command_id=uuid4()
            )
    with pytest.raises(NoResultFound):
        other.current(plan)
    with pytest.raises(NoResultFound):
        other.submit(plan, approved, SECOND)
    monkeypatch.delenv("FITNESS_PLANNING_OWNER_ID")
    with pytest.raises(PermissionError):
        PlanCommands(db)
    raw = db.get(PlanRevision, approved).snapshot
    for fields in (
        dict(user_id=cycle.owner, plan_id=foreign_plan, base_id=None, context_id=cycle.context),
        dict(user_id=cycle.owner, plan_id=other_plan, base_id=approved, context_id=cycle.context),
        dict(user_id=cycle.owner, plan_id=other_plan, base_id=None, context_id=ctx),
    ):
        with pytest.raises(IntegrityError), db.begin_nested():
            db.add(PlanRevision(**fields, snapshot=raw))
            db.flush()
    with pytest.raises(IntegrityError), db.begin_nested():
        db.add(
            PlanDecision(
                user_id=other_owner.id,
                plan_id=foreign_plan,
                revision_id=approved,
                choice="approve",
                command_id=uuid4(),
            )
        )
        db.flush()


def test_sql_guards_for_sealed_rows_and_head(db: Session, cycle: Cycle) -> None:
    cmd, plan = cycle.commands, cycle.plan
    first = first_approved(cycle)
    rejected = cmd.submit(plan, first, SECOND)
    cmd.decide(plan, rejected, expected_head=first, choice="decline", command_id=uuid4())
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(update(TrainingPlan).values(head_id=rejected))
    second = cmd.submit(plan, first, SECOND)
    approve(cycle, second, first)
    for statement in (
        update(PlanRevision).values(snapshot={}),
        delete(PlanRevision),
        update(PlanRevision).values(base_id=None),
        text(
            "TRUNCATE athlete_contexts, training_plans, plan_revisions, "
            "plan_decisions, session_outcomes"
        ),
        update(PlanDecision).values(choice="approve"),
        delete(PlanDecision),
        update(AthleteContext).values(snapshot={}),
        delete(AthleteContext),
        update(TrainingPlan).values(block={}),
        delete(TrainingPlan),
        *(update(TrainingPlan).values(head_id=target) for target in (None, first, rejected)),
    ):
        with pytest.raises(IntegrityError), db.begin_nested():
            db.execute(statement)
    assert cmd.current(plan).revision_id == second


@pytest.mark.parametrize(
    "defect", ["version", "unknown", "bad-kind", "quantity", "calendar", "plausible"]
)
def test_corrupt_candidate_cannot_activate(db: Session, cycle: Cycle, defect: str) -> None:
    cmd, plan = cycle.commands, cycle.plan
    valid = cmd.submit(plan, None, FIRST)
    raw = deepcopy(db.get(PlanRevision, valid).snapshot)
    days = raw["data"]["week"]["days"]
    group = days[0]["sessions"][0]["prescription"]["exercises"][0]["groups"][0]
    if defect == "version":
        raw["schema_version"] = 2
    elif defect == "unknown":
        group["injected"] = True
    elif defect == "bad-kind":
        group["kind"] = "surprise"
    elif defect == "quantity":
        group["external_kg"]["nominal"] = "NaN"
    elif defect == "calendar":
        days.pop()
    else:
        group["count"] += 1
    row = PlanRevision(
        plan_id=plan, user_id=cycle.owner, context_id=cycle.context, base_id=None, snapshot=raw
    )
    db.add(row)
    db.flush()
    with pytest.raises(InvalidSnapshot):
        approve(cycle, row.id)
    assert (
        cmd.current(plan) is None and db.scalar(select(func.count()).select_from(PlanDecision)) == 0
    )


def test_canonical_snapshot_independent_of_decimal_scale_and_set_order(cycle: Cycle) -> None:
    revision = cycle.commands.submit(cycle.plan, None, FIRST)
    candidate = cycle.commands.preview(cycle.plan, revision).candidate
    week = candidate.week
    block = replace(BLOCK, baseline_kg=Decimal("30.000000"))
    changed = replace(week, inputs=replace(week.inputs, block=block))
    a = snapshot(candidate)
    b = snapshot(Candidate(candidate.request, changed, ()))
    assert a == b == snapshot(read(CANDIDATE, a))
    assert a["data"]["week"]["inputs"]["block"]["baseline_kg"] == "30"
    availability = replace(CONTEXT.availability, equipment=frozenset(("rack", "barbell", "bench")))
    assert snapshot(PlanningContext(availability))["data"]["availability"]["equipment"] == [
        "barbell",
        "bench",
        "rack",
    ]


def test_direct_decision_checks_current_context_and_base(db: Session, cycle: Cycle) -> None:
    cmd, plan = cycle.commands, cycle.plan
    stale_ctx = cmd.submit(plan, None, FIRST)
    cmd.capture_context(CONTEXT, expected_context=cycle.context)
    stale_base = cmd.submit(plan, None, FIRST)

    def insert_receipt(revision: UUID) -> None:
        with pytest.raises(IntegrityError), db.begin_nested():
            db.add(
                PlanDecision(
                    plan_id=plan,
                    user_id=cycle.owner,
                    revision_id=revision,
                    choice="approve",
                    command_id=uuid4(),
                )
            )
            db.flush()

    insert_receipt(stale_ctx)
    winner = first_approved(cycle)
    insert_receipt(stale_base)
    assert cmd.current(plan).revision_id == winner
    assert db.scalar(select(func.count()).select_from(PlanDecision)) == 1


def test_retained_week_and_zone_constraints(cycle: Cycle) -> None:
    cmd, plan = cycle.commands, cycle.plan
    base = first_approved(cycle)
    changed = replace(CONTEXT.availability, overrides=((BLOCK.start, None),))
    ctx = cmd.capture_context(PlanningContext(changed), expected_context=cycle.context)
    with pytest.raises(StalePlan, match="retained week"):
        cmd.submit(plan, base, SECOND)
    travel = replace(CONTEXT.availability, zone=ZoneInfo("America/Vancouver"))
    cmd.capture_context(PlanningContext(travel), expected_context=ctx)
    with pytest.raises(StalePlan, match="planning zone"):
        cmd.submit(plan, base, FIRST)


def test_e2_migration_preflight_and_prior_head_roundtrip(db: Session) -> None:
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.downgrade(config, "b702_hevy_pending")
    assert db.scalar(text("SELECT to_regclass('plan_revisions') IS NULL"))
    assert db.scalar(text("SELECT to_regprocedure('e2_apply_decision()') IS NULL"))
    db.commit()
    command.upgrade(config, "e201")
    command.upgrade(config, "head")
    command.check(config)
    owner = User()
    db.add(owner)
    db.flush()
    db.add(TrainingPlan(user_id=owner.id, block=snapshot(BLOCK)))
    db.commit()
    with pytest.raises(RuntimeError, match="preserve history"):
        command.downgrade(config, "b702_hevy_pending")
    assert db.scalar(select(func.count()).select_from(TrainingPlan)) == 1


def test_rule_change_requires_review_and_history_stays_readable(
    cycle: Cycle, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = first_approved(cycle)
    pending = cycle.commands.submit(cycle.plan, base, SECOND)
    original = cycle.commands.current(cycle.plan).candidate
    monkeypatch.setattr(plan_commands, "RULES", "synthetic-new-release")
    with pytest.raises(StalePlan, match="rule version"):
        approve(cycle, pending, base)
    assert cycle.commands.current(cycle.plan).candidate == original


def test_context_writer_serializes_with_approval(db: Session, cycle: Cycle) -> None:
    base = first_approved(cycle)
    pending = cycle.commands.submit(cycle.plan, base, SECOND)
    db.commit()
    engine = db.get_bind()
    gate = Barrier(2)

    def approve_in_another_session() -> None:
        with Session(engine) as fresh, fresh.begin():
            cmd = PlanCommands(fresh)
            gate.wait(timeout=10)
            with pytest.raises(StalePlan, match="context"):
                cmd.decide(
                    cycle.plan, pending, expected_head=base, choice="approve", command_id=uuid4()
                )

    with ThreadPoolExecutor(max_workers=1) as pool:
        restricted = PlanningContext(replace(CONTEXT.availability, equipment=frozenset()))
        cycle.commands.capture_context(restricted, expected_context=cycle.context)
        future = pool.submit(approve_in_another_session)
        gate.wait(timeout=10)
        db.commit()
        future.result(timeout=15)
    assert cycle.commands.current(cycle.plan).revision_id == base
    assert cycle.commands.preview(cycle.plan, pending).decision is None

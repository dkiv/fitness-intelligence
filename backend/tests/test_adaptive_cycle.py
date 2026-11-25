"""E3 golden cases, synthetic owners and a fixed January 2027 UTC clock."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import UTC, datetime, time
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import delete, func, select, text, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session
from test_evidence_catalog import FIXTURE, fixture, load_modified

from fitness_intelligence.db.execution import OutcomeConflict
from fitness_intelligence.db.models import ExternalReference, SourceAccount, User, Workout
from fitness_intelligence.db.plan_commands import InfeasiblePlan, PlanCommands, StalePlan
from fitness_intelligence.db.plan_models import PlanRevision, SessionOutcome
from fitness_intelligence.db.plan_snapshot import Generate, Move, PlanningContext
from fitness_intelligence.db.review import render_review
from fitness_intelligence.planning import rationale
from fitness_intelligence.planning.outcomes import Actual, WorkingSet
from fitness_intelligence.planning.planner import Exposure, Slot, WeekReview
from fitness_intelligence.planning.press_block import Availability, PressBlock

pytestmark = pytest.mark.postgres


def instant(day: int, hour: int = 14) -> datetime:
    return datetime(2027, 1, day, hour, tzinfo=UTC)


def lift(count: int, **changes: object) -> Actual:
    values = dict(
        status="completed",
        confirmed_barbell_press=True,
        manageable=True,
        working_sets=tuple(WorkingSet(ordinal=i + 1, rpe=7) for i in range(count)),
    )
    return Actual.model_validate(values | changes)


@dataclass
class Cycle:
    cmd: PlanCommands
    owner: UUID
    plan: UUID
    first: UUID
    context: UUID

    def record(
        self,
        slot: Slot,
        day: int,
        actual: Actual,
        *,
        command_id: UUID | None = None,
        workout_id: UUID | None = None,
        supersedes_id: UUID | None = None,
    ) -> UUID:
        return self.cmd.record_outcome(
            self.plan,
            self.first,
            1,
            slot,
            actual,
            occurred_at=instant(day),
            command_id=command_id or uuid4(),
            workout_id=workout_id,
            supersedes_id=supersedes_id,
        )

    def propose(self) -> UUID:
        return self.cmd.submit(self.plan, self.first, Generate(2))

    def approve(self, proposal: UUID) -> None:
        self.cmd.decide(
            self.plan, proposal, expected_head=self.first, choice="approve", command_id=uuid4()
        )


@pytest.fixture
def cycle(db: Session, monkeypatch: pytest.MonkeyPatch) -> Cycle:
    owner = User()
    db.add(owner)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(owner.id))
    cmd = PlanCommands(db)
    monkeypatch.setattr(PlanCommands, "_now", lambda _: instant(2))
    context = cmd.capture_context(PlanningContext(Availability()), expected_context=None)
    plan = cmd.create_cycle(PressBlock())
    first = cmd.submit(plan, None, Generate(1))
    cmd.decide(plan, first, expected_head=None, choice="approve", command_id=uuid4())
    monkeypatch.setattr(PlanCommands, "_now", lambda _: instant(10))
    db.commit()
    return Cycle(cmd, owner.id, plan, first, context)


def test_a1_full_review_and_immutable_history(db: Session, cycle: Cycle) -> None:
    cycle.record(Slot.FIRST_PRESS, 4, lift(3))
    cycle.record(Slot.SECOND_PRESS, 7, lift(2))
    cycle.record(Slot.SHORT_RUN, 5, Actual(status="missed", feedback="Schedule conflict"))
    proposal = cycle.propose()
    view = cycle.cmd.preview(cycle.plan, proposal)
    why = view.rationale
    assert why.outcomes.counts() == dict(completed=2, missed=1, partial=0, unknown=1)
    assert why.selection.release_id == "j1-screening-1" and why.claim_keys == ()
    assert why.outcomes.known_coverage == (3, 4) and why.outcomes.completion_among_known == (2, 3)
    assert why.selection.query == rationale.DOSE_QUERY
    report = render_review(view)
    for required in (
        "Known coverage 3/4",
        "completion among known 2/3",
        "press 5 → 6 sets",
        "runs 45 → 45 min",
        "working 2 × 6 at 30 kg",
        "working 3 × 6 at 30 kg",
        "Evidence gap",
        "synthetic fixture parameters",
        "approved base",
        "approve or decline",
        "Schedule conflict",
    ):
        assert required in report
    assert not any(c.assertion in report for c in rationale.current_catalog().release.claims)
    week = view.candidate.week
    assert week.inputs.block == week.inputs.previous.inputs.block == PressBlock()
    assert [
        week.session(s).prescription.duration_seconds.nominal
        for s in (Slot.SHORT_RUN, Slot.LONG_RUN)
    ] == [1200, 1500]
    db.commit()
    with Session(db.get_bind()) as fresh:
        assert render_review(PlanCommands(fresh).preview(cycle.plan, proposal)) == report
    cycle.approve(proposal)
    assert cycle.cmd.current(cycle.plan).revision_id == proposal


@pytest.mark.parametrize(
    "observation",
    [
        lift(2, manageable=None),
        lift(2, inferred_sets=1),
        lift(1),
        lift(2, status="partial"),
        lift(2, working_sets=(WorkingSet(ordinal=1, rpe=7), WorkingSet(ordinal=2))),
        lift(2, working_sets=(WorkingSet(ordinal=1, rpe=8), WorkingSet(ordinal=2, rpe=7))),
        lift(2, working_sets=(WorkingSet(ordinal=1, rpe=7, reps=4), WorkingSet(ordinal=2, rpe=7))),
        Actual(status="completed", inferred_sets=2),
        Actual(status="unknown"),
    ],
)
def test_a2_insufficient_evidence_cannot_progress(cycle: Cycle, observation: Actual) -> None:
    cycle.record(Slot.FIRST_PRESS, 4, lift(3))
    cycle.record(Slot.SECOND_PRESS, 7, observation)
    # Even a supplied E2 review attesting everything cannot bypass the projection.
    fabricated = WeekReview(
        PressBlock().version,
        PressBlock().start,
        instant(10),
        Exposure(True, (Decimal(7),) * 3),
        Exposure(True, (Decimal(7),) * 2),
        True,
    )
    cycle.cmd.capture_context(
        PlanningContext(Availability(), fabricated), expected_context=cycle.context
    )
    view = cycle.cmd.preview(cycle.plan, cycle.propose())
    assert (view.candidate.week.press_sets, view.candidate.week.running_seconds) == (5, 2700)
    assert "eligible=False" in render_review(view)


def test_d2_late_run_and_corrected_feedback(db: Session, cycle: Cycle) -> None:
    proposal = cycle.propose()
    cycle.approve(proposal)
    report = cycle.cmd.preview(cycle.plan, proposal).rationale
    actual = Actual(status="partial", run_seconds=900, run_rpe=4)
    token = uuid4()
    original = cycle.record(Slot.SHORT_RUN, 5, actual, command_id=token)
    assert cycle.record(Slot.SHORT_RUN, 5, actual, command_id=token) == original
    with pytest.raises(OutcomeConflict, match="different intent"):
        cycle.record(Slot.SHORT_RUN, 5, Actual(status="completed"), command_id=token)
    with pytest.raises(OutcomeConflict, match="current slot"):
        cycle.record(Slot.SHORT_RUN, 5, actual)
    with pytest.raises(OutcomeConflict, match="in force"):
        cycle.cmd.record_outcome(
            cycle.plan,
            proposal,
            1,
            Slot.SHORT_RUN,
            actual,
            occurred_at=instant(5),
            command_id=uuid4(),
            supersedes_id=original,
        )
    corrected = cycle.record(
        Slot.SHORT_RUN, 5, Actual(status="completed", run_seconds=1200), supersedes_id=original
    )
    with pytest.raises(OutcomeConflict, match="current slot"):
        cycle.record(Slot.SHORT_RUN, 5, actual, supersedes_id=original)
    assert db.get(SessionOutcome, corrected).supersedes_id == original
    assert db.get(SessionOutcome, original).actual["status"] == "partial"
    current = cycle.cmd.weekly_review(cycle.plan, 1)
    run = next(s for s in current.slots if s.slot == Slot.SHORT_RUN)
    assert (run.revision_id, run.recorded_at, run.occurred_at) == (
        cycle.first,
        instant(10),
        instant(5),
    )
    assert run.status == "completed" and report.outcomes.counts()["unknown"] == 4
    assert cycle.cmd.preview(cycle.plan, proposal).rationale == report
    for stmt in (
        update(SessionOutcome).values(week=2),
        delete(SessionOutcome),
        text("TRUNCATE session_outcomes"),
    ):
        with pytest.raises(IntegrityError), db.begin_nested():
            db.execute(stmt)


def test_d2_ambiguous_workouts_require_explicit_attribution_and_live_support(
    db: Session, cycle: Cycle
) -> None:
    first, alternate = (
        Workout(user_id=cycle.owner, title="Synthetic", started_at=instant(4)) for _ in range(2)
    )
    db.add_all([first, alternate])
    account = SourceAccount(
        user_id=cycle.owner, provider="hevy", provider_account_id="fixture", status="active"
    )
    db.add(account)
    db.flush()
    ref = ExternalReference(
        user_id=cycle.owner,
        source_account_id=account.id,
        provider="hevy",
        entity_type="workout",
        external_id="synthetic",
        workout_id=first.id,
        raw_payload={},
    )
    db.add(ref)
    db.flush()
    assert cycle.cmd.weekly_review(cycle.plan, 1).counts()["unknown"] == 4
    cycle.record(Slot.FIRST_PRESS, 4, lift(3), workout_id=first.id)
    for link in (first.id, None):
        with pytest.raises(OutcomeConflict, match="already attributed"):
            cycle.record(Slot.SECOND_PRESS, 4, lift(2), workout_id=link)
    cycle.record(Slot.SECOND_PRESS, 7, lift(2))
    proposal = cycle.propose()
    assert cycle.cmd.preview(cycle.plan, proposal).candidate.week.press_sets == 6
    ref.source_deleted_at = instant(10)
    db.flush()
    with pytest.raises(StalePlan, match="execution review"):
        cycle.approve(proposal)
    after = cycle.cmd.preview(cycle.plan, cycle.propose())
    assert after.candidate.week.press_sets == 5
    assert after.rationale.outcomes.counts()["unknown"] == 3
    assert "no longer supports" in render_review(after)
    assert cycle.cmd.preview(cycle.plan, proposal).rationale.outcomes.counts()["completed"] == 2


def test_d3_owner_plan_and_approval_lineage(
    db: Session, cycle: Cycle, monkeypatch: pytest.MonkeyPatch
) -> None:
    other = User()
    db.add(other)
    db.flush()
    foreign = Workout(user_id=other.id, title="Fixture", started_at=instant(4))
    db.add(foreign)
    db.flush()
    with pytest.raises(NoResultFound):
        cycle.record(Slot.FIRST_PRESS, 4, lift(3), workout_id=foreign.id)
    other_plan = cycle.cmd.create_cycle(PressBlock())
    pending = cycle.propose()
    declined = cycle.propose()
    cycle.cmd.decide(
        cycle.plan, declined, expected_head=cycle.first, choice="decline", command_id=uuid4()
    )
    for plan, revision in (
        (other_plan, cycle.first),
        (cycle.plan, pending),
        (cycle.plan, declined),
    ):
        with pytest.raises(OutcomeConflict):
            cycle.cmd.record_outcome(
                plan,
                revision,
                1,
                Slot.FIRST_PRESS,
                lift(3),
                occurred_at=instant(4),
                command_id=uuid4(),
            )
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(other.id))
    outsider = PlanCommands(db)
    with pytest.raises(NoResultFound):
        outsider.weekly_review(cycle.plan, 1)
    with pytest.raises(NoResultFound):
        outsider.record_outcome(
            cycle.plan,
            cycle.first,
            1,
            Slot.FIRST_PRESS,
            lift(3),
            occurred_at=instant(4),
            command_id=uuid4(),
        )
    baseline = dict(
        user_id=cycle.owner,
        plan_id=cycle.plan,
        revision_id=cycle.first,
        week=1,
        slot=Slot.FIRST_PRESS,
        command_id=uuid4(),
        actual=lift(3).model_dump(mode="json"),
        occurred_at=instant(4),
        recorded_at=instant(10),
    )
    for changes in (
        dict(user_id=other.id),
        dict(plan_id=other_plan),
        dict(week=2),
        dict(revision_id=pending),
        dict(revision_id=declined),
        dict(workout_id=foreign.id),
    ):
        with pytest.raises(IntegrityError), db.begin_nested():
            db.add(SessionOutcome(**(baseline | changes)))
            db.flush()


def test_a6_and_infeasible_schedule(cycle: Cycle) -> None:
    pending = cycle.propose()
    restriction = replace(Availability(), excluded_movements=frozenset({"press"}))
    ctx = cycle.cmd.capture_context(PlanningContext(restriction), expected_context=cycle.context)
    with pytest.raises(StalePlan, match="context"):
        cycle.approve(pending)
    assert "Excluded movements · press" in render_review(cycle.cmd.current(cycle.plan))
    with pytest.raises(InfeasiblePlan) as error:
        cycle.propose()
    assert "movement-restriction" in {f.rule for f in error.value.conflicts.findings}
    no_weekend = replace(
        Availability(), overrides=((instant(16).date(), None), (instant(17).date(), None))
    )
    cycle.cmd.capture_context(PlanningContext(no_weekend), expected_context=ctx)
    with pytest.raises(InfeasiblePlan) as error:
        cycle.propose()
    f = next(f for f in error.value.conflicts.findings if f.rule == "distinct-running-days")
    assert (
        dict(f.facts)["available_days"] == 1
        and cycle.cmd.current(cycle.plan).revision_id == cycle.first
    )


def test_corrected_observation_serializes_with_approval(db: Session, cycle: Cycle) -> None:
    original = cycle.record(Slot.FIRST_PRESS, 4, lift(3))
    pending = cycle.propose()
    db.commit()
    gate = Barrier(2)
    engine = db.get_bind()

    def approve() -> None:
        with Session(engine) as fresh, fresh.begin():
            gate.wait(timeout=10)
            with pytest.raises(StalePlan, match="execution review"):
                PlanCommands(fresh).decide(
                    cycle.plan,
                    pending,
                    expected_head=cycle.first,
                    choice="approve",
                    command_id=uuid4(),
                )

    with ThreadPoolExecutor(max_workers=1) as pool:
        # Same counts, same effort, new feedback and a new attestation identity.
        cycle.record(Slot.FIRST_PRESS, 4, lift(3, feedback="Felt steady"), supersedes_id=original)
        future = pool.submit(approve)
        gate.wait(timeout=10)
        db.commit()
        future.result(timeout=15)
    assert cycle.cmd.preview(cycle.plan, pending).decision is None
    cycle.approve(cycle.propose())


def test_c2_c3_selection_approval_and_withdrawal(
    cycle: Cycle, monkeypatch: pytest.MonkeyPatch
) -> None:
    old = fixture()
    data = json.loads(FIXTURE.read_bytes())
    data.update(
        release_id="fixture-c3",
        withdrawals=[
            dict(claim="effect-a@1", withdrawn_on="2000-01-11", reason="Fixture correction")
        ],
    )
    current = load_modified(data)
    registry = {c.release.release_id: c for c in (old, current)}
    monkeypatch.setattr(rationale, "load_release", registry.__getitem__)
    monkeypatch.setattr(rationale, "CURRENT_RELEASE", old.release.release_id)
    scope = old.release.claims[0].scope
    for experience, term in (
        ("recreational", "indirect"),
        ("unknown", "Evidence gap"),
        ("trained", "direct"),
    ):
        monkeypatch.setattr(
            rationale, "DOSE_QUERY", scope.model_copy(update=dict(experience=experience))
        )
        pending = cycle.propose()
        view = cycle.cmd.preview(cycle.plan, pending)
        assert term in render_review(view)
    before = render_review(view)
    for fragment in (
        "conflicts-with",
        "Table A, change score",
        "Figure B, fixed-dose contrast",
        "Programming option",
        "preferred-increase@1",
        "synthetic fixture parameters",
    ):
        assert fragment in before
    assert view.rationale.claim_keys == ("effect-a@1", "effect-b@1")
    token = uuid4()
    intent = dict(expected_head=cycle.first, choice="approve", command_id=token)
    receipt = cycle.cmd.decide(cycle.plan, pending, **intent)
    outstanding = cycle.cmd.submit(cycle.plan, pending, Generate(2))
    monkeypatch.setattr(rationale, "CURRENT_RELEASE", current.release.release_id)
    with pytest.raises(StalePlan, match="scientific reference"):
        cycle.cmd.decide(
            cycle.plan, outstanding, expected_head=pending, choice="approve", command_id=uuid4()
        )
    historical = cycle.cmd.preview(cycle.plan, pending)
    assert historical.rationale == view.rationale
    assert "withdrawn: Fixture correction" in render_review(historical)
    assert {outstanding, pending} <= set(cycle.cmd.citing("effect-a@1"))
    assert cycle.cmd.decide(cycle.plan, pending, **intent) == receipt
    fresh = cycle.cmd.submit(cycle.plan, pending, Generate(2))
    assert cycle.cmd.preview(cycle.plan, fresh).rationale.claim_keys == ("effect-b@1",)


def test_proposal_failure_rolls_back_observation_and_revision(db: Session, cycle: Cycle) -> None:
    db.execute(
        text("""CREATE FUNCTION reject_proposal() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN RAISE EXCEPTION 'injected failure' USING ERRCODE='23514'; END $$""")
    )
    db.execute(
        text("""CREATE TRIGGER reject_proposal BEFORE INSERT ON plan_revisions
                    FOR EACH ROW EXECUTE FUNCTION reject_proposal()""")
    )
    cycle.record(Slot.FIRST_PRESS, 4, lift(3))
    with pytest.raises(IntegrityError, match="injected failure"):
        cycle.propose()
    db.rollback()
    assert db.scalar(select(func.count()).select_from(SessionOutcome)) == 0
    assert db.scalar(select(func.count()).select_from(PlanRevision)) == 1
    assert cycle.cmd.current(cycle.plan).revision_id == cycle.first


def test_prescription_time_and_payload_guards(cycle: Cycle) -> None:
    for day in (1, 3, 11):
        with pytest.raises((OutcomeConflict, ValueError)):
            cycle.record(Slot.FIRST_PRESS, day, lift(3))
    with pytest.raises(ValueError, match="scheduled instant"):
        cycle.record(Slot.LONG_RUN, 5, Actual(status="missed"))
    with pytest.raises(ValueError, match="running slot"):
        cycle.record(Slot.FIRST_PRESS, 4, Actual(status="partial", run_seconds=600))
    with pytest.raises(ValueError, match="ordinal outside"):
        cycle.record(Slot.SECOND_PRESS, 7, lift(3))
    with pytest.raises(ValidationError, match="distinct ordinal"):
        lift(2, working_sets=(WorkingSet(ordinal=1), WorkingSet(ordinal=1)))
    with pytest.raises(ValidationError, match="confirm the prescribed"):
        lift(2, confirmed_barbell_press=False)


def test_e3_downgrade_preserves_data(db: Session, cycle: Cycle) -> None:
    cycle.record(Slot.FIRST_PRESS, 4, lift(3))
    db.commit()
    with pytest.raises(RuntimeError, match="preserve history"):
        command.downgrade(Config(str(Path(__file__).parents[1] / "alembic.ini")), "e201")
    assert cycle.cmd.weekly_review(cycle.plan, 1).counts()["completed"] == 1


def test_d2_move_splits_execution_timeline(cycle: Cycle, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(PlanCommands, "_now", lambda _: instant(6))
    target = instant(10).date()
    move = cycle.cmd.submit(cycle.plan, cycle.first, Move(Slot.LONG_RUN, target, time(9)))
    cycle.approve(move)
    monkeypatch.setattr(PlanCommands, "_now", lambda _: instant(10, 18))
    original = cycle.record(Slot.FIRST_PRESS, 4, lift(3))
    with pytest.raises(OutcomeConflict, match="in force"):
        cycle.record(Slot.SECOND_PRESS, 7, lift(2))
    later = cycle.cmd.record_outcome(
        cycle.plan, move, 1, Slot.SECOND_PRESS, lift(2), occurred_at=instant(7), command_id=uuid4()
    )
    run = cycle.cmd.record_outcome(
        cycle.plan,
        cycle.first,
        1,
        Slot.LONG_RUN,
        Actual(status="completed", run_seconds=1500),
        occurred_at=instant(5, 18),
        command_id=uuid4(),
    )
    second = cycle.cmd.submit(cycle.plan, move, Generate(2))
    view = cycle.cmd.preview(cycle.plan, second)
    assert view.candidate.week.press_sets == 6
    assert {
        (o.observation_id, o.revision_id) for o in view.rationale.outcomes.slots if o.actual
    } == {(original, cycle.first), (later, move), (run, cycle.first)}
    assert "Prescription in force at execution · 2027-01-09" in render_review(view)
    assert view.candidate.week.inputs.previous.session(Slot.LONG_RUN).day == target


def test_historical_v1_and_pinned_selection_validation(db: Session, cycle: Cycle) -> None:
    old = cycle.propose()
    row = db.get(PlanRevision, old)

    def candidate_with(rationale_data: dict | None) -> UUID:
        copied = PlanRevision(
            user_id=cycle.owner,
            plan_id=cycle.plan,
            base_id=cycle.first,
            context_id=cycle.context,
            snapshot=row.snapshot,
            rationale=rationale_data,
        )
        db.add(copied)
        db.flush()
        return copied.id

    legacy = candidate_with(None)
    assert "Historical E2" in render_review(cycle.cmd.preview(cycle.plan, legacy))
    with pytest.raises(StalePlan, match="legacy proposal"):
        cycle.approve(legacy)
    modified = json.loads(json.dumps(row.rationale))
    modified["selection"]["digest"] = "f" * 64
    damaged = candidate_with(modified)
    with pytest.raises(StalePlan, match="pinned scientific"):
        cycle.approve(damaged)
    assert cycle.cmd.current(cycle.plan).revision_id == cycle.first

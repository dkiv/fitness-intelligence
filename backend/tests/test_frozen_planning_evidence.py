"""Normal planning and import commands share a PostgreSQL owner lock across connections."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from queue import Queue
from threading import Event
from time import monotonic, sleep
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import Engine, func, select, text
from sqlalchemy.orm import Session
from test_familiar import NOW, approve
from test_familiar import preview_cycle as preview_fixture
from test_familiar_execution import Cycle, partial_strength
from test_familiar_execution import cycle as execution_fixture
from test_garmin_history import HistoricalProvider
from test_garmin_history import run as sync_history
from test_garmin_importer import DAY, IDENT, KEY, GarminClient, enroll, evidence
from test_garmin_importer import Importer as GarminImporter
from test_hevy_importer import FakeClient, edit
from test_planning_evidence import confirmed_run, qual

from fitness_intelligence.adapters.garmin.history import HistoryRun
from fitness_intelligence.adapters.garmin.history_state import Category, issue
from fitness_intelligence.adapters.garmin.history_state import Scope as HistoryScope
from fitness_intelligence.adapters.garmin.importer import Mode
from fitness_intelligence.adapters.hevy.importer import Importer, LocalBinding
from fitness_intelligence.adapters.local_account import locked_account
from fitness_intelligence.db import familiar_snapshot as wire
from fitness_intelligence.db import planning_evidence
from fitness_intelligence.db.familiar_snapshot import PREVIEW_OWNER
from fitness_intelligence.db.models import SourceAccount, User
from fitness_intelligence.db.plan_commands import PlanCommands, StalePlan
from fitness_intelligence.db.plan_models import PlanDecision, PlanRevision
from fitness_intelligence.db.review import render_review
from fitness_intelligence.planning import confirmation as cf
from fitness_intelligence.planning import evidence as e
from fitness_intelligence.planning import familiar as f

preview_cycle = preview_fixture
cycle = execution_fixture


def proposal(
    db: Session, preview_cycle: tuple[PlanCommands, UUID, UUID]
) -> tuple[PlanCommands, UUID, UUID, UUID, e.ReviewedCandidate, Importer]:
    cmd, cycle, _ = preview_cycle
    src = SourceAccount(
        user_id=PREVIEW_OWNER, provider="hevy", provider_account_id="account", status="active"
    )
    db.add(src)
    db.flush()
    importer = Importer(db.get_bind(), LocalBinding(PREVIEW_OWNER, src.id, "account"), FakeClient())
    scope = e.Scope(
        start=date(2026, 1, 1),
        stop=date(2026, 1, 2),
        strength_account=src.id,
        external_load_templates=("T1",),
    )
    head = approve(cmd, cycle, f.ProposeBlock(), None)
    rev = cmd.submit(cycle, head, f.FamiliarWeek(number=1), evidence_scope=scope)
    preview = cmd.preview(cycle, rev)
    original = preview.candidate
    assert isinstance(original, e.ReviewedCandidate)
    assert "0 performance records" in render_review(preview)
    assert "2026-01-01 · activity acquisition unselected · open issues none" in render_review(
        preview
    )
    assert original.decision_inputs.projection.performances == ()
    assert original.decision_inputs.projection.days[0].open_issues == ()
    assert (
        original.decision_inputs.cutoff == NOW
        and original.decision_inputs.projection.scope == scope
    )
    db.commit()
    return cmd, cycle, head, rev, original, importer


def wait_for_owner_waiter(engine: Engine, holder: int) -> None:
    # Verify a real wait on users ... FOR UPDATE, before any child write or FK check.
    deadline = monotonic() + 10
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as observer:
        while monotonic() < deadline:
            blocked = observer.scalar(
                text("""
                SELECT EXISTS(SELECT 1 FROM pg_stat_activity
                 WHERE :holder = ANY(pg_blocking_pids(pid))
                 AND query LIKE '%FROM users%' AND query LIKE '%FOR UPDATE%')
            """),
                {"holder": holder},
            )
            if blocked:
                return
            sleep(0.01)
    pytest.fail("expected another backend waiting for this owner's row lock")


def test_import_commits_before_waiting_approval(
    db: Session, preview_cycle: tuple, monkeypatch: pytest.MonkeyPatch
) -> None:
    cmd, cycle, head, rev, original, importer = proposal(db, preview_cycle)
    key = uuid4()
    engine = db.get_bind()
    from fitness_intelligence.adapters.hevy import importer as hevy

    acquired = Queue()
    release = Event()
    lock = hevy.lock_owner

    def pause_writer(session: Session, owner: UUID) -> None:
        lock(session, owner)
        if not release.is_set():
            acquired.put(session.scalar(text("SELECT pg_backend_pid()")))
            assert release.wait(20)

    monkeypatch.setattr(hevy, "lock_owner", pause_writer)

    def accept() -> None:
        with Session(engine) as decision, decision.begin():
            PlanCommands(decision).decide(
                cycle, rev, expected_head=head, choice="approve", command_id=key
            )

    with ThreadPoolExecutor(max_workers=2) as pool:
        writer = pool.submit(importer.sync)
        try:
            pid = acquired.get(timeout=10)
            decision = pool.submit(accept)
            wait_for_owner_waiter(engine, pid)
        finally:
            release.set()
        writer.result(timeout=10)
        with pytest.raises(StalePlan, match="evidence changed"):
            decision.result(timeout=10)
    assert cmd.current(cycle).revision_id == head
    assert (
        db.scalar(
            select(func.count()).select_from(PlanDecision).where(PlanDecision.command_id == key)
        )
        == 0
    )
    assert cmd.replay_familiar(cycle, rev) == original
    new_rev = cmd.submit(
        cycle,
        head,
        f.FamiliarWeek(number=1),
        evidence_scope=original.decision_inputs.projection.scope,
    )
    updated = cmd.preview(cycle, new_rev).candidate.decision_inputs.projection
    assert (
        len(updated.performances) == 1
        and updated.performances[0].members[0].fact.external_id == "synthetic-workout"
    )
    assert (
        cmd.decide(cycle, new_rev, expected_head=head, choice="approve", command_id=key).revision_id
        == new_rev
    )
    db.commit()


def test_approval_holds_writer_until_commit_and_retries(db: Session, preview_cycle: tuple) -> None:
    cmd, cycle, head, rev, original, importer = proposal(db, preview_cycle)
    key = uuid4()
    intent = dict(expected_head=head, choice="approve", command_id=key)
    cmd.decide(cycle, rev, **intent)
    db.rollback()
    assert cmd.current(cycle).revision_id == head and cmd.preview(cycle, rev).decision is None
    db.commit()
    with ThreadPoolExecutor(max_workers=1) as pool:
        try:
            receipt = cmd.decide(cycle, rev, **intent)
            pid = db.scalar(text("SELECT pg_backend_pid()"))
            writer = pool.submit(importer.sync)
            wait_for_owner_waiter(db.get_bind(), pid)
            db.commit()
        finally:
            db.rollback()
        writer.result(timeout=10)
    assert cmd.current(cycle).revision_id == rev
    assert cmd.decide(cycle, rev, **intent) == receipt
    assert cmd.replay_familiar(cycle, rev) == original
    assert cmd.preview(cycle, rev).candidate == original


def test_historical_import_opens_issue_and_preserves_sealed_review(
    db: Session, preview_cycle: tuple
) -> None:
    cmd, cycle, _ = preview_cycle
    ev = evidence(db.get(User, PREVIEW_OWNER))
    provider = HistoricalProvider()
    db.commit()
    client = GarminClient(KEY, transport=httpx.MockTransport(provider.handle))
    try:
        enroll(GarminImporter(db.get_bind(), ev, client))
    finally:
        client.close()
    scope = e.Scope(
        start=DAY, stop=DAY + timedelta(days=1), endurance_account=ev.source.source_account_id
    )
    head = approve(cmd, cycle, f.ProposeBlock(), None)
    request = f.FamiliarWeek(number=1)
    rev = cmd.submit(cycle, head, request, evidence_scope=scope)
    before = cmd.preview(cycle, rev).candidate
    assert before.decision_inputs.projection.days[0].open_issues == ()
    db.commit()
    provider.steps = [{"index": 0, "sport": "RUNNING"}]
    result = sync_history(db, (ev, provider), (Category.ACTIVITIES, Category.STEPS))
    assert result["stopped"] == "activity detail requires reconciliation"
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=uuid4())
    assert cmd.replay_familiar(cycle, rev) == before
    fresh = cmd.submit(cycle, head, request, evidence_scope=scope)
    current = cmd.preview(cycle, fresh).candidate.decision_inputs
    assert current.projection.days[0].open_issues[0].issue.reason == "incomplete_steps"
    assert current.coverage_receipts and current.projection.days[0].instructions.status == "partial"


def test_explicit_account_isolation_and_transaction_mode(db: Session, preview_cycle: tuple) -> None:
    cmd, cycle, head, rev, original, _ = proposal(db, preview_cycle)
    other = User()
    db.add(other)
    db.flush()
    foreign = SourceAccount(
        user_id=other.id, provider="hevy", provider_account_id="foreign", status="active"
    )
    db.add(foreign)
    db.flush()
    foreign_scope = original.decision_inputs.projection.scope.model_copy(
        update={"strength_account": foreign.id}
    )
    with pytest.raises(ValueError, match="invalid source account"):
        cmd.submit(cycle, head, f.FamiliarWeek(number=1), evidence_scope=foreign_scope)
    writer = Importer(db.get_bind(), LocalBinding(other.id, foreign.id, "foreign"), FakeClient())
    writer.client.identity_value = "foreign"
    db.commit()
    writer.sync()
    with db.get_bind().connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        with (
            Session(connection) as session,
            pytest.raises(ValueError, match="active database transaction"),
        ):
            PlanCommands(session).decide(
                cycle, rev, expected_head=head, choice="approve", command_id=uuid4()
            )
    with db.get_bind().connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        with Session(connection) as session, pytest.raises(ValueError, match="read-committed"):
            PlanCommands(session).decide(
                cycle, rev, expected_head=head, choice="approve", command_id=uuid4()
            )
    assert (
        cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=uuid4()).revision_id
        == rev
    )


def test_new_issue_alone_invalidates_an_empty_day(db: Session, preview_cycle: tuple) -> None:
    """Use the historical writer's issue-only transaction without touching coverage or workouts."""
    cmd, cycle, _ = preview_cycle
    ev = evidence(db.get(User, PREVIEW_OWNER))
    provider = HistoricalProvider()
    db.commit()
    engine = db.get_bind()
    client = GarminClient(KEY, transport=httpx.MockTransport(provider.handle))
    try:
        enroll(GarminImporter(engine, ev, client))
        scope = e.Scope(
            start=DAY, stop=DAY + timedelta(days=1), endurance_account=ev.source.source_account_id
        )
        head = approve(cmd, cycle, f.ProposeBlock(), None)
        request = f.FamiliarWeek(number=1)
        pending = cmd.submit(cycle, head, request, evidence_scope=scope)
        before = cmd.preview(cycle, pending).candidate.decision_inputs
        db.commit()
        history_scope = HistoryScope("repair", DAY, DAY, (Category.ACTIVITIES,), uuid4(), 1)
        with locked_account(engine, ev.source.source_account_id) as writer:
            with writer.begin():
                binding = ev.resolve(writer, allow_new=False)
            with client.verified_session():
                history = HistoryRun(writer, ev, binding, client, history_scope)
                with history.write():
                    issue(
                        writer,
                        ev.source,
                        Category.ACTIVITIES,
                        DAY,
                        "day",
                        "contradictory_revision",
                        ["synthetic"],
                        NOW,
                    )
    finally:
        client.close()
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle, pending, expected_head=head, choice="approve", command_id=uuid4())
    db.rollback()
    fresh = cmd.submit(cycle, head, request, evidence_scope=scope)
    after = cmd.preview(cycle, fresh).candidate.decision_inputs
    assert before.projection.performances == after.projection.performances == ()
    assert before.coverage_receipts == after.coverage_receipts == ()
    assert before.projection.days[0].open_issues == ()
    assert after.projection.days[0].open_issues[0].issue.reason == "contradictory_revision"
    assert cmd.replay_familiar(cycle, pending).decision_inputs == before


def test_default_scope_rechecks_new_account_and_old_pending_requires_review(
    db: Session, preview_cycle: tuple
) -> None:
    cmd, cycle, _ = preview_cycle
    head = approve(cmd, cycle, f.ProposeBlock(), None)
    request = f.FamiliarWeek(number=1)
    rev = cmd.submit(cycle, head, request)
    pending = cmd.preview(cycle, rev)
    frozen = pending.candidate.decision_inputs
    assert frozen.selection == "representative-week" and not frozen.accounts
    assert frozen.projection.scope.start == pending.sealed_context.history_start
    # Also represent an otherwise-valid archived revision from before decision inputs existed.
    raw = wire.snapshot(pending.candidate)
    del raw["data"]["decision_inputs"]
    old = PlanRevision(
        user_id=PREVIEW_OWNER,
        plan_id=cycle,
        context_id=pending.context_id,
        base_id=head,
        snapshot=raw,
    )
    db.add(old)
    db.flush()
    assert wire.snapshot(cmd.replay_familiar(cycle, old.id)) == raw
    with pytest.raises(StalePlan, match="predates frozen"):
        cmd.decide(cycle, old.id, expected_head=head, choice="approve", command_id=uuid4())
    ev = evidence(db.get(User, PREVIEW_OWNER))
    db.commit()
    client = GarminClient(KEY, transport=httpx.MockTransport(HistoricalProvider().handle))
    try:
        enroll(GarminImporter(db.get_bind(), ev, client))
    finally:
        client.close()
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=uuid4())
    fresh = cmd.submit(cycle, head, request)
    inputs = cmd.preview(cycle, fresh).candidate.decision_inputs
    assert inputs.projection.scope.endurance_account == ev.source.source_account_id
    assert inputs.projection.scope.recovery_account == ev.source.source_account_id


def test_freeze_confirmation_mask_manual_lineage_and_exclusions(db: Session, cycle: Cycle) -> None:
    cmd = cycle.cmd
    scope, receipt = confirmed_run(db, cmd, "unknown", ("elapsed_seconds",))
    first = cycle.record("gym-a", partial_strength())
    second = cycle.record("gym-a", partial_strength(), supersedes_id=first)
    gym_day = cycle.session("gym-a").day
    manual_scope = e.Scope(start=gym_day, stop=gym_day + timedelta(days=1))
    head = cycle.weeks[-1]
    rev = cmd.submit(cycle.plan, head, f.FamiliarWeek(number=4), evidence_scope=scope)
    sealed = cmd.preview(cycle.plan, rev).candidate
    inputs = sealed.decision_inputs.projection
    (run,) = inputs.performances
    manual_rev = cmd.submit(cycle.plan, head, f.FamiliarWeek(number=4), evidence_scope=manual_scope)
    manual_review = cmd.preview(cycle.plan, manual_rev).candidate
    (gym,) = manual_review.decision_inputs.projection.performances
    assert "running-role" in qual(run.tasks[0], "comparable-running").missing
    assert inputs.confirmations[0].confirmed == (("elapsed_seconds", 1250),)
    assert [item.id for item in gym.manual.history] == [first, second]
    db.commit()
    display = receipt.intent.display
    answer = cf.Answer(member=run.workout, disposition="withdraw", supersedes=receipt.command)
    cmd.confirm_observations(uuid4(), cf.prepare(display, (), exceptions=(answer,)), current=())
    db.commit()
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle.plan, rev, expected_head=head, choice="approve", command_id=uuid4())
    assert cmd.replay_familiar(cycle.plan, rev) == sealed
    assert cmd.confirmation_receipt(receipt.command) == receipt
    third = cycle.record("gym-a", partial_strength(), supersedes_id=second)
    db.commit()
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle.plan, manual_rev, expected_head=head, choice="approve", command_id=uuid4())
    assert third != second and cmd.replay_familiar(cycle.plan, manual_rev) == manual_review


def test_same_totals_new_source_children_require_fresh_review(
    db: Session, preview_cycle: tuple
) -> None:
    cmd, cycle, head, _, empty, importer = proposal(db, preview_cycle)
    importer.sync()
    scope = empty.decision_inputs.projection.scope
    request = f.FamiliarWeek(number=1)
    rev = cmd.submit(cycle, head, request, evidence_scope=scope)
    sealed = cmd.preview(cycle, rev).candidate
    (before,) = sealed.decision_inputs.projection.performances[0].members
    db.commit()
    importer.client.data["exercises"][0]["title"] = "Corrected synthetic exercise"
    edit(importer.client)
    importer.sync()
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=uuid4())
    assert cmd.replay_familiar(cycle, rev) == sealed
    fresh = cmd.submit(cycle, head, request, evidence_scope=scope)
    (after,) = (
        cmd.preview(cycle, fresh).candidate.decision_inputs.projection.performances[0].members
    )
    assert before.fact.row.repetitions == after.fact.row.repetitions == 8
    assert before.fact.row.weight_kg == after.fact.row.weight_kg == 0
    assert before.fact.row.set_id != after.fact.row.set_id and before.digest != after.digest


def test_bounded_running_edit_only_stales_the_selected_day(
    db: Session, preview_cycle: tuple
) -> None:
    cmd, cycle, _ = preview_cycle
    ev = evidence(db.get(User, PREVIEW_OWNER))
    provider = HistoricalProvider()
    db.commit()
    client = GarminClient(KEY, transport=httpx.MockTransport(provider.handle))
    importer = GarminImporter(db.get_bind(), ev, client)
    try:
        enroll(importer)
        assert importer.run(Mode.ACTIVITIES, day=DAY, steps=True)["created"] == 1
        scope = e.Scope(
            start=DAY, stop=DAY + timedelta(days=1), endurance_account=ev.source.source_account_id
        )
        other = scope.model_copy(
            update={"start": scope.stop, "stop": scope.stop + timedelta(days=1)}
        )
        head = approve(cmd, cycle, f.ProposeBlock(), None)
        request = f.FamiliarWeek(number=1)
        selected = cmd.submit(cycle, head, request, evidence_scope=scope)
        unselected = cmd.submit(cycle, head, request, evidence_scope=other)
        sealed = cmd.preview(cycle, selected).candidate
        (before,) = sealed.decision_inputs.projection.performances[0].members
        db.commit()
        provider.summaries[DAY][0]["distance"] = 0
        provider.details[IDENT]["metadataDTO"]["lastUpdateDate"] = "2024-11-06T01:00:00.000"
        assert importer.run(Mode.ACTIVITIES, day=DAY, steps=True)["updated"] == 1
    finally:
        client.close()
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle, selected, expected_head=head, choice="approve", command_id=uuid4())
    fresh = cmd.submit(cycle, head, request, evidence_scope=scope)
    (after,) = (
        cmd.preview(cycle, fresh).candidate.decision_inputs.projection.performances[0].members
    )
    assert before.fact.workout_id == after.fact.workout_id
    assert before.fact.distance_m > 0 and after.fact.distance_m == 0
    assert cmd.replay_familiar(cycle, selected) == sealed
    assert (
        cmd.decide(
            cycle, unselected, expected_head=head, choice="approve", command_id=uuid4()
        ).revision_id
        == unselected
    )


def test_policy_change_requires_fresh_review_even_when_facts_match(
    db: Session, preview_cycle: tuple, monkeypatch: pytest.MonkeyPatch
) -> None:
    cmd, cycle, head, rev, original, _ = proposal(db, preview_cycle)
    monkeypatch.setattr(planning_evidence, "DECISION_POLICY", "test-revised-policy")
    with pytest.raises(StalePlan, match="evidence changed"):
        cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=uuid4())
    scope = original.decision_inputs.projection.scope
    fresh = cmd.submit(cycle, head, f.FamiliarWeek(number=1), evidence_scope=scope)
    inputs = cmd.preview(cycle, fresh).candidate.decision_inputs
    assert inputs.projection == original.decision_inputs.projection
    assert inputs.policy != original.decision_inputs.policy
    assert cmd.replay_familiar(cycle, rev) == original

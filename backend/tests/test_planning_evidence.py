"""Read real D1D normalized synthetic observations and immutable E421/E422 rows together."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from test_familiar_execution import Cycle, partial_strength
from test_familiar_execution import cycle as cycle_fixture
from test_longitudinal import NOW, PERIOD, START, account, coverage, issue
from test_training_exposure import lift, outing, recovery

from fitness_intelligence.db.confirmation_models import ConfirmationReceipt
from fitness_intelligence.db.endurance_models import ActivitySplit, ActivityStep
from fitness_intelligence.db.familiar_snapshot import PREVIEW_OWNER
from fitness_intelligence.db.history_models import GarminCoverage
from fitness_intelligence.db.models import ExerciseSet, User, Workout, WorkoutTombstone
from fitness_intelligence.db.plan_commands import PlanCommands
from fitness_intelligence.db.plan_models import SessionOutcome
from fitness_intelligence.db.planning_evidence import query_planning_evidence
from fitness_intelligence.domain.endurance import DailyMetric
from fitness_intelligence.planning import confirmation as c
from fitness_intelligence.planning import evidence as e
from fitness_intelligence.planning import familiar_outcomes as actual

cycle = cycle_fixture


@pytest.fixture
def plans(db: Session, monkeypatch: pytest.MonkeyPatch) -> PlanCommands:
    db.add(User(id=PREVIEW_OWNER))
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(PREVIEW_OWNER))
    return PlanCommands(db)


def context(member: e.NativeMember, **changes) -> e.StrengthContext:
    return e.StrengthContext(
        account=member.fact.source.source_account_id,
        member=member.fact.row.set_id,
        source_digest=member.digest,
        basis="athlete identified this exercise and ordinal in the displayed workout",
        authority="athlete-context",
        comparison="standing-press",
        version="review-1",
        movement="press",
        variation="standing",
        equipment="barbell",
        load_convention="total-external-kg",
        group="primary",
        kind="working",
        ordinal=changes.get("ordinal", 1),
    )


def field(task: e.Task, name: str) -> e.FieldEvidence:
    return next(f for f in task.fields if f.name == name)


def qual(task: e.Task, name: str) -> e.Qualification:
    return next(q for q in task.qualifications if q.purpose == name)


def test_scoped_confirmation_replacement_and_withdrawal(db: Session, plans: PlanCommands) -> None:
    src = account(db, PREVIEW_OWNER, "hevy")
    workout = lift(db, src, 0, "press", [("press", [("normal", 5, False)])])
    scope = e.Scope(
        start=PERIOD.start,
        stop=PERIOD.stop,
        strength_account=src.id,
        external_load_templates=("press",),
    )
    engine = db.get_bind()
    db.commit()

    def read() -> e.Projection:
        return query_planning_evidence(engine, scope)

    original = read()
    (p,) = original.performances
    (m,) = p.members
    assert m.fact.load_convention == "external_kg" and m.fact.execution == "inferred"
    assert m.display is None and not qual(p.tasks[0], "comparable-strength").eligible
    assert field(p.tasks[0], "status").claims[0].tier == "provider-inferred"
    assert m.fact.row.exercise_position == m.fact.row.set_position == 0
    assert m.workout_created_at and m.reference_first_imported_at and m.recorded_at is None
    assert original.model_dump_json() == read().model_dump_json()
    assert e.Projection.model_validate_json(original.model_dump_json()) == original
    scope = scope.model_copy(update={"contexts": (context(m),)})
    fact = read().performances[0].members[0].display
    display = plans.preview_observations(src.id, (fact,))
    answer = c.Answer(
        member=fact.member,
        disposition="confirm",
        fields=("completion",),
        reported=c.AthleteReport(reps=4, set_rpe=Decimal(7)),
    )
    root = plans.confirm_observations(
        uuid4(), c.prepare(display, (), exceptions=(answer,)), current=(fact,)
    )
    db.commit()
    result = read()
    t = result.performances[0].tasks[0]
    assert len(result.performances) == len(result.confirmations) == 1
    assert field(t, "reps").value == 4 and [x.value for x in field(t, "reps").claims] == [5, 4]
    assert field(t, "kg").state == "source-only" and field(t, "set_rpe").value == 7
    assert qual(t, "confirmed-execution").eligible and not qual(t, "comparable-strength").eligible
    deletion = WorkoutTombstone(
        user_id=PREVIEW_OWNER,
        provider="hevy",
        source_account_id=src.id,
        external_id=m.fact.external_id,
        pending=True,
    )
    db.add(deletion)
    db.commit()
    held = read()
    assert (
        held.confirmations[0].state == "stale" and held.performances[0].execution_state == "unknown"
    )
    assert held.performances[0].members[0].pending_deletion.id == deletion.id
    assert field(held.performances[0].tasks[0], "reps").state == "withheld"
    db.delete(deletion)
    db.commit()
    source = db.get(ExerciseSet, fact.member)
    assert source.completed_at is None and source.repetitions == 5 and source.rpe is None
    stale_scope = scope.model_copy(
        update={"contexts": (context(m).model_copy(update={"version": "v2"}),)}
    )
    assert query_planning_evidence(engine, stale_scope).confirmations[0].state == "stale"
    withdrawal = c.Answer(member=fact.member, disposition="withdraw", supersedes=root.command)
    saved = plans.confirm_observations(
        uuid4(), c.prepare(display, (), exceptions=(withdrawal,)), current=()
    )
    db.commit()
    assert read().confirmations[0].state == "withdrawn"
    replacement = answer.model_copy(update={"supersedes": saved.command})
    plans.confirm_observations(
        uuid4(), c.prepare(display, (), exceptions=(replacement,)), current=(fact,)
    )
    db.commit()
    source.repetitions = 6
    db.commit()
    stale = read()
    assert stale.confirmations[0].state == "stale"
    assert stale.confirmations[0].history[-1].answer.reported.reps == 4
    assert field(stale.performances[0].tasks[0], "reps").value == 6
    assert field(stale.performances[0].tasks[0], "set_rpe").state == "unknown"
    db.delete(source)
    db.flush()
    new = ExerciseSet(
        user_id=PREVIEW_OWNER,
        exercise_id=fact.exercise,
        position=0,
        kind="normal",
        repetitions=6,
        weight_kg=Decimal(60),
    )
    db.add(new)
    db.commit()
    restored = read()
    assert restored.performances[0].workout == workout.id
    assert restored.performances[0].tasks[0].member == new.id and new.id != fact.member
    assert (
        restored.confirmations[0].member == fact.member
        and len(restored.confirmations[0].history) == 3
    )
    assert plans.confirmation_receipt(root.command) == root


def test_native_running_coverage_and_field_boundaries(db: Session, plans: PlanCommands) -> None:
    src = account(db, PREVIEW_OWNER)
    run = outing(db, src, 0, "101", "running", "trail_running", 5000, 1820, 1800, 1900)
    partial = coverage(src, 0, "activities", "partial", None)
    empty = coverage(src, 1, "activities", "empty", 0)
    full = coverage(src, 2, "activities", "empty", 0)
    full.receipts = {"empty_activity_scan": {"started_at": (NOW - timedelta(hours=1)).isoformat()}}
    db.add_all(
        [
            partial,
            empty,
            full,
            recovery(src, 0, DailyMetric.RESTING_HR, 58),
            ActivitySplit(
                user_id=PREVIEW_OWNER, workout_id=run.workout_id, position=0, kind="work", count=3
            ),
            ActivityStep(
                user_id=PREVIEW_OWNER,
                workout_id=run.workout_id,
                workout_index=0,
                step_index=0,
                target_zone=3,
            ),
        ]
    )
    scope = e.Scope(
        start=PERIOD.start,
        stop=PERIOD.stop,
        endurance_account=src.id,
        recovery_account=src.id,
        zone="America/Toronto",
        endurance_zone="America/Toronto",
        recovery_zone="America/Toronto",
    )
    engine = db.get_bind()
    db.commit()
    raw = query_planning_evidence(engine, scope)
    d0, d1, d2 = raw.days[:3]
    assert d0.activities.status == "partial" and (d0.running_count, d0.running_count_status) == (
        1,
        "lower_bound",
    )
    assert d1.running_count is None and d1.running_count_status == "empty_at_retrieval"
    assert (d2.running_count, d2.running_count_status) == (0, "complete_empty")
    assert any(cell.fact and cell.fact.value == 58 for cell in d0.recovery.cells)
    member = raw.performances[0].members[0]
    native = member.fact
    assert native.report_date != native.provider_date and native.subtype == "trail_running"
    assert native.instruction_positions == ((0, 0),) and native.split_positions == (0,)
    assert native.fields[0].source_field == "Synthetic.distance"
    assert member.display is None
    ctx = e.RunContext(
        account=src.id,
        member=run.workout_id,
        source_digest=member.digest,
        version="v1",
        comparison="controlled-protocol",
        basis="athlete identified the outing protocol",
        authority="athlete-context",
        role="controlled",
        structure="intervals",
    )
    scope = scope.model_copy(update={"contexts": (ctx,)})
    fact = query_planning_evidence(engine, scope).performances[0].members[0].display
    assert fact.achieved_steps == ()
    display = plans.preview_observations(src.id, (fact,))
    answer = c.Answer(
        member=fact.member,
        disposition="confirm",
        fields=("outing", "elapsed_seconds"),
        reported=c.AthleteReport(session_rpe=Decimal(6)),
    )
    plans.confirm_observations(
        uuid4(), c.prepare(display, (), exceptions=(answer,)), current=(fact,)
    )
    db.commit()
    t = query_planning_evidence(engine, scope).performances[0].tasks[0]
    assert (
        field(t, "session_rpe").value == 6 and field(t, "completed_work_repetitions").value is None
    )
    assert not any(x.name.endswith("achieved_rpe") for x in t.fields)
    assert field(t, "average_speed_mps").value == 4 and field(t, "activity_seconds").value == 1820
    assert "aligned-work-durations" in qual(t, "comparable-running").missing
    step = db.get(ActivityStep, (run.workout_id, 0, 0))
    step.target_zone = 4
    db.commit()
    edited = query_planning_evidence(engine, scope)
    edited_member = edited.performances[0].members[0]
    assert edited_member.fact.instruction_positions == native.instruction_positions
    assert edited_member.fact.instruction_content_digests != native.instruction_content_digests
    assert edited.confirmations[0].state == "stale" and edited_member.display is None
    db.add(issue(src, 0, "activities", "unresolved_activity"))
    db.commit()
    held = query_planning_evidence(engine, scope)
    assert not qual(held.performances[0].tasks[0], "confirmed-execution").eligible
    assert held.days[0].activities.issues
    (opened,) = held.days[0].open_issues
    assert opened.evidence_digest and opened.issue.reason == "unresolved_activity"


def test_owner_and_account_isolation(
    db: Session, plans: PlanCommands, monkeypatch: pytest.MonkeyPatch
) -> None:
    own = account(db, PREVIEW_OWNER, "hevy")
    other = account(db, PREVIEW_OWNER, "hevy")
    foreign = account(db)
    lift(db, other, 0, "outside", [("squat", [("normal", 8, True)])])
    db.commit()
    scope = e.Scope(start=START, stop=PERIOD.stop, strength_account=own.id)
    assert query_planning_evidence(db.get_bind(), scope).performances == ()
    for wrong in (foreign.id, other.id):
        with pytest.raises(ValueError, match="source account"):
            query_planning_evidence(
                db.get_bind(), scope.model_copy(update={"endurance_account": wrong})
            )
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(foreign.user_id))
    with pytest.raises(PermissionError):
        query_planning_evidence(db.get_bind(), scope)


def test_linked_hybrid_week_and_manual_correction(db: Session, cycle: Cycle) -> None:
    hevy = account(db, PREVIEW_OWNER, "hevy")
    garmin = account(db, PREVIEW_OWNER)
    gym = cycle.session("gym-a")
    w = lift(
        db, hevy, 0, "press", [("press", [("normal", 5, False)]), ("extra", [("normal", 8, False)])]
    )
    w.started_at = w.ended_at = gym.start_utc
    w.exercises[0].sets[0].weight_kg = 42
    easy = cycle.session("easy")
    run = outing(db, garmin, 0, "101", "running", "running", 2300, 1200, 1150, 1250)
    db.get(Workout, run.workout_id).started_at = easy.start_utc
    run.local_date = easy.day
    first = cycle.record("gym-a", partial_strength())
    cycle.record(
        "easy",
        actual.RunExecution(
            status="completed",
            role="easy",
            confirmed_outing=True,
            elapsed_seconds=1250,
            manageable=True,
        ),
    )
    cycle.record(
        "cruise",
        actual.RunExecution(
            status="partial",
            role="controlled",
            confirmed_outing=True,
            elapsed_seconds=1400,
            session_rpe=Decimal(6),
        ),
    )
    cycle.record("long", actual.RunExecution(status="missed", role="long", confirmed_outing=False))
    scope = e.Scope(
        start=date(2027, 1, 4),
        stop=date(2027, 1, 11),
        zone="America/Toronto",
        strength_account=hevy.id,
        endurance_account=garmin.id,
    )
    engine = db.get_bind()
    db.commit()
    initial = query_planning_evidence(engine, scope)
    press = next(p for p in initial.performances if p.workout == w.id)
    assert press.potential_duplicates == (first,)
    scope = scope.model_copy(update={"contexts": (context(press.members[0]),)})
    fact = (
        next(p for p in query_planning_evidence(engine, scope).performances if p.workout == w.id)
        .members[0]
        .display
    )
    display = cycle.cmd.preview_observations(hevy.id, (fact,))
    answer = c.Answer(
        member=fact.member,
        disposition="confirm",
        fields=("completion", "kg"),
        outcome=first,
        reported=c.AthleteReport(reps=4),
    )
    root = cycle.cmd.confirm_observations(
        uuid4(), c.prepare(display, (), exceptions=(answer,)), current=(fact,)
    )
    db.commit()
    manual_only = query_planning_evidence(
        engine, e.Scope(start=scope.start, stop=scope.stop, zone=scope.zone)
    )
    easy_task = next(p.tasks[0] for p in manual_only.performances if p.manual.prescribed == easy)
    assert qual(easy_task, "familiar-dose-input").eligible
    assert qual(easy_task, "progression-review-input").eligible
    assert field(easy_task, "session_rpe").state == "unknown"
    report = query_planning_evidence(engine, scope)
    assert e.Projection.model_validate_json(report.model_dump_json()) == report
    assert (
        len(report.performances) == 5
    )  # Linked lift, two unresolved easy-run records, cruise and miss.
    gym_result = next(p for p in report.performances if p.workout == w.id)
    assert (
        gym_result.manual.origin == cycle.weeks[0]
        and gym_result.manual.prescribed.occurrence == gym.occurrence
    )
    assert len(gym_result.tasks) == 5  # Four reported ordinals, plus an unplanned imported set.
    extra = next(t for t in gym_result.tasks if t.member == w.exercises[1].sets[0].id)
    assert extra.manual_set is None and field(extra, "reps").value == 8
    assert (
        qual(extra, "descriptive-exposure").eligible
        and not qual(extra, "comparable-strength").eligible
    )
    press_task = next(t for t in gym_result.tasks if t.member == fact.member)
    assert field(press_task, "reps").state == "conflict" and field(press_task, "reps").value is None
    assert {v.value for v in field(press_task, "reps").claims} == {4, 5}
    assert "contradictory reps" in qual(press_task, "comparable-strength").exclusions
    assert field(press_task, "kg").value == 42 and field(press_task, "set_rpe").value == 9
    assert report.model_dump_json() == query_planning_evidence(engine, scope).model_dump_json()
    cycle.record(
        "gym-a",
        actual.StrengthExecution(
            status="partial",
            sets=(
                actual.SetExecution(
                    movement="press",
                    variation="standing",
                    equipment="barbell",
                    group="primary",
                    kind="working",
                    ordinal=1,
                    status="partial",
                    reps=4,
                ),
            ),
        ),
        supersedes_id=first,
    )
    db.commit()
    updated = query_planning_evidence(engine, scope)
    assert updated.confirmations[0].effective_link is None
    revised = next(p for p in updated.performances if p.manual and p.sport == "strength")
    assert len(revised.manual.history) == 2 and field(revised.tasks[0], "status").value == "partial"
    assert revised.potential_duplicates == (w.id,)
    assert cycle.cmd.confirmation_receipt(root.command) == root
    assert db.scalar(select(func.count()).select_from(SessionOutcome)) == 5


def test_existing_ambiguous_ordinals_preserve_work(db: Session, cycle: Cycle) -> None:
    src = account(db, PREVIEW_OWNER, "hevy")
    w = lift(
        db, src, 0, "repeat", [("press", [("normal", 5, False)]), ("press", [("normal", 5, False)])]
    )
    w.started_at = w.ended_at = cycle.session("gym-a").start_utc
    outcome = cycle.record("gym-a", partial_strength())
    scope = e.Scope(start=date(2027, 1, 4), stop=date(2027, 1, 11), strength_account=src.id)
    db.commit()
    engine = db.get_bind()
    rows = next(p for p in query_planning_evidence(engine, scope).performances if p.workout).members
    scope = scope.model_copy(update={"contexts": tuple(context(m) for m in rows)})
    members = next(
        p for p in query_planning_evidence(engine, scope).performances if p.workout
    ).members
    # Sealed historical receipts from before E422 rejected this collision.
    for m in members:
        fact = m.display
        display = cycle.cmd.preview_observations(src.id, (fact,))
        answer = c.Answer(
            member=fact.member, disposition="confirm", fields=("completion",), outcome=outcome
        )
        intent = c.prepare(display, (), exceptions=(answer,))
        db.add(
            ConfirmationReceipt(
                user_id=PREVIEW_OWNER,
                actor=PREVIEW_OWNER,
                command=uuid4(),
                recorded_at=cycle.now,
                intent_digest=c.digest(intent),
                payload=intent.model_dump(mode="json"),
            )
        )
    db.commit()
    result = query_planning_evidence(engine, scope)
    assert len(result.confirmations) == 2
    assert all(s.ambiguous_set_link and s.effective_link is None for s in result.confirmations)
    imported = next(p for p in result.performances if p.workout)
    assert imported.manual is None and imported.potential_duplicates == (outcome,)
    assert len(imported.tasks) == 2
    assert all(
        "ambiguous prescribed ordinal" in qual(t, "comparable-strength").exclusions
        for t in imported.tasks
    )
    assert all(field(t, "status").state == "actual" for t in imported.tasks)


def test_one_snapshot_across_source_and_athlete_writers(
    db: Session, plans: PlanCommands, monkeypatch: pytest.MonkeyPatch
) -> None:
    from fitness_intelligence.db import planning_evidence as reader

    src = account(db, PREVIEW_OWNER, "hevy")
    lift(db, src, 0, "repeatable", [("press", [("normal", 5, False)])])
    scope = e.Scope(start=PERIOD.start, stop=PERIOD.stop, strength_account=src.id)
    engine = db.get_bind()
    db.commit()
    member = query_planning_evidence(engine, scope).performances[0].members[0]
    scope = scope.model_copy(update={"contexts": (context(member),)})
    fact = query_planning_evidence(engine, scope).performances[0].members[0].display
    display = plans.preview_observations(src.id, (fact,))
    root = plans.confirm_observations(
        uuid4(), c.prepare(display, ("completion", "reps")), current=(fact,)
    )
    db.commit()
    read_days = reader.read_training_days

    def interleave(session, *args, **kwargs):
        assert session.scalar(text("SHOW transaction_read_only")) == "on"
        days = read_days(session, *args, **kwargs)
        db.get(ExerciseSet, fact.member).repetitions = 9
        answer = c.Answer(member=fact.member, disposition="withdraw", supersedes=root.command)
        plans.confirm_observations(
            uuid4(), c.prepare(display, (), exceptions=(answer,)), current=()
        )
        db.commit()
        return days

    with monkeypatch.context() as mp:
        mp.setattr(reader, "read_training_days", interleave)
        consistent = query_planning_evidence(engine, scope)
    assert consistent.confirmations[0].state == "confirmed"
    assert field(consistent.performances[0].tasks[0], "reps").value == 5
    latest = query_planning_evidence(engine, scope)
    assert (
        latest.confirmations[0].state == "withdrawn"
        and field(latest.performances[0].tasks[0], "reps").value == 9
    )


def confirmed_run(
    db: Session, plans: PlanCommands, role: str, fields: tuple[c.Name, ...]
) -> tuple[e.Scope, c.Receipt]:
    src = account(db, PREVIEW_OWNER)
    run = outing(db, src, 0, "101", "running", "running", 2300, 1200, 1150, 1250)
    db.add(coverage(src, 0, "activities", "partial", None))
    scope = e.Scope(start=PERIOD.start, stop=PERIOD.stop, endurance_account=src.id)
    db.commit()
    member = query_planning_evidence(db.get_bind(), scope).performances[0].members[0]
    ctx = e.RunContext(
        account=src.id,
        member=run.workout_id,
        source_digest=member.digest,
        version="review-1",
        comparison="course-a",
        basis="athlete reviewed outing",
        authority="athlete-context",
        role=role,
        structure="continuous",
    )
    scope = scope.model_copy(update={"contexts": (ctx,)})
    fact = query_planning_evidence(db.get_bind(), scope).performances[0].members[0].display
    display = plans.preview_observations(src.id, (fact,))
    answer = c.Answer(
        member=fact.member,
        disposition="confirm",
        fields=fields,
        reported=c.AthleteReport(tolerance="comfortable"),
    )
    receipt = plans.confirm_observations(
        uuid4(), c.prepare(display, (), exceptions=(answer,)), current=(fact,)
    )
    db.commit()
    return scope, receipt


@pytest.mark.parametrize("role,eligible", [("unknown", False), ("easy", True)])
def test_review_running_role(db: Session, plans: PlanCommands, role: str, eligible: bool) -> None:
    scope, receipt = confirmed_run(db, plans, role, ("outing", "elapsed_seconds"))
    report = query_planning_evidence(db.get_bind(), scope)
    (p,) = report.performances
    (t,) = p.tasks
    assert p.members[0].display.role == role
    assert field(t, "outing").value is True and qual(t, "confirmed-execution").eligible
    assert field(t, "elapsed_seconds").value == 1250
    assert field(t, "elapsed_seconds").claims[-1].tier == "confirmed-display"
    assert field(t, "tolerance").value == "comfortable"
    assert report.confirmations[0].history[-1].command == receipt.command
    for purpose in ("comparable-running", "progression-review-input"):
        q = qual(t, purpose)
        assert q.eligible == eligible
        assert q.missing == (() if eligible else ("running-role",))
        assert q.exclusions == ()


@pytest.mark.parametrize("dimension", ["movement", "variation", "equipment", "group", None])
def test_review_strength_dimensions(
    db: Session, plans: PlanCommands, dimension: str | None
) -> None:
    src = account(db, PREVIEW_OWNER, "hevy")
    lift(db, src, 0, "press", [("press", [("normal", 5, True)])])
    db.commit()
    scope = e.Scope(start=PERIOD.start, stop=PERIOD.stop, strength_account=src.id)
    member = query_planning_evidence(db.get_bind(), scope).performances[0].members[0]
    ctx = context(member)
    if dimension:
        ctx = ctx.model_copy(update={dimension: "unknown"})
    scope = scope.model_copy(update={"contexts": (ctx,)})
    fact = query_planning_evidence(db.get_bind(), scope).performances[0].members[0].display
    display = plans.preview_observations(src.id, (fact,))
    plans.confirm_observations(uuid4(), c.prepare(display, ("reps", "kg")), current=(fact,))
    db.commit()
    t = query_planning_evidence(db.get_bind(), scope).performances[0].tasks[0]
    assert field(t, "reps").value == 5 and field(t, "kg").value == 60
    assert qual(t, "confirmed-execution").eligible
    q = qual(t, "comparable-strength")
    assert q.eligible == (dimension is None)
    assert q.missing == ((dimension,) if dimension else ()) and q.exclusions == ()


@pytest.mark.parametrize("count", [4, 3])
def test_review_interval_duration_coverage(db: Session, cycle: Cycle, count: int) -> None:
    steps = tuple(
        actual.StepExecution(index=i, purpose="work", status="completed", elapsed_seconds=240)
        for i in (2, 4, 6)
    )
    outcome = cycle.record(
        "cruise",
        actual.RunExecution(
            role="controlled",
            status="completed",
            confirmed_outing=True,
            elapsed_seconds=2100,
            manageable=True,
            completed_work_repetitions=count,
            steps=steps,
        ),
    )
    db.commit()
    day = cycle.session("cruise").day
    report = query_planning_evidence(
        db.get_bind(), e.Scope(start=day, stop=day + timedelta(days=1))
    )
    (p,) = report.performances
    (t,) = p.tasks
    assert p.manual.history[-1].id == outcome and p.manual.history[-1].actual.steps == steps
    assert field(t, "completed_work_repetitions").value == count
    assert (
        field(t, "elapsed_seconds").value == 2100 and field(t, "session_manageable").value is True
    )
    assert [
        f.value
        for f in t.fields
        if f.name.startswith("step.") and f.name.endswith(".elapsed_seconds")
    ] == [240] * 3
    assert qual(t, "confirmed-execution").eligible
    for purpose in ("comparable-running", "familiar-dose-input", "progression-review-input"):
        q = qual(t, purpose)
        assert q.eligible == (count == 3)
        assert q.missing == (() if count == 3 else ("aligned-work-durations",))
        assert q.exclusions == (
            ()
            if count == 3
            else ("3 of 4 reported work repetitions have aligned achieved durations",)
        )


def test_review_outing_enumeration(db: Session, plans: PlanCommands) -> None:
    scope, receipt = confirmed_run(db, plans, "easy", ("elapsed_seconds",))
    ledger = db.scalars(
        select(GarminCoverage).where(GarminCoverage.source_account_id == scope.endurance_account)
    ).one()
    for status in ("partial", "empty"):
        if status == "empty":
            ledger.status, ledger.eligible_count, ledger.last_success = (
                "empty",
                0,
                ledger.attempted_at,
            )
            db.commit()
        report = query_planning_evidence(db.get_bind(), scope)
        day = report.days[0]
        task = report.performances[0].tasks[0]
        reasons = () if status == "partial" else ("retained_after_empty",)
        assert day.discrepancies == reasons
        assert day.running_count_status == (
            "lower_bound" if status == "partial" else "observed_only"
        )
        assert day.running_count == 1 and qual(task, "descriptive-exposure").eligible
        assert field(task, "outing").state == "source-only" and field(task, "outing").value is True
        assert (
            field(task, "elapsed_seconds").value == 1250
            and field(task, "tolerance").value == "comfortable"
        )
        assert report.confirmations[0].confirmed == (("elapsed_seconds", 1250),)
        assert plans.confirmation_receipt(receipt.command) == receipt
        for purpose in ("confirmed-execution", "comparable-running", "progression-review-input"):
            q = qual(task, purpose)
            assert q.eligible == (status == "partial")
            assert q.exclusions == reasons

    # A separate assertion about the outing itself supplies the disputed execution input.
    fact = report.performances[0].members[0].display
    display = plans.preview_observations(scope.endurance_account, (fact,))
    answer = c.Answer(
        member=fact.member,
        disposition="confirm",
        fields=("outing", "elapsed_seconds"),
        reported=c.AthleteReport(tolerance="comfortable"),
        supersedes=receipt.command,
    )
    plans.confirm_observations(
        uuid4(), c.prepare(display, (), exceptions=(answer,)), current=(fact,)
    )
    db.commit()
    affirmed = query_planning_evidence(db.get_bind(), scope)
    assert affirmed.days[0].discrepancies == ("retained_after_empty",)
    assert affirmed.days[0].running_count_status == "observed_only"
    assert affirmed.confirmations[0].history[0].command == receipt.command
    task = affirmed.performances[0].tasks[0]
    assert field(task, "outing").state == "actual" and field(task, "outing").value is True
    for purpose in ("confirmed-execution", "comparable-running", "progression-review-input"):
        q = qual(task, purpose)
        assert q.eligible and q.exclusions == ()


def test_review_manual_set_exposure(db: Session, cycle: Cycle) -> None:
    done = partial_strength().sets[1]
    skipped = done.model_copy(
        update={
            "ordinal": 2,
            "status": "not-performed",
            "reps": None,
            "kg": None,
            "achieved_rpe": None,
        }
    )
    session = actual.StrengthExecution(status="partial", sets=(done, skipped))
    outcome = cycle.record("gym-a", session)
    db.commit()
    day = cycle.session("gym-a").day
    (p,) = query_planning_evidence(
        db.get_bind(), e.Scope(start=day, stop=day + timedelta(days=1))
    ).performances
    assert p.execution_state == "partial" and p.manual.history[-1].id == outcome
    assert p.manual.history[-1].actual == session
    assert [t.manual_set for t in p.tasks] == [done, skipped]
    for task in p.tasks:
        performed = task.manual_set == done
        assert field(task, "status").value == ("completed" if performed else "not-performed")
        assert field(task, "status").claims[-1].support == outcome
        assert field(task, "reps").value == (5 if performed else None)
        assert field(task, "session_status").value == "partial"
        q = qual(task, "descriptive-exposure")
        assert q.eligible == performed
        assert q.missing == (() if performed else ("performed-set",))
        assert q.exclusions == ()

"""Synthetic batch rehearsal. The supplied projection never calls a provider."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fitness_intelligence.db.confirmation_models import ConfirmationMember, ConfirmationReceipt
from fitness_intelligence.db.familiar_snapshot import PREVIEW_OWNER
from fitness_intelligence.db.models import ExerciseSet, User, Workout, WorkoutExercise
from fitness_intelligence.db.plan_commands import PlanCommands
from fitness_intelligence.db.plan_models import SessionOutcome
from fitness_intelligence.planning import confirmation as c
from fitness_intelligence.planning.familiar_outcomes import StepExecution

CONFIG = Path(__file__).parents[1] / "alembic.ini"


@pytest.fixture
def cmd(db: Session, monkeypatch: pytest.MonkeyPatch) -> PlanCommands:
    db.add(User(id=PREVIEW_OWNER))
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(PREVIEW_OWNER))
    return PlanCommands(db)


@pytest.fixture
def sets() -> tuple[c.StrengthFact, ...]:
    account = uuid4()
    facts = []
    for day in (3, 5):
        workout, exercise, ref = uuid4(), uuid4(), uuid4()
        for ordinal in (1, 2, 3):
            facts.append(
                c.StrengthFact(
                    owner=PREVIEW_OWNER,
                    account=account,
                    workout=workout,
                    reference=ref,
                    occurred_at=datetime(2025, 2, day, 12, tzinfo=UTC),
                    exercise=exercise,
                    member=uuid4(),
                    movement="press",
                    variation="standing",
                    equipment="barbell",
                    load_convention="total-external-kg",
                    group="primary",
                    kind="working",
                    ordinal=ordinal,
                    reps=5,
                    kg=Decimal("40.0"),
                    provenance="historically-inferred",
                    mapping="exercise-v1",
                    comparison="press-v1",
                )
            )
    return tuple(facts)


def selected(display: c.Display, overrides: dict[UUID, dict] | None = None) -> c.Intent:
    overrides = overrides or {}
    answers = []
    for fact in display.members:
        args = {"disposition": "confirm", "fields": tuple(fact.eligible)}
        answers.append(c.Answer(member=fact.member, **(args | overrides.get(fact.member, {}))))
    return c.Intent(display=display, displayed_digest=display.digest, answers=tuple(answers))


def test_batch_rehearsal(cmd: PlanCommands, sets: tuple, db: Session) -> None:
    a, b, d, e, excluded, uncertain = sets
    display = cmd.preview_observations(a.account, sets[::-1])
    assert display.members == sets and display == cmd.preview_observations(a.account, sets)
    assert display.offers[0].fields == ("completion", "kg", "reps")
    intent = selected(
        display,
        {
            b.member: dict(fields=("completion",)),
            excluded.member: dict(disposition="exclude", fields=()),
            uncertain.member: dict(disposition="uncertain", fields=()),
        },
    )
    key = uuid4()
    root = cmd.confirm_observations(key, intent, current=sets)
    assert root.actor == PREVIEW_OWNER and root.intent_digest == c.digest(intent)
    assert db.scalar(select(func.count()).select_from(ConfirmationMember)) == 6
    assert db.scalar(select(func.count()).select_from(ConfirmationReceipt)) == 1
    assert db.scalar(select(func.count()).select_from(Workout)) == 0
    assert db.scalar(select(func.count()).select_from(SessionOutcome)) == 0
    review = cmd.confirmation_review(key, current=sets)
    assert [x.state for x in review] == ["confirmed"] * 4 + ["excluded", "uncertain"]
    assert review[0].confirmed == {"completion": True, "kg": Decimal("40.0"), "reps": 5}
    assert review[1].unconfirmed == ("kg", "reps") and review[1].confirmed == {"completion": True}
    assert all(x.independent_report is None for x in review)
    assert all(x.history[0].source.completed_at is None for x in review)
    assert all(x.history[0].source.provenance == "historically-inferred" for x in review)

    # Correct only A. Confirm displayed load, independently report four reps and set RPE.
    single = cmd.preview_observations(a.account, (a,))
    correction = selected(
        single,
        {
            a.member: dict(
                supersedes=key,
                fields=("completion", "kg"),
                reported=c.AthleteReport(reps=4, set_rpe=Decimal(7)),
            )
        },
    )
    newer = cmd.confirm_observations(uuid4(), correction, current=(a,))
    changed = d.model_copy(update={"reps": 3})
    current = (a, b, changed, e, excluded, uncertain)
    revised = cmd.confirmation_review(key, current=current)
    assert [h.command for h in revised[0].history] == [key, newer.command]
    assert revised[0].confirmed == {"completion": True, "kg": Decimal(40)}
    assert revised[0].independent_report.reps == 4 and revised[0].independent_report.set_rpe == 7
    assert revised[2].state == "stale" and revised[2].confirmed == {}
    assert revised[2].history[0].source.reps == 5 and changed.reps == 3
    assert revised[1] == review[1] and revised[3:] == review[3:]
    assert cmd.confirmation_receipt(key) == root
    assert cmd.confirm_observations(key, intent, current=()) == root
    with pytest.raises(ValueError, match="different intent"):
        cmd.confirm_observations(key, correction, current=(a,))
    with pytest.raises(ValueError, match="current assertion"):
        cmd.confirm_observations(uuid4(), correction, current=(a,))


@pytest.mark.parametrize(
    "change",
    [
        {"deleted": True},
        {"reference_active": False},
        {"member": uuid4()},
        {"reference": uuid4()},
        {"mapping": "exercise-v2"},
        {"comparison": "other"},
        {"revision": "replaced"},
        {"exercise": uuid4()},
    ],
)
def test_invalidated_member_and_withdrawal(cmd: PlanCommands, sets: tuple, change: dict) -> None:
    a, b = sets[0], sets[-1]
    display = cmd.preview_observations(a.account, (a, b))
    root = cmd.confirm_observations(uuid4(), selected(display), current=(a, b))
    changed = a.model_copy(update=change)
    first, other = cmd.confirmation_review(root.command, current=(changed, b))
    assert first.state == "stale" and first.reason and other.state == "confirmed"
    withdraw = selected(
        cmd.preview_observations(a.account, (a,)),
        {a.member: dict(disposition="withdraw", fields=(), supersedes=root.command)},
    )
    cmd.confirm_observations(uuid4(), withdraw, current=())
    first, same = cmd.confirmation_review(root.command, current=(b,))
    assert same == other and first.state == "withdrawn" and first.confirmed == {}
    assert first.history[0].answer.disposition == "confirm"


def test_changed_display_and_permissions(
    cmd: PlanCommands, sets: tuple, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    a = sets[0]
    display = cmd.preview_observations(a.account, (a,))
    intent = selected(display)
    for attr, val in (
        ("kg", Decimal(41)),
        ("member", uuid4()),
        ("owner", uuid4()),
        ("account", uuid4()),
    ):
        with pytest.raises(ValueError):
            cmd.confirm_observations(uuid4(), intent, current=(a.model_copy(update={attr: val}),))
    with pytest.raises(ValueError, match="duplicate"):
        cmd.preview_observations(a.account, (a, a))
    with pytest.raises(ValueError, match="duplicate exercise"):
        cmd.preview_observations(a.account, (a, a.model_copy(update={"member": uuid4()})))
    with pytest.raises(ValidationError, match="answer each"):
        c.Intent(display=display, displayed_digest=display.digest, answers=())
    with pytest.raises(ValidationError, match="digest differs"):
        c.Intent(display=display, displayed_digest="a" * 64, answers=intent.answers)
    with pytest.raises(ValidationError, match="session RPE"):
        selected(display, {a.member: dict(reported=c.AthleteReport(session_rpe=Decimal(6)))})
    assert db.scalar(select(func.count()).select_from(ConfirmationReceipt)) == 0
    root = cmd.confirm_observations(uuid4(), intent, current=(a,))
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(uuid4()))
    foreign = PlanCommands(db)
    for action in (
        lambda: foreign.confirmation_receipt(root.command),
        lambda: foreign.preview_observations(a.account, (a,)),
        lambda: foreign.confirmation_review(root.command, current=(a,)),
        lambda: foreign.confirm_observations(uuid4(), intent, current=(a,)),
    ):
        with pytest.raises(PermissionError):
            action()


def test_running_scope(cmd: PlanCommands, sets: tuple) -> None:
    a = sets[0]
    run = c.RunningFact(
        owner=a.owner,
        account=uuid4(),
        workout=uuid4(),
        reference=uuid4(),
        occurred_at=a.occurred_at,
        mapping="running-v1",
        comparison="controlled",
        role="controlled",
        provenance="activity-summary",
        instructions=("3 x 360 s",),
        elapsed_seconds=2400,
    )
    display = cmd.preview_observations(run.account, (run,))
    assert display.offers[0].fields == ("elapsed_seconds", "outing")
    with pytest.raises(ValidationError, match="absent or ineligible"):
        selected(display, {run.member: dict(fields=("step.2.status",))})
    with pytest.raises(ValidationError, match="outside outing"):
        selected(display, {run.member: dict(reported=c.AthleteReport(set_rpe=Decimal(5)))})
    intent = selected(
        display,
        {
            run.member: dict(
                fields=("outing",),
                reported=c.AthleteReport(session_rpe=Decimal(6), tolerance="comfortable"),
            )
        },
    )
    root = cmd.confirm_observations(uuid4(), intent, current=(run,))
    (support,) = cmd.confirmation_review(root.command, current=(run,))
    assert support.confirmed == {"outing": True}
    assert support.history[0].source.achieved_steps == ()
    step = StepExecution(index=2, purpose="work", status="completed", elapsed_seconds=330)
    measured = run.model_copy(update={"achieved_steps": (step,)})
    new = selected(
        cmd.preview_observations(run.account, (measured,)),
        {run.member: dict(supersedes=root.command)},
    )
    cmd.confirm_observations(uuid4(), new, current=(measured,))
    (support,) = cmd.confirmation_review(root.command, current=(measured,))
    assert support.confirmed["step.2.status"] == "completed"
    assert support.confirmed["step.2.elapsed_seconds"] == 330
    assert "step.2.achieved_rpe" not in support.confirmed
    only_time = c.prepare(new.display, ("step.2.elapsed_seconds",))
    assert only_time.answers[0].fields == ("step.2.elapsed_seconds",)


def test_concurrent_corrections(db: Session, cmd: PlanCommands, sets: tuple) -> None:
    a = sets[0]
    display = cmd.preview_observations(a.account, (a,))
    root = cmd.confirm_observations(uuid4(), selected(display), current=(a,))
    db.commit()
    engine = db.get_bind()
    barrier = Barrier(2)

    def correct(field: str) -> bool:
        intent = selected(display, {a.member: dict(supersedes=root.command, fields=(field,))})
        with Session(engine) as session, session.begin():
            barrier.wait(timeout=10)
            try:
                PlanCommands(session).confirm_observations(uuid4(), intent, current=(a,))
                return True
            except ValueError as error:
                assert "current assertion" in str(error)
                return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(correct, ("reps", "kg"))) == [False, True]
    (support,) = cmd.confirmation_review(root.command, current=(a,))
    assert len(support.history) == 2


def test_storage_guards(db: Session, cmd: PlanCommands, sets: tuple) -> None:
    config = Config(str(CONFIG))
    db.commit()
    command.downgrade(config, "e421")
    command.upgrade(config, "head")
    a, b = sets[:2]
    root = cmd.confirm_observations(
        uuid4(), selected(cmd.preview_observations(a.account, (a, b))), current=(a, b)
    )
    db.commit()
    with pytest.raises(RuntimeError, match="preserve scoped confirmation"):
        command.downgrade(config, "e421")
    assert cmd.confirmation_receipt(root.command) == root
    for table in ("confirmation_receipts", "confirmation_members"):
        for sql in (
            f"DELETE FROM {table}",
            f"UPDATE {table} SET command=command",
            f"TRUNCATE {table} CASCADE",
        ):
            with pytest.raises(IntegrityError), db.begin_nested():
                db.execute(text(sql))
    with pytest.raises(IntegrityError), db.begin_nested():
        db.add(
            ConfirmationMember(
                user_id=a.owner,
                account=a.account,
                workout=a.workout,
                member=uuid4(),
                command=root.command,
            )
        )
        db.flush()
    for updated in ({"schema_version": 2}, {"answers": []}):
        with pytest.raises(IntegrityError), db.begin_nested():
            db.add(
                ConfirmationReceipt(
                    user_id=a.owner,
                    actor=a.owner,
                    command=uuid4(),
                    recorded_at=root.recorded_at,
                    intent_digest=root.intent_digest,
                    payload=root.intent.model_dump(mode="json") | updated,
                )
            )
            db.flush()


def test_bulk_mask_and_canonical_source_unchanged(
    cmd: PlanCommands, db: Session, sets: tuple
) -> None:
    a, b = sets[:2]
    workout = Workout(
        id=a.workout, user_id=a.owner, title="Synthetic press", started_at=a.occurred_at
    )
    db.add(workout)
    db.flush()
    exercise = WorkoutExercise(
        id=a.exercise, workout_id=a.workout, user_id=a.owner, position=0, name="Synthetic press"
    )
    db.add(exercise)
    db.flush()
    for position, fact in enumerate((a, b)):
        db.add(
            ExerciseSet(
                id=fact.member,
                user_id=a.owner,
                exercise_id=a.exercise,
                position=position,
                repetitions=fact.reps,
                weight_kg=fact.kg,
                kind="normal",
            )
        )
    db.flush()
    display = cmd.preview_observations(a.account, (a, b))
    intent = c.prepare(
        display,
        ("reps", "kg", "completion"),
        exceptions=(c.Answer(member=b.member, disposition="uncertain"),),
    )
    root = cmd.confirm_observations(uuid4(), intent, current=(a, b))
    db.commit()
    assert cmd.confirmation_review(root.command, current=(a, b))[0].confirmed["reps"] == 5
    source = db.get(ExerciseSet, a.member)
    assert (source.repetitions, source.weight_kg, source.completed_at, source.rpe) == (
        5,
        Decimal(40),
        None,
        None,
    )
    with pytest.raises(ValueError, match="outside displayed"):
        c.prepare(
            display, ("completion",), exceptions=(c.Answer(member=uuid4(), disposition="exclude"),)
        )


def test_member_lineage_and_wire_version(db: Session, cmd: PlanCommands, sets: tuple) -> None:
    a, b = sets[0], sets[-1]

    def confirm_one(fact: c.Fact) -> c.Receipt:
        return cmd.confirm_observations(
            uuid4(),
            c.prepare(cmd.preview_observations(fact.account, (fact,)), ("completion",)),
            current=(fact,),
        )

    first = confirm_one(a)
    unrelated = confirm_one(b)
    scope = first.intent.display
    wrong = selected(scope, {a.member: dict(supersedes=unrelated.command)})
    with pytest.raises(IntegrityError), db.begin_nested():
        db.add(
            ConfirmationReceipt(
                user_id=a.owner,
                actor=a.owner,
                command=uuid4(),
                recorded_at=unrelated.recorded_at,
                intent_digest=c.digest(wrong),
                payload=wrong.model_dump(mode="json"),
            )
        )
        db.flush()
    assert db.scalar(select(func.count()).select_from(ConfirmationReceipt)) == 2
    for change in ({"account": uuid4()}, {"workout": uuid4()}):
        moved = a.model_copy(update=change)
        intent = selected(
            cmd.preview_observations(moved.account, (moved,)),
            {a.member: dict(supersedes=first.command)},
        )
        with pytest.raises(ValueError, match="source identity"):
            cmd.confirm_observations(uuid4(), intent, current=(moved,))
    with pytest.raises(ValidationError):
        c.Intent.model_validate_json(
            first.intent.model_dump_json().replace('"schema_version":1', '"schema_version":7')
        )

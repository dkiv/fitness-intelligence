"""E4.2A synthetic execution rehearsals on isolated PostgreSQL schemas."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from fitness_intelligence.db.execution import OutcomeConflict
from fitness_intelligence.db.familiar_snapshot import PREVIEW_OWNER
from fitness_intelligence.db.models import User
from fitness_intelligence.db.plan_commands import PlanCommands
from fitness_intelligence.db.plan_models import SessionOutcome
from fitness_intelligence.db.plan_snapshot import Generate, PlanningContext
from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning import familiar_outcomes as fo
from fitness_intelligence.planning.familiar_examples import example
from fitness_intelligence.planning.outcomes import Actual
from fitness_intelligence.planning.planner import Slot
from fitness_intelligence.planning.press_block import Availability, PressBlock

CONFIG = Path(__file__).parents[1] / "alembic.ini"


def at(day: int) -> datetime:
    return datetime(2027, 1, day, 12, tzinfo=UTC)


@dataclass
class Cycle:
    cmd: PlanCommands
    plan: UUID
    block: UUID
    weeks: tuple[UUID, ...]
    now: datetime

    def session(self, template: str, week: int = 1) -> f.Session:
        p = self.cmd.preview(self.plan, self.weeks[week - 1])
        return next(s for day in p.candidate.days for s in day.sessions if s.template == template)

    def record(self, template: str, actual: fo.Execution, week: int = 1, **kwargs) -> UUID:
        s = self.session(template, week)
        return self.cmd.record_outcome(
            self.plan,
            self.weeks[week - 1],
            week,
            s.occurrence,
            actual,
            **({"occurred_at": s.start_utc, "command_id": uuid4()} | kwargs),
        )


@pytest.fixture
def cycle(db: Session, monkeypatch: pytest.MonkeyPatch) -> Cycle:
    db.add(User(id=PREVIEW_OWNER))
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(PREVIEW_OWNER))
    cmd = PlanCommands(db)
    block, ctx = example("running")
    c = Cycle(cmd, UUID(int=0), UUID(int=0), (), at(2))
    monkeypatch.setattr(PlanCommands, "_now", lambda _: c.now)
    cmd.capture_context(ctx, expected_context=None)
    c.plan = cmd.create_cycle(block)
    head = None
    for request, day in (
        (f.ProposeBlock(), 2),
        (f.FamiliarWeek(number=1), 2),
        (f.FamiliarWeek(number=2), 6),
        (f.FamiliarWeek(number=3), 7),
    ):
        c.now = at(day)
        rev = cmd.submit(c.plan, head, request)
        cmd.decide(c.plan, rev, expected_head=head, choice="approve", command_id=uuid4())
        if isinstance(request, f.ProposeBlock):
            c.block = rev
        else:
            c.weeks = (*c.weeks, rev)
        head = rev
    c.now = at(12)
    db.commit()
    return c


def part(movement: str, group: str, ordinal: int, **actual) -> fo.SetExecution:
    return fo.SetExecution(
        movement=movement,
        variation="standing",
        equipment="barbell",
        group=group,
        kind="warmup" if group == "prepare" else "working",
        ordinal=ordinal,
        **actual,
    )


def partial_strength() -> fo.StrengthExecution:
    return fo.StrengthExecution(
        status="partial",
        manageable=False,
        feedback="Stopped after squat",
        sets=(
            part(
                "press",
                "prepare",
                1,
                status="completed",
                reps=5,
                kg=Decimal(20),
                load_convention="total-external-kg",
            ),
            part(
                "press",
                "primary",
                1,
                status="completed",
                reps=5,
                kg=Decimal(42),
                load_convention="total-external-kg",
                achieved_rpe=Decimal(9),
            ),
            part("press", "backoff", 1, status="completed"),
            part("squat", "primary", 1, status="partial", reps=3),
        ),
    )


def test_late_reports_and_weekly_work(db: Session, cycle: Cycle) -> None:
    early = cycle.cmd.weekly_review(cycle.plan, 1, as_of=at(3))
    assert early.known_coverage is early.completion_among_known is None
    assert all(not s.elapsed for s in early.sessions)
    assert cycle.cmd.weekly_review(cycle.plan, 1, as_of=at(7)).known_coverage == 0
    assert cycle.cmd.weekly_review(cycle.plan, 1, as_of=at(7)).completion_among_known is None
    root = cycle.record("gym-a", partial_strength())
    cycle.record(
        "easy",
        fo.RunExecution(
            role="easy",
            status="completed",
            confirmed_outing=True,
            elapsed_seconds=1200,
            distance_metres=Decimal(2300),
        ),
    )
    cycle.record(
        "cruise",
        fo.RunExecution(
            role="controlled",
            status="completed",
            confirmed_outing=True,
            elapsed_seconds=1900,
            moving_seconds=1800,
            session_rpe=Decimal(6),
        ),
    )
    cycle.record(
        "long",
        fo.RunExecution(role="long", status="missed", confirmed_outing=False, feedback="Travel"),
    )
    r = cycle.cmd.weekly_review(cycle.plan, 1)
    gym, easy, cruise, long = r.sessions
    assert (
        r.owner,
        r.cycle,
        r.block_key,
        r.block_revision,
        r.week,
        r.origin_revision,
        r.calendar_head,
    ) == (
        PREVIEW_OWNER,
        cycle.plan,
        "familiar-block",
        cycle.block,
        1,
        cycle.weeks[0],
        cycle.weeks[2],
    )
    assert gym.effective.id == root and gym.effective.effective_head == cycle.weeks[0]
    assert cruise.effective.effective_head == cycle.weeks[2]
    assert (
        cruise.effective.actual.steps == ()
        and cruise.effective.actual.completed_work_repetitions is None
    )
    assert easy.effective.actual.manageable is easy.effective.actual.session_rpe is None
    assert [s.reps for s in r.reported_sets] == [5, 5, None, 3]
    assert r.reported_sets[-1].kg is r.reported_sets[-1].achieved_rpe is None
    assert len(r.reported_outings) == 2
    assert r.counts() == {"completed": 2, "partial": 1, "missed": 1, "unknown": 0}
    assert r.known_coverage == 1 and r.completion_among_known == Decimal("0.5")
    assert any("exceeded cap 8" in d for d in gym.differences)
    assert any("kg 42 outside" in d for d in gym.differences)
    assert gym.effective.occurred_at < gym.effective.recorded_at
    assert long.effective.actual.feedback == "Travel"
    db.commit()
    with db.begin():
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
        assert cycle.cmd.weekly_review(cycle.plan, 1) == r


def test_interval_detail_correction_and_historical_render(cycle: Cycle) -> None:
    summary = fo.RunExecution(
        status="partial", role="controlled", confirmed_outing=True, elapsed_seconds=1300
    )
    key = uuid4()
    root = cycle.record("cruise", summary, command_id=key)
    first = cycle.cmd.weekly_review(cycle.plan, 1)
    assert first.counts()["unknown"] == 3 and first.known_coverage == Decimal("0.25")
    detailed = fo.RunExecution(
        status="partial",
        role="controlled",
        confirmed_outing=True,
        elapsed_seconds=1300,
        completed_work_repetitions=1,
        session_rpe=Decimal(6),
        steps=(
            fo.StepExecution(
                index=2,
                purpose="work",
                status="completed",
                elapsed_seconds=250,
                achieved_rpe=Decimal(8),
            ),
            fo.StepExecution(index=3, purpose="recovery", status="completed", elapsed_seconds=90),
            fo.StepExecution(index=4, purpose="work", status="partial", elapsed_seconds=60),
        ),
    )
    cycle.now = at(13)
    newkey = uuid4()
    latest = cycle.record("cruise", detailed, supersedes_id=root, command_id=newkey)
    assert cycle.record("cruise", summary, command_id=key) == root
    assert cycle.record("cruise", detailed, supersedes_id=root, command_id=newkey) == latest
    with pytest.raises(OutcomeConflict, match="different intent"):
        cycle.record("cruise", detailed, command_id=key)
    with pytest.raises(OutcomeConflict, match="current slot"):
        cycle.record("cruise", summary, supersedes_id=root)
    current = cycle.cmd.weekly_review(cycle.plan, 1)
    slot = current.sessions[2]
    assert [a.id for a in slot.history] == [root, latest] and slot.effective.supersedes_id == root
    assert slot.effective.actual.steps[1].achieved_rpe is None
    assert any("1 work repetitions vs 3" in msg for msg in slot.differences)
    assert any("step 2 (work) RPE 8 exceeded cap 7" in msg for msg in slot.differences)
    assert current.reported_outings == (detailed,)
    assert cycle.cmd.weekly_review(cycle.plan, 1, as_of=at(12)) == first
    rendered = fo.render_execution_review(current)
    assert f"superseded {root}" in rendered and f"effective {latest}" in rendered
    assert "superseded" not in fo.render_execution_review(first)


def test_later_week_unknown_and_explicit_miss(cycle: Cycle) -> None:
    cycle.now = at(21)
    unknown = fo.StrengthExecution(status="unknown", feedback="Unsure")
    root = cycle.record("gym-a", unknown, week=3)
    cycle.record(
        "easy", fo.RunExecution(status="missed", role="easy", confirmed_outing=False), week=3
    )
    r = cycle.cmd.weekly_review(cycle.plan, 3)
    assert r.origin_revision == cycle.weeks[2] and r.sessions[0].effective.id == root
    assert r.counts() == {"unknown": 1, "completed": 0, "partial": 0, "missed": 1}
    assert [s.elapsed for s in r.sessions] == [True, True, False, False]
    assert r.known_coverage == Decimal("0.5") and r.completion_among_known == 0


def test_invalid_attribution_and_duplicate_performance(
    db: Session, cycle: Cycle, monkeypatch: pytest.MonkeyPatch
) -> None:
    cmd = cycle.cmd
    pending = cmd.submit(cycle.plan, cycle.weeks[2], f.FamiliarWeek(number=4))
    other_plan = cmd.create_cycle(example("running")[0])
    s = cycle.session("gym-a")
    for revision, week, slot, instant in (
        (pending, 1, s.occurrence, s.start_utc),
        (cycle.block, 1, s.occurrence, s.start_utc),
        (cycle.weeks[2], 1, s.occurrence, s.start_utc),
        (cycle.weeks[0], 1, uuid4(), s.start_utc),
        (cycle.weeks[0], 2, s.occurrence, s.start_utc),
        (cycle.weeks[0], 1, s.occurrence, at(1)),
        (cycle.weeks[0], 1, s.occurrence, at(11)),
    ):
        with pytest.raises(ValueError):
            cmd.record_outcome(
                cycle.plan,
                revision,
                week,
                slot,
                partial_strength(),
                occurred_at=instant,
                command_id=uuid4(),
            )
    with pytest.raises(OutcomeConflict):
        cmd.record_outcome(
            other_plan,
            cycle.weeks[0],
            1,
            s.occurrence,
            partial_strength(),
            occurred_at=s.start_utc,
            command_id=uuid4(),
        )
    with pytest.raises(ValueError, match="scheduled instant"):
        cycle.record(
            "gym-a",
            fo.StrengthExecution(status="missed"),
            occurred_at=s.start_utc + timedelta(minutes=1),
        )
    with pytest.raises(ValueError, match="elapsed aware"):
        cycle.record("gym-a", partial_strength(), occurred_at=at(13))
    with pytest.raises(ValueError, match="deferred"):
        cycle.record("gym-a", partial_strength(), workout_id=uuid4())
    with pytest.raises(ValueError, match="matching exercise"):
        cycle.record(
            "gym-a",
            fo.StrengthExecution(
                status="partial", sets=(part("squat", "other", 1, status="partial"),)
            ),
        )
    cycle.record("gym-a", partial_strength())
    with pytest.raises(OutcomeConflict, match="already attributed"):
        cycle.record(
            "easy",
            fo.RunExecution(status="completed", role="easy", confirmed_outing=True),
            occurred_at=s.start_utc,
        )
    with pytest.raises(ValueError, match="prescribed running role"):
        cycle.record(
            "easy", fo.RunExecution(status="completed", role="long", confirmed_outing=True)
        )
    with pytest.raises(ValueError, match="expanded index"):
        cycle.record(
            "easy",
            fo.RunExecution(
                status="partial",
                role="easy",
                confirmed_outing=True,
                steps=(fo.StepExecution(index=2, purpose="work", status="completed"),),
            ),
        )
    other = User()
    db.add(other)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(other.id))
    with pytest.raises(NoResultFound):
        PlanCommands(db).weekly_review(cycle.plan, 1)
    with pytest.raises(NoResultFound):
        PlanCommands(db).record_outcome(
            cycle.plan,
            cycle.weeks[0],
            1,
            s.occurrence,
            partial_strength(),
            occurred_at=s.start_utc,
            command_id=uuid4(),
        )


def test_concurrent_corrections(db: Session, cycle: Cycle) -> None:
    root = cycle.record("gym-a", partial_strength())
    s = cycle.session("gym-a")
    db.commit()
    engine = db.get_bind()
    barrier = Barrier(2)

    def correct(reps: int) -> bool:
        with Session(engine) as conn, conn.begin():
            barrier.wait(timeout=10)
            try:
                PlanCommands(conn).record_outcome(
                    cycle.plan,
                    cycle.weeks[0],
                    1,
                    s.occurrence,
                    fo.StrengthExecution(
                        status="partial",
                        sets=(part("squat", "primary", 1, status="partial", reps=reps),),
                    ),
                    occurred_at=s.start_utc,
                    supersedes_id=root,
                    command_id=uuid4(),
                )
                return True
            except OutcomeConflict:
                return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(correct, (2, 3))) == [False, True]
    history = cycle.cmd.weekly_review(cycle.plan, 1).sessions[0].history
    assert len(history) == 2 and history[1].supersedes_id == root


def test_direct_sql_scope_immutability_and_downgrade(db: Session, cycle: Cycle) -> None:
    gym = cycle.session("gym-a")
    base = dict(
        user_id=PREVIEW_OWNER,
        plan_id=cycle.plan,
        revision_id=cycle.weeks[0],
        origin_revision_id=cycle.weeks[0],
        week=1,
        slot=str(gym.occurrence),
        outcome_version=2,
        actual=partial_strength().model_dump(mode="json"),
        occurred_at=gym.start_utc,
        recorded_at=at(12),
    )
    pending = cycle.cmd.submit(cycle.plan, cycle.weeks[2], f.FamiliarWeek(number=4))
    other_owner = User()
    db.add(other_owner)
    db.flush()
    other_plan = cycle.cmd.create_cycle(example("running")[0])
    for overrides in (
        dict(user_id=other_owner.id),
        dict(plan_id=other_plan),
        dict(origin_revision_id=None),
        dict(week=4),
        dict(slot=str(uuid4())),
        dict(origin_revision_id=pending),
        dict(revision_id=cycle.weeks[2]),
        dict(origin_revision_id=cycle.weeks[2]),
        dict(outcome_version=1),
        dict(outcome_version=3),
        dict(workout_id=uuid4()),
        dict(occurred_at=at(11), revision_id=cycle.weeks[2]),
        dict(actual=Actual(status="partial").model_dump(mode="json")),
        dict(
            actual=fo.StrengthExecution(status="missed").model_dump(mode="json"),
            occurred_at=gym.start_utc + timedelta(seconds=1),
        ),
    ):
        with pytest.raises(IntegrityError), db.begin_nested():
            db.add(SessionOutcome(**(base | overrides), command_id=uuid4()))
            db.flush()
    root = cycle.record("gym-a", partial_strength())
    easy = cycle.session("easy")
    with pytest.raises(IntegrityError), db.begin_nested():
        db.add(
            SessionOutcome(
                **(
                    base
                    | dict(
                        slot=str(easy.occurrence),
                        actual=fo.RunExecution(
                            status="partial", role="easy", confirmed_outing=True
                        ).model_dump(mode="json"),
                    )
                ),
                command_id=uuid4(),
            )
        )
        db.flush()
    for sql in (
        "UPDATE session_outcomes SET week=2",
        "DELETE FROM session_outcomes",
        "TRUNCATE session_outcomes",
    ):
        with pytest.raises(IntegrityError), db.begin_nested():
            db.execute(text(sql))
    db.commit()
    with pytest.raises(RuntimeError, match="preserve history"):
        command.downgrade(Config(str(CONFIG)), "b330")
    assert db.get(SessionOutcome, root).origin_revision_id == cycle.weeks[0]


def test_migration_preserves_populated_legacy_execution(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = Config(str(CONFIG))
    command.downgrade(config, "b330")
    user = User()
    db.add(user)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(user.id))
    monkeypatch.setattr(PlanCommands, "_now", lambda _: at(2))
    cmd = PlanCommands(db)
    cmd.capture_context(PlanningContext(Availability()), expected_context=None)
    plan = cmd.create_cycle(PressBlock())
    rev = cmd.submit(plan, None, Generate(1))
    cmd.decide(plan, rev, expected_head=None, choice="approve", command_id=uuid4())
    ident, key = uuid4(), uuid4()
    actual = Actual(status="partial", feedback="Synthetic early stop")
    db.execute(
        text("""INSERT INTO session_outcomes
        (id,user_id,plan_id,revision_id,week,slot,occurred_at,recorded_at,command_id,actual)
        VALUES (:id,:owner,:plan,:rev,1,'first-press',:occurred,:recorded,:key,
                CAST(:actual AS jsonb))"""),
        dict(
            id=ident,
            owner=user.id,
            plan=plan,
            rev=rev,
            occurred=at(4),
            recorded=at(5),
            key=key,
            actual=actual.model_dump_json(),
        ),
    )
    db.commit()
    command.upgrade(config, "head")
    row = db.get(SessionOutcome, ident)
    assert (
        row.outcome_version == 1
        and row.origin_revision_id is None
        and row.actual == actual.model_dump(mode="json")
    )
    monkeypatch.setattr(PlanCommands, "_now", lambda _: at(6))
    assert (
        cmd.record_outcome(
            plan, rev, 1, Slot.FIRST_PRESS, actual, occurred_at=at(4), command_id=key
        )
        == ident
    )
    assert cmd.weekly_review(plan, 1).slots[0].observation_id == ident
    db.commit()
    command.downgrade(config, "b330")
    assert db.scalar(text("SELECT id FROM session_outcomes")) == ident
    db.commit()
    command.upgrade(config, "head")
    command.check(config)


def test_unperformed_and_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="cannot attest sets"):
        fo.StrengthExecution(
            status="unknown", sets=(part("press", "primary", 1, status="completed"),)
        )
    with pytest.raises(ValidationError, match="moving|exceeds"):
        fo.RunExecution(
            status="partial",
            role="easy",
            confirmed_outing=True,
            elapsed_seconds=100,
            moving_seconds=120,
        )
    with pytest.raises(ValidationError, match="cannot attest running"):
        fo.RunExecution(
            status="missed", role="long", confirmed_outing=False, session_rpe=Decimal(0)
        )
    with pytest.raises(ValidationError, match="actual load convention"):
        part("press", "primary", 1, status="partial", kg=Decimal(0))


def test_correction_revalidates_changed_execution_instant(cycle: Cycle) -> None:
    first = cycle.record("gym-a", fo.StrengthExecution(status="missed", feedback="Initial report"))
    cycle.now = at(13)
    corrected_time = at(8)
    corrected = fo.StrengthExecution(status="completed", manageable=True)
    recovery_key = uuid4()
    latest = cycle.record(
        "gym-a", corrected, occurred_at=corrected_time, command_id=recovery_key, supersedes_id=first
    )
    history = cycle.cmd.weekly_review(cycle.plan, 1).sessions[0].history
    assert [a.effective_head for a in history] == [cycle.weeks[0], cycle.weeks[2]]
    assert history[-1].id == latest and history[-1].occurred_at == corrected_time
    current = cycle.cmd.weekly_review(cycle.plan, 1)
    assert current.reported_sets == ()
    assert "vs scheduled" in current.sessions[0].differences[0]
    assert "vs scheduled" in fo.render_execution_review(current)
    with pytest.raises(OutcomeConflict, match="different intent"):
        cycle.record(
            "gym-a", corrected, occurred_at=at(9), command_id=recovery_key, supersedes_id=first
        )

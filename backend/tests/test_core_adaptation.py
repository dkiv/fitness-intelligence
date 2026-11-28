"""Synthetic E4.3 decisions through the owner-bound planning commands on PostgreSQL."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from fitness_intelligence.db.familiar_snapshot import PREVIEW_OWNER
from fitness_intelligence.db.models import User
from fitness_intelligence.db.plan_commands import PlanCommands, StalePlan
from fitness_intelligence.db.review import render_review
from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning import familiar_outcomes as actual
from fitness_intelligence.planning.core_adaptation import easy_duration_step
from fitness_intelligence.planning.familiar_examples import example


@dataclass
class Rehearsal:
    cmd: PlanCommands
    cycle: UUID
    head: UUID
    context: UUID
    ctx: f.Context
    now: datetime

    def propose(self, n: int, choice: str | None = None) -> UUID:
        return self.cmd.submit(self.cycle, self.head, f.FamiliarWeek(number=n, choice=choice))

    def approve(self, revision: UUID) -> None:
        self.cmd.decide(
            self.cycle, revision, expected_head=self.head, choice="approve", command_id=uuid4()
        )
        self.head = revision

    def candidate(self, revision: UUID):
        return self.cmd.preview(self.cycle, revision).candidate

    def report(
        self,
        n: int,
        *,
        load: Decimal | None = None,
        effort: Decimal | None = Decimal(7),
        easy_seconds: int = 1200,
        primary_reps: tuple[int, int] = (5, 5),
    ) -> dict[str, UUID]:
        # All dated sessions have elapsed at 23:30 Toronto on the final Sunday.
        self.now = datetime(2027, 1, 11, 4, 30, tzinfo=UTC) + timedelta(weeks=n - 1)
        ids = {}
        for day in self.candidate(self.head).days:
            for session in day.sessions:
                key = session.template
                if key in ("gym-a", "gym-b"):
                    sets = tuple(
                        actual.SetExecution(
                            movement=m,
                            variation="standing",
                            equipment="barbell",
                            group=g,
                            kind="working",
                            ordinal=i,
                            status="completed",
                            reps=primary_reps[i - 1]
                            if key == "gym-a" and m == "press" and g == "primary"
                            else 5,
                            kg=load
                            if key == "gym-a"
                            and m == "press"
                            and g == "primary"
                            and load is not None
                            else Decimal(kg),
                            load_convention="total-external-kg",
                            achieved_rpe=effort,
                        )
                        for m, base in (("press", 40), ("squat", 50))
                        for g, i, kg in (
                            ("primary", 1, base),
                            ("primary", 2, base),
                            ("backoff", 1, base - 5),
                        )
                    )
                    report = actual.StrengthExecution(
                        status="completed", manageable=True, sets=sets
                    )
                else:
                    report = actual.RunExecution(
                        status="completed",
                        manageable=True,
                        confirmed_outing=True,
                        role=key,
                        elapsed_seconds=easy_seconds if key == "easy" else 1800,
                        conversational=True,
                    )
                ids[key] = self.cmd.record_outcome(
                    self.cycle,
                    self.head,
                    n,
                    session.occurrence,
                    report,
                    command_id=uuid4(),
                    occurred_at=session.start_utc,
                )
        return ids

    def interruption(self, active: bool, since: date = date(2027, 1, 4)) -> None:
        interruptions = (
            (f.Interruption(template="gym-a", since=since, reason="travel; reduced load reported"),)
            if active
            else ()
        )
        self.ctx = self.ctx.model_copy(update={"interruptions": interruptions})
        self.context = self.cmd.capture_context(self.ctx, expected_context=self.context)


def start(
    db: Session,
    mp: pytest.MonkeyPatch,
    *,
    movement: str = "press",
    fixed: bool = False,
    balanced: bool = False,
    weekly_seconds: int | None = None,
    protect_group: bool = False,
    increment: str = "0.5",
) -> Rehearsal:
    block, ctx = example("strength")
    if protect_group:
        block = block.model_copy(
            update={
                "protections": (
                    *block.protections,
                    f.Protection(
                        sport="strength",
                        task=movement,
                        protocol="same load and repetitions",
                        desired_direction="maintain",
                    ),
                )
            }
        )
    if balanced:
        ctx = ctx.model_copy(
            update={"objectives": tuple(o.model_copy(update={"rank": 1}) for o in ctx.objectives)}
        )
    group = f.DevelopingGroup(
        template="gym-a",
        movement=movement,
        variation="standing",
        group="primary",
        burden="upper" if movement == "press" else "lower",
        rep_range=None if fixed else (5, 6),
        set_seconds=65,
        followup_template="long",
    )
    templates = []
    for t in block.templates:
        p = t.prescription
        if isinstance(p, f.Strength):
            p = p.model_copy(
                update={
                    "exercises": tuple(
                        x.model_copy(update={"load_step_kg": Decimal(increment)})
                        for x in p.exercises
                    )
                }
            )
        templates.append(t.model_copy(update={"prescription": p}))
    profile = f.CoreProfile(groups=(group,), easy_template="easy", weekly_seconds=weekly_seconds)
    block = block.model_copy(update={"adaptation": profile, "templates": tuple(templates)})
    db.add(User(id=PREVIEW_OWNER))
    db.flush()
    mp.setenv("FITNESS_PLANNING_OWNER_ID", str(PREVIEW_OWNER))
    cmd = PlanCommands(db)
    clock = datetime(2027, 1, 2, tzinfo=UTC)
    mp.setattr(PlanCommands, "_now", lambda self: r.now)
    r = Rehearsal(cmd, UUID(int=0), UUID(int=0), UUID(int=0), ctx, clock)
    r.context = cmd.capture_context(ctx, expected_context=None)
    r.cycle = cmd.create_cycle(block)
    first = cmd.submit(r.cycle, None, f.ProposeBlock())
    cmd.decide(r.cycle, first, expected_head=None, choice="approve", command_id=uuid4())
    r.head = first
    r.approve(r.propose(1))
    db.commit()
    return r


def two_weeks(r: Rehearsal) -> dict[str, UUID]:
    r.report(1)
    r.approve(r.propose(2, "hold"))
    return r.report(2)


def test_upper_and_easy_joint_review_replay_and_no_second_credit(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch)
    latest = two_weeks(r)
    base = r.head
    rev = r.propose(3)
    c = r.candidate(rev)
    assert c.adaptation.predecessor == base
    press, easy = c.adaptation.decisions
    assert (press.action, press.before, press.after) == (
        "reps",
        "5 × 40 kg, 5 × 40 kg",
        "6 × 40 kg, 5 × 40 kg",
    )
    assert (easy.action, easy.before, easy.after) == (
        "duration",
        "1200 elapsed s",
        "1500 elapsed s",
    )
    assert latest["gym-a"] in press.assertions and latest["easy"] in easy.assertions
    assert len(set(easy.performances)) == 2
    assert c == r.candidate(r.propose(3))
    assert "J-DEFAULT" in render_review(r.cmd.preview(r.cycle, rev))
    r.approve(rev)
    db.commit()
    r.now += timedelta(days=7)
    later = r.candidate(r.propose(4))
    assert [d.action for d in later.adaptation.decisions] == ["hold", "hold"]
    assert all(d.anchor_revision == base for d in later.adaptation.decisions)
    assert [d.after for d in later.adaptation.decisions] == [press.after, easy.after]
    assert r.cmd.replay_familiar(r.cycle, rev) == c


@pytest.mark.parametrize(
    ("balanced", "choice", "actions"),
    [
        (False, None, ["reps", "hold"]),
        (True, None, ["hold", "hold"]),
        (True, "running", ["hold", "duration"]),
    ],
)
def test_competing_lower_and_easy(
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    balanced: bool,
    choice: str | None,
    actions: list[str],
) -> None:
    r = start(db, monkeypatch, movement="squat", balanced=balanced)
    two_weeks(r)
    rev = r.propose(3, choice)
    changes = r.candidate(rev).adaptation.decisions
    assert [d.action for d in changes] == actions
    assert all("J-DEFAULT" in d.reason for d in changes if d.action == "hold")
    r.approve(rev)


def test_correction_stales_pending_change(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    r = start(db, monkeypatch)
    tips = two_weeks(r)
    rev = r.propose(3)
    before = r.candidate(rev)
    assert before.adaptation.decisions[1].action == "duration"
    occurrence = next(
        s for day in r.candidate(r.head).days for s in day.sessions if s.template == "easy"
    )
    r.cmd.record_outcome(
        r.cycle,
        r.head,
        2,
        occurrence.occurrence,
        actual.RunExecution(
            status="partial",
            role="easy",
            manageable=True,
            confirmed_outing=True,
            elapsed_seconds=960,
        ),
        occurred_at=occurrence.start_utc,
        command_id=uuid4(),
        supersedes_id=tips["easy"],
    )
    db.commit()
    with pytest.raises(StalePlan, match="evidence changed"):
        r.approve(rev)
    assert (
        r.cmd.current(r.cycle).revision_id == r.head
        and r.cmd.preview(r.cycle, rev).decision is None
    )
    assert r.cmd.replay_familiar(r.cycle, rev) == before
    assert r.candidate(r.propose(3)).adaptation.decisions[1].action == "hold"


def test_reentry_requires_actuals_and_restores_one_step(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch, fixed=True)
    r.report(1, load=Decimal("37.5"))
    r.interruption(True, since=date(2027, 1, 10))
    with pytest.raises(ValueError, match="defer gym-a"):
        r.propose(2)
    r.interruption(True)
    rev = r.propose(2)
    d = r.candidate(rev).adaptation.decisions[0]
    assert d.reentry and d.action == "resume" and d.after == "5 × 37.5 kg, 5 × 37.5 kg"
    r.approve(rev)
    r.interruption(False)
    r.report(2, load=Decimal("37.5"))
    held = r.propose(3)
    assert r.candidate(held).adaptation.decisions[0].reentry
    assert r.candidate(held).adaptation.decisions[0].action == "hold"
    r.approve(held)
    r.report(3, load=Decimal("37.5"), easy_seconds=1500)
    restored = r.candidate(r.propose(4)).adaptation.decisions[0]
    assert restored.action == "load" and not restored.reentry and "restoration" in restored.reason
    assert restored.after == "5 × 38.0 kg, 5 × 38.0 kg"


def test_equipment_ceiling_missing_effort_and_time_budget(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The 6480-second familiar week fills the budget, including setup and rest.
    r = start(db, monkeypatch, fixed=True, increment="2.5", weekly_seconds=6480)
    r.report(1, effort=None)
    rev = r.propose(2)
    assert "two distinct" in r.candidate(rev).adaptation.decisions[0].reason
    r.approve(rev)
    r.report(2, effort=None)
    press, easy = r.candidate(r.propose(3)).adaptation.decisions
    assert press.action == "hold" and "equipment step exceeds" in press.reason
    assert easy.action == "hold" and "weekly time budget" in easy.reason


def test_variable_group_tops_out_then_resets_reps_with_load(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch)
    r.report(1, effort=None)
    r.approve(r.propose(2))
    r.report(2, effort=None)
    rev = r.propose(3)
    assert r.candidate(rev).adaptation.decisions[0].after == "6 × 40 kg, 5 × 40 kg"
    r.approve(rev)
    r.report(3, primary_reps=(6, 5), easy_seconds=1500)
    rev = r.propose(4)
    assert r.candidate(rev).adaptation.decisions[0].after == "6 × 40 kg, 6 × 40 kg"
    r.approve(rev)
    r.report(4, primary_reps=(6, 6), easy_seconds=1500)
    decision = r.candidate(r.propose(5)).adaptation.decisions[0]
    assert decision.action == "load" and decision.after == "5 × 40.5 kg, 5 × 40.5 kg"


def test_fixed_load_bound_to_initial_even_with_fresh_performances(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch, fixed=True, increment="1")
    for n, kg, easy, expected in [(1, 40, 1200, 41), (2, 41, 1200, 42), (3, 42, 1500, 42)]:
        r.report(n, load=Decimal(kg), easy_seconds=easy)
        rev = r.propose(n + 1)
        decision = r.candidate(rev).adaptation.decisions[0]
        assert decision.after == f"5 × {expected} kg, 5 × {expected} kg"
        if n == 3:
            assert decision.action == "hold" and "initial load ceiling" in decision.reason
        r.approve(rev)


def test_equal_dose_reentry_cannot_count_preinterruption_work(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch, fixed=True)
    two_weeks(r)
    r.interruption(True, since=date(2027, 1, 11))
    rev = r.propose(3)
    assert r.candidate(rev).adaptation.decisions[0].ceiling_since_week == 3
    r.approve(rev)
    r.interruption(False)
    r.report(3)
    decision = r.candidate(r.propose(4)).adaptation.decisions[0]
    assert decision.reentry and decision.action == "hold"
    assert len(decision.performances) == 1


def test_review_window_and_protected_task(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    r = start(db, monkeypatch)
    with pytest.raises(StalePlan, match="upcoming week"):
        r.propose(2)
    r.report(1)
    rev = r.propose(2)
    c = r.candidate(rev)
    scope = c.decision_inputs.projection.scope
    narrow = scope.model_copy(update={"start": scope.stop - timedelta(days=1)})
    with pytest.raises(ValueError, match="full recent period"):
        r.cmd.submit(r.cycle, r.head, f.FamiliarWeek(number=2), evidence_scope=narrow)
    long = [s for d in c.days for s in d.sessions if s.template == "long"][0]
    assert long.prescription.duration.nominal == 1800
    r.now += timedelta(hours=2)
    with pytest.raises(StalePlan, match="review day changed"):
        r.approve(rev)


@pytest.mark.parametrize(
    ("nominal", "maximum", "initial", "room"),
    [
        (2400, 2400, 2400, 240),
        (2640, 2640, 2400, 264),
        (9300, 9300, 8400, 300),
        (9500, 9550, 8400, 50),
        (9600, 9600, 8400, 0),
        (2400, 2640, 2400, 0),
    ],
)
def test_duration_bounds_use_maximum_weekly_endpoints(
    nominal: int, maximum: int, initial: int, room: int
) -> None:
    assert easy_duration_step(nominal, maximum, initial) == room


def test_corrected_credit_cannot_carry_an_unperformed_trial(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch)
    tips = two_weeks(r)
    source = r.head
    rev = r.propose(3)
    r.approve(rev)
    r.now += timedelta(days=7)
    occurrence = next(
        s for d in r.candidate(source).days for s in d.sessions if s.template == "easy"
    )
    r.cmd.record_outcome(
        r.cycle,
        source,
        2,
        occurrence.occurrence,
        actual.RunExecution(
            status="partial",
            role="easy",
            manageable=True,
            confirmed_outing=True,
            elapsed_seconds=960,
        ),
        occurred_at=occurrence.start_utc,
        command_id=uuid4(),
        supersedes_id=tips["easy"],
    )
    with pytest.raises(ValueError, match="no longer supports the approved trial"):
        r.propose(4)
    assert r.cmd.current(r.cycle).revision_id == rev


def test_adverse_set_effort_defers_numeric_week_even_for_hold(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch)
    r.report(1, effort=Decimal(9))
    with pytest.raises(ValueError, match="adverse tolerance"):
        r.propose(2, "hold")


def test_named_protected_group_holds_even_when_successful(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch, protect_group=True)
    two_weeks(r)
    press, easy = r.candidate(r.propose(3)).adaptation.decisions
    assert press.action == "hold" and press.before == press.after and "protected" in press.reason
    assert easy.action == "duration"


def test_equal_rank_budget_tradeoff_exposes_exact_alternatives(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch, balanced=True, weekly_seconds=6780)
    two_weeks(r)
    press, easy = r.candidate(r.propose(3)).adaptation.decisions
    assert press.action == easy.action == "hold"
    assert press.considered == "6 × 40 kg, 5 × 40 kg" and easy.considered == "1500 elapsed s"
    press, easy = r.candidate(r.propose(3, "running")).adaptation.decisions
    assert press.action == "hold" and "weekly time budget" in press.reason
    assert easy.action == "duration"


def test_interruption_cannot_override_rep_envelope(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    r = start(db, monkeypatch)
    r.report(1, primary_reps=(3, 3))
    r.interruption(True)
    with pytest.raises(ValueError, match="rep envelope"):
        r.propose(2)

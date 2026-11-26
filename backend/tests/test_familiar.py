"""E4.1 domain, calendar, wire and trusted command conformance. All data is invented."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from threading import Barrier
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from fitness_intelligence.db import familiar_snapshot as wire
from fitness_intelligence.db.models import User
from fitness_intelligence.db.plan_commands import DecisionConflict, PlanCommands, StalePlan
from fitness_intelligence.db.plan_models import PlanDecision, PlanRevision
from fitness_intelligence.db.plan_snapshot import Generate, InvalidSnapshot
from fitness_intelligence.db.review import render_review
from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning.familiar_calendar import PlacementFailure, generate
from fitness_intelligence.planning.familiar_examples import Emphasis, example
from fitness_intelligence.planning.outcomes import Actual
from fitness_intelligence.planning.planner import Slot
from fitness_intelligence.planning.prescriptions import Target

CYCLE = UUID(int=41)
NOW = datetime(2027, 1, 2, 12, tzinfo=UTC)


def sessions(days: tuple[f.Day, ...]) -> tuple[f.Session, ...]:
    return tuple(s for day in days for s in day.sessions)


@pytest.mark.parametrize(("emphasis", "count"), [("strength", 4), ("running", 4), ("balanced", 5)])
def test_familiar_weeks(emphasis: Emphasis, count: int) -> None:
    block, ctx = example(emphasis)
    assert ctx.emphasis == emphasis
    for number in (1, 3, 6):
        days = generate(CYCLE, block, ctx, number)
        assert [d.day for d in days] == [
            block.start + timedelta(weeks=number - 1, days=i) for i in range(7)
        ]
        placed = sessions(days)
        assert len(placed) == count and len({s.occurrence for s in placed}) == count
        assert {s.template: s.prescription for s in placed} == {
            t.key: t.prescription for t in block.templates
        }
        assert all(a.end <= b.start_utc for a, b in zip(placed, placed[1:], strict=False))
        assert days == generate(CYCLE, block, ctx, number)
    assert (
        sessions(generate(CYCLE, block, ctx, 1))[0].occurrence
        != sessions(generate(CYCLE, block, ctx, 2))[0].occurrence
    )
    gym = block.templates[0].prescription
    assert isinstance(gym, f.Strength)
    assert [e.movement for e in gym.exercises] == ["press", "squat"]
    assert gym.minimum_exposure == 6 and gym.reserved_seconds == 1560
    assert [s.ordinal for s in gym.exercises[0].groups[1].sets] == [1, 2]
    for number in (0, 7, True):
        with pytest.raises(ValueError, match="outside block"):
            generate(CYCLE, block, ctx, number)


def test_strength_baseline_requires_the_same_variation_and_load_convention() -> None:
    block, ctx = example("strength")
    report = ctx.observations[0]
    for changed in (
        {"variation": "seated"},
        {"convention": "per-hand-kg"},
        {"ordinal": 3},
        {"kg": Decimal("100")},
    ):
        sets = (report.sets[0].model_copy(update=changed), *report.sets[1:])
        history = (report.model_copy(update={"sets": sets}), *ctx.observations[1:])
        with pytest.raises(ValueError, match="comparable actual work"):
            generate(CYCLE, block, ctx.model_copy(update={"observations": history}), 1)


def test_interval_expansion_and_upper_endpoint() -> None:
    block, ctx = example("running")
    template = block.templates[-1]
    p = template.prescription
    assert isinstance(p, f.Running)
    warm, repeats, cool = p.segments
    assert isinstance(repeats, f.Repeat)
    assert p.duration == Target(1860, 1860, 1860) and p.reserved_seconds == 2040
    amended = repeats.model_copy(update={"final_recovery": repeats.between})
    assert p.model_copy(update={"segments": (warm, amended, cool)}).duration.high == 1980
    # Same nominal total; a supported wide upper endpoint no longer fits a 40-minute window.
    assert isinstance(warm, f.Step)
    bounded = warm.model_copy(update={"seconds": Target(500, 600, 1020)})
    new_template = template.model_copy(
        update={"prescription": p.model_copy(update={"segments": (bounded, repeats, cool)})}
    )
    block = block.model_copy(update={"templates": (*block.templates[:-1], new_template)})
    with pytest.raises(ValueError, match="confirmed elapsed work"):
        generate(CYCLE, block, ctx, 1)
    report = ctx.observations[-1]
    steps = (report.steps[0].model_copy(update={"familiar_max_seconds": 1020}), *report.steps[1:])
    ctx = ctx.model_copy(
        update={
            "observations": (*ctx.observations[:-1], report.model_copy(update={"steps": steps}))
        }
    )
    # Remove branching unrelated to this duration assertion.
    ctx = ctx.model_copy(
        update={
            "fixed": tuple(
                f.FixedStart(template=t.key, day=block.start + timedelta(days=i), minute=1080)
                for i, t in enumerate(block.templates)
            )
        }
    )
    with pytest.raises(PlacementFailure, match="2460s") as exc:
        generate(CYCLE, block, ctx, 1)
    assert not exc.value.incomplete


def test_evidence_protection_and_finite_domain() -> None:
    block, ctx = example("balanced")
    for change in (
        {"confirmed": False},
        {"manageable": None},
        {"provenance": "synthetic-inference"},
    ):
        altered = ctx.observations[0].model_copy(update=change)
        with pytest.raises(ValueError, match="confirmed, manageable"):
            generate(
                CYCLE,
                block,
                ctx.model_copy(update={"observations": (altered, *ctx.observations[1:])}),
                1,
            )
    with pytest.raises(ValueError, match="insufficient"):
        generate(CYCLE, block, ctx.model_copy(update={"observations": ctx.observations[1:]}), 1)
    with pytest.raises(PlacementFailure, match="protected long needs"):
        generate(
            CYCLE,
            block.model_copy(
                update={"commitments": (block.commitments[0].model_copy(update={"sessions": 3}),)}
            ),
            ctx,
            1,
        )
    with pytest.raises(PlacementFailure, match="equipment") as exhausted:
        generate(
            CYCLE,
            block,
            ctx.model_copy(
                update={
                    "windows": tuple(w.model_copy(update={"equipment": ()}) for w in ctx.windows)
                }
            ),
            1,
        )
    assert not exhausted.value.incomplete
    with pytest.raises(PlacementFailure, match="search incomplete") as limited:
        generate(CYCLE, block, ctx, 1, limit=1)
    assert limited.value.incomplete and limited.value.examined == 1
    with pytest.raises(PlacementFailure, match="restricted"):
        generate(CYCLE, block, ctx.model_copy(update={"excluded_tasks": ("squat",)}), 1)


def test_dst_fixed_start_event_and_adjacent_spacing() -> None:
    block, ctx = example("strength", date(2027, 3, 8))
    sun = block.start + timedelta(days=6)
    pins = (f.FixedStart(template="easy", day=sun, minute=150),)
    ctx = ctx.model_copy(
        update={
            "fixed": pins,
            "windows": (
                *ctx.windows,
                f.Window(weekday=6, start_minute=60, end_minute=300, equipment=()),
            ),
        }
    )
    with pytest.raises(PlacementFailure, match="invalid local start"):
        generate(CYCLE, block, ctx, 1)
    ctx = ctx.model_copy(update={"fixed": (f.FixedStart(template="easy", day=sun, minute=183),)})
    first = sessions(generate(CYCLE, block, ctx, 1))
    easy = next(s for s in first if s.template == "easy")
    assert easy.start_utc == datetime(2027, 3, 14, 7, 3, tzinfo=UTC)
    ctx = ctx.model_copy(update={"events": (f.Event(start=easy.start_utc, end=easy.end),)})
    with pytest.raises(PlacementFailure, match="fixed event"):
        generate(CYCLE, block, ctx, 1)
    # The same local start on consecutive days is 23 elapsed hours across spring DST.
    prior_date = date(2027, 3, 13)
    prior = easy.model_copy(
        update={
            "template": "long",
            "start_utc": datetime(2027, 3, 13, 8, 3, tzinfo=UTC),
            "day": prior_date,
        }
    )
    gap = f.Spacing(first="long", second="easy", elapsed_seconds=86400)
    with pytest.raises(PlacementFailure, match="86400s"):
        generate(
            CYCLE,
            block.model_copy(update={"spacing": (gap,)}),
            ctx.model_copy(update={"events": ()}),
            1,
            (prior,),
        )

    autumn, ctx = example("running", date(2027, 11, 1))
    sunday = autumn.start + timedelta(days=6)
    ctx = ctx.model_copy(
        update={
            "windows": (
                *ctx.windows,
                f.Window(weekday=6, start_minute=0, end_minute=180, equipment=()),
            ),
            "fixed": (f.FixedStart(template="easy", day=sunday, minute=90),),
        }
    )
    with pytest.raises(PlacementFailure, match="invalid local start"):
        generate(CYCLE, autumn, ctx, 1)
    fold = ctx.fixed[0].model_copy(update={"fold": 1})
    placed = sessions(generate(CYCLE, autumn, ctx.model_copy(update={"fixed": (fold,)}), 1))
    assert next(s.start_utc for s in placed if s.template == "easy") == datetime(
        2027, 11, 7, 6, 30, tzinfo=UTC
    )


def test_strict_versioned_wire() -> None:
    block, ctx = example("balanced")
    for item in (block, ctx):
        assert wire.read(type(item), wire.snapshot(item)) == item
        for raw in (
            wire.snapshot(item) | {"other": 1},
            wire.snapshot(item) | {"schema_version": 1},
        ):
            with pytest.raises(InvalidSnapshot):
                wire.read(type(item), raw)
    raw = wire.snapshot(block)
    raw["data"]["operational"] = True
    with pytest.raises(InvalidSnapshot):
        wire.read(f.Block, raw)
    with pytest.raises(ValidationError):
        f.FamiliarWeek(number=True)


@pytest.fixture
def preview_cycle(db: Session, monkeypatch: pytest.MonkeyPatch) -> tuple[PlanCommands, UUID, UUID]:
    db.add(User(id=wire.PREVIEW_OWNER))
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(wire.PREVIEW_OWNER))
    monkeypatch.setattr(PlanCommands, "_now", lambda self: NOW)
    block, ctx = example("running")
    cmd = PlanCommands(db)
    context_id = cmd.capture_context(ctx, expected_context=None)
    cycle = cmd.create_cycle(block)
    db.commit()
    return cmd, cycle, context_id


def approve(
    cmd: PlanCommands, cycle: UUID, request: f.ProposeBlock | f.FamiliarWeek, head: UUID | None
) -> UUID:
    rev = cmd.submit(cycle, head, request)
    cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=uuid4())
    return rev


def test_dated_receipts_replay_and_refs(db: Session, preview_cycle: tuple) -> None:
    cmd, cycle, _ = preview_cycle
    block = approve(cmd, cycle, f.ProposeBlock(), None)
    assert not cmd.current(cycle).candidate.days
    versions = []
    head = block
    for number in range(1, 7):
        rev = cmd.submit(cycle, head, f.FamiliarWeek(number=number))
        old = cmd.current(cycle)
        assert old.revision_id == head
        p = cmd.preview(cycle, rev)
        assert p.candidate.block_revision == block and p.decision is None
        assert [ref.revision for ref in p.candidate.prior_weeks] == versions
        assert cmd.replay_familiar(cycle, rev) == p.candidate
        key = uuid4()
        receipt = cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=key)
        if number == 1:
            first, key1 = receipt, key
        versions.append(rev)
        head = rev
    assert (
        cmd.decide(cycle, versions[0], expected_head=block, choice="approve", command_id=key1)
        == first
    )
    assert cmd.preview(cycle, versions[0]).candidate == cmd.replay_familiar(cycle, versions[0])
    with pytest.raises(DecisionConflict):
        cmd.decide(cycle, versions[0], expected_head=block, choice="decline", command_id=key1)
    with pytest.raises(ValueError, match="outside block"):
        cmd.submit(cycle, head, f.FamiliarWeek(number=7))
    with pytest.raises(ValueError, match="unsupported"):
        cmd.submit(cycle, head, Generate(1))
    with pytest.raises(ValueError, match="unsupported"):
        cmd.submit(cycle, head, f.ProposeBlock())
    assert cmd.weekly_review(cycle, 1).origin_revision == versions[0]
    with pytest.raises(ValueError, match="unsupported"):
        cmd.record_outcome(
            cycle,
            head,
            1,
            Slot.SHORT_RUN,
            Actual(status="unknown"),
            occurred_at=NOW,
            command_id=uuid4(),
        )


def test_stale_context_decline_rollback_and_elapsed(
    db: Session, preview_cycle: tuple, monkeypatch: pytest.MonkeyPatch
) -> None:
    cmd, cycle, context = preview_cycle
    opening = approve(cmd, cycle, f.ProposeBlock(), None)
    rev = cmd.submit(cycle, opening, f.FamiliarWeek(number=1))
    db.commit()
    cmd.decide(cycle, rev, expected_head=opening, choice="approve", command_id=uuid4())
    db.rollback()
    assert cmd.current(cycle).revision_id == opening
    cmd.decide(cycle, rev, expected_head=opening, choice="decline", command_id=uuid4())
    assert cmd.current(cycle).revision_id == opening
    rev = cmd.submit(cycle, opening, f.FamiliarWeek(number=1))
    block, ctx = example("running")
    cmd.capture_context(
        ctx.model_copy(update={"excluded_tasks": ("squat",)}), expected_context=context
    )
    with pytest.raises(StalePlan, match="context"):
        cmd.decide(cycle, rev, expected_head=opening, choice="approve", command_id=uuid4())
    with pytest.raises(PlacementFailure, match="restricted"):
        cmd.submit(cycle, opening, f.FamiliarWeek(number=1))
    db.rollback()
    rev = cmd.submit(cycle, opening, f.FamiliarWeek(number=1))
    monkeypatch.setattr(
        cmd, "_now", lambda: datetime.combine(block.start, datetime.min.time(), ZoneInfo(ctx.zone))
    )
    with pytest.raises(StalePlan, match="has started"):
        cmd.decide(cycle, rev, expected_head=opening, choice="approve", command_id=uuid4())


def test_operational_owner_and_foreign_replay(
    db: Session, preview_cycle: tuple, monkeypatch: pytest.MonkeyPatch
) -> None:
    cmd, cycle, _ = preview_cycle
    rev = approve(cmd, cycle, f.ProposeBlock(), None)
    owner = User()
    db.add(owner)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(owner.id))
    personal = PlanCommands(db)
    block, ctx = example("running")
    with pytest.raises(PermissionError, match="no authorized rules"):
        personal.capture_context(ctx, expected_context=None)
    with pytest.raises(PermissionError, match="no authorized rules"):
        personal.create_cycle(block)
    with pytest.raises(NoResultFound):
        personal.preview(cycle, rev)


def test_competing_generalized_approvals(db: Session, preview_cycle: tuple) -> None:
    cmd, cycle, _ = preview_cycle
    head = approve(cmd, cycle, f.ProposeBlock(), None)
    revs = [cmd.submit(cycle, head, f.FamiliarWeek(number=1)) for _ in range(2)]
    assert cmd.preview(cycle, revs[0]).candidate == cmd.preview(cycle, revs[1]).candidate
    db.commit()
    barrier = Barrier(2)
    engine = db.get_bind()

    def decide(rev: UUID) -> bool:
        with Session(engine) as other, other.begin():
            barrier.wait(timeout=10)
            try:
                PlanCommands(other).decide(
                    cycle, rev, expected_head=head, choice="approve", command_id=uuid4()
                )
                return True
            except StalePlan:
                return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(decide, revs)) == [False, True]
    assert len(db.scalars(select(PlanDecision).where(PlanDecision.plan_id == cycle)).all()) == 2


def test_approved_and_future_fixed_week_boundaries() -> None:
    block, ctx = example("strength")
    block = block.model_copy(
        update={"spacing": (f.Spacing(first="easy", second="long", elapsed_seconds=25 * 3600),)}
    )
    last = block.start + timedelta(days=6)
    pins = (
        f.FixedStart(template="long", day=last, minute=1080),
        f.FixedStart(template="easy", day=last + timedelta(days=1), minute=1080),
    )
    previous = sessions(generate(CYCLE, block, ctx.model_copy(update={"fixed": pins[:1]}), 1))
    with pytest.raises(PlacementFailure, match="requires 90000s"):
        generate(CYCLE, block, ctx.model_copy(update={"fixed": pins[1:]}), 2, previous)
    with pytest.raises(PlacementFailure, match="requires 90000s"):
        generate(CYCLE, block, ctx.model_copy(update={"fixed": pins}), 1)


def test_changed_context_retains_approved_dates(preview_cycle: tuple) -> None:
    cmd, cycle, context = preview_cycle
    opening = approve(cmd, cycle, f.ProposeBlock(), None)
    week = approve(cmd, cycle, f.FamiliarWeek(number=1), opening)
    p = cmd.preview(cycle, week)
    placed = sessions(p.candidate.days)
    old = placed[0]
    new_ctx = p.sealed_context.model_copy(update={"unavailable_dates": (old.day,)})
    cmd.capture_context(new_ctx, expected_context=context)
    with pytest.raises(StalePlan, match="retained prescription"):
        cmd.submit(cycle, week, f.FamiliarWeek(number=2))
    assert cmd.replay_familiar(cycle, week) == p.candidate
    rendered = render_review(cmd.preview(cycle, week))
    assert "context has changed" in rendered and str(old.occurrence) in rendered
    assert "backoff (working)" in rendered and "step RPE" in rendered


def test_corrupt_sealed_generalized_week(db: Session, preview_cycle: tuple) -> None:
    cmd, cycle, context = preview_cycle
    opening = approve(cmd, cycle, f.ProposeBlock(), None)
    proposal = cmd.submit(cycle, opening, f.FamiliarWeek(number=1))
    candidate = cmd.preview(cycle, proposal).candidate
    damaged = candidate.model_copy(update={"supports": ()})
    revision = PlanRevision(
        user_id=wire.PREVIEW_OWNER,
        plan_id=cycle,
        base_id=opening,
        context_id=context,
        snapshot=wire.snapshot(damaged),
    )
    db.add(revision)
    db.flush()
    with pytest.raises(InvalidSnapshot, match="differs from replay"):
        cmd.decide(cycle, revision.id, expected_head=opening, choice="approve", command_id=uuid4())
    assert cmd.current(cycle).revision_id == opening


@pytest.mark.parametrize(
    ("sport", "change", "reason"),
    [
        ("strength", {"target": {"low": "6", "nominal": "8", "high": "8"}}, "range or nominal"),
        ("strength", {"cap": "9"}, "execution cap"),
        ("running", {"target": {"low": "5", "nominal": "7", "high": "7"}}, "range or nominal"),
        (
            "running",
            {"target": {"low": "5", "nominal": "6", "high": "8"}, "cap": "8"},
            "range or nominal",
        ),
        ("running", {"cap": "9"}, "execution cap"),
    ],
)
def test_matched_work_cannot_change_effort(sport: str, change: dict, reason: str) -> None:
    block, ctx = example("balanced")
    raw = wire.snapshot(block)
    templates = {t["key"]: t["prescription"] for t in raw["data"]["templates"]}
    if sport == "strength":
        effort = templates["gym-a"]["exercises"][0]["groups"][1]["effort"]
    else:
        effort = templates["cruise"]["segments"][1]["work"]["effort"]
    effort.update(change)
    with pytest.raises(ValueError, match=reason):
        generate(CYCLE, wire.read(f.Block, raw), ctx, 1)


@pytest.mark.parametrize(
    ("support", "reason"),
    [
        (None, "no confirmed familiar instruction"),
        (f.EffortEvidence(observed_rpe=Decimal(7)), "no confirmed familiar instruction"),
        (
            f.EffortEvidence(
                observed_rpe=Decimal(8), confirmed_target=Target(Decimal(6), Decimal(7), Decimal(8))
            ),
            "execution cap lacks matching explicit confirmation",
        ),
        (
            f.EffortEvidence(
                observed_rpe=Decimal(9),
                confirmed_target=Target(Decimal(6), Decimal(7), Decimal(8)),
                confirmed_cap=Decimal(8),
            ),
            "observed effort exceeded",
        ),
    ],
)
def test_strength_evidence_scoped_to_each_ordinal(
    support: f.EffortEvidence | None,
    reason: str,
) -> None:
    block, ctx = example("strength")
    report = ctx.observations[0]
    assert report.manageable and report.sets[1].effort.confirmed_cap == 8
    # Identical instruction is confirmed for the first primary set and the backoff group.
    # Neither can supply the missing or contradictory evidence for primary ordinal two.
    sets = list(report.sets)
    sets[2] = sets[2].model_copy(update={"effort": support})
    ctx = ctx.model_copy(
        update={
            "observations": (report.model_copy(update={"sets": tuple(sets)}), *ctx.observations[1:])
        }
    )
    with pytest.raises(ValueError, match=f"gym-a/press/primary set 2: .*{reason}"):
        generate(CYCLE, block, ctx, 1)


def test_running_support_belongs_to_the_role_and_expanded_step() -> None:
    block, ctx = example("running")
    raw = wire.snapshot(ctx)
    reports = {o["role"]: o for o in raw["data"]["observations"]}
    # Other work reps remain confirmed. A recovery cue cannot cover this work rep.
    steps = reports["controlled"]["steps"]
    steps[3]["effort"] = steps[2]["effort"]
    with pytest.raises(ValueError, match=r"cruise/controlled step 4 \(work\): effort range"):
        generate(CYCLE, block, wire.read(f.Context, raw), 1)
    # Easy and long have identical numeric cues. A confirmation on easy cannot cover long.
    del reports["long"]["steps"][0]["effort"]
    with pytest.raises(ValueError, match=r"long/long step 1 \(work\): numeric effort target"):
        generate(CYCLE, block, wire.read(f.Context, raw), 1)


@pytest.mark.parametrize("emphasis", ["strength", "running", "balanced"])
def test_confirmed_instructions_without_measured_effort(emphasis: Emphasis) -> None:
    block, ctx = example(emphasis)
    sealed = wire.read(f.Context, wire.snapshot(ctx))
    for report in sealed.observations:
        for item in (*report.sets, *report.steps):
            assert item.effort.confirmed_target and item.effort.confirmed_cap is not None
            assert item.effort.observed_rpe is None
    assert len(generate(CYCLE, block, sealed, 1)) == 7


def test_pre_correction_snapshot_replay_is_read_only(
    db: Session, preview_cycle: tuple[PlanCommands, UUID, UUID]
) -> None:
    cmd, cycle, initial = preview_cycle
    block, ctx = example("running")
    raw = wire.snapshot(ctx)
    for observation in raw["data"]["observations"]:
        for item in (*observation["sets"], *observation["steps"]):
            del item["effort"]
    historical_context = wire.read(f.Context, raw)
    assert wire.snapshot(historical_context) == raw
    context_id = cmd.capture_context(historical_context, expected_context=initial)

    def sealed(base: UUID | None, candidate: f.Candidate) -> PlanRevision:
        revision = PlanRevision(
            user_id=wire.PREVIEW_OWNER,
            plan_id=cycle,
            context_id=context_id,
            base_id=base,
            snapshot=wire.snapshot(candidate),
        )
        db.add(revision)
        db.flush()
        return revision

    old_rule = "synthetic.familiar.hold.v1"
    opening = sealed(
        None,
        f.Candidate(
            rules=old_rule,
            request=f.ProposeBlock(),
            cycle=cycle,
            block_key=block.key,
            block_revision=None,
            prior_weeks=(),
            days=(),
            supports=tuple(sorted(o.support for o in ctx.observations)),
        ),
    )
    # An already sealed approving receipt from the pre-correction implementation.
    command = uuid4()
    db.add(
        PlanDecision(
            user_id=wire.PREVIEW_OWNER,
            plan_id=cycle,
            revision_id=opening.id,
            choice="approve",
            command_id=command,
            decided_at=NOW,
        )
    )
    db.flush()
    expected = f.Candidate(
        rules=old_rule,
        request=f.FamiliarWeek(number=1),
        cycle=cycle,
        block_key=block.key,
        block_revision=opening.id,
        prior_weeks=(),
        days=generate(cycle, block, ctx, 1),
        supports=tuple(sorted(o.support for o in ctx.observations)),
    )
    pending = sealed(opening.id, expected)
    assert wire.snapshot(cmd.replay_familiar(cycle, pending.id)) == pending.snapshot
    assert (
        cmd.decide(
            cycle, opening.id, expected_head=None, choice="approve", command_id=command
        ).revision_id
        == opening.id
    )
    with pytest.raises(StalePlan, match="effort rule changed"):
        cmd.decide(
            cycle, pending.id, expected_head=opening.id, choice="approve", command_id=uuid4()
        )
    with pytest.raises(ValueError, match="no confirmed familiar instruction"):
        cmd.submit(cycle, opening.id, f.FamiliarWeek(number=1))

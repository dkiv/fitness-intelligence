"""Golden domain cases, revision 1. All observations and programming limits are synthetic."""

from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal as D
from zoneinfo import ZoneInfo

import pytest

from fitness_intelligence.planning.planner import (
    BlockRevisionRequired,
    Conflicts,
    Exposure,
    Finding,
    Slot,
    WeekInputs,
    WeekPlan,
    WeekReview,
    change_run_commitment,
    generate_week,
    propose_move,
)
from fitness_intelligence.planning.prescriptions import (
    Intervals,
    RunSession,
    RunStep,
    StrengthSession,
    Target,
    fixed,
)
from fitness_intelligence.planning.press_block import LIFT, RUN, Availability, PressBlock, PressDose

BLOCK = PressBlock()
AVAILABILITY = Availability()
START = date(2027, 1, 4)
REVIEW = WeekReview(
    "synthetic.press.v1",
    START,
    datetime(2027, 1, 10, 18, tzinfo=UTC),
    Exposure(True, (D(6), D(7), D(7))),
    Exposure(True, (D(6), D(7))),
    True,
)
SATURDAY = date(2027, 1, 16)
SUNDAY = date(2027, 1, 17)
MONDAY = date(2027, 1, 18)


def week_one(block: PressBlock = BLOCK, availability: Availability = AVAILABILITY) -> WeekPlan:
    plan = generate_week(WeekInputs(block, availability, 1))
    assert isinstance(plan, WeekPlan)
    return plan


def two_inputs(block: PressBlock = BLOCK) -> WeekInputs:
    return WeekInputs(
        block, AVAILABILITY, 2, week_one(block), replace(REVIEW, block_version=block.version)
    )


def conflict(result: WeekPlan | Conflicts, rule: str) -> Finding:
    assert isinstance(result, Conflicts)
    return next(f for f in result.findings if f.rule == rule)


def test_a1_two_weeks_of_manual_entry_prescriptions() -> None:
    inputs = two_inputs()
    first = inputs.previous
    second = generate_week(inputs)
    assert first is not None and isinstance(second, WeekPlan)
    assert (first.press_sets, second.press_sets) == (5, 6)
    assert first.inputs.block == second.inputs.block == BLOCK
    assert len(BLOCK.intents) == 8
    assert first.inputs.review is None and second.inputs.review == REVIEW
    for i, week in enumerate((first, second)):
        assert week.rule_version == "synthetic.press.e1.v1"
        assert [d.day for d in week.days] == [START + timedelta(days=7 * i + j) for j in range(7)]
        assert [d.day.weekday() for d in week.days if d.is_rest] == [2, 4, 6]
        assert week.running_seconds == 45 * 60
        for slot, weekday, count, reps in (
            (Slot.FIRST_PRESS, 0, 3, 5),
            (Slot.SECOND_PRESS, 3, 2 + i, 6),
        ):
            session = week.session(slot)
            assert (session.day.weekday(), session.start) == (weekday, time(9))
            rx = session.prescription
            assert isinstance(rx, StrengthSession) and rx.reserved_seconds == 2400
            (exercise,) = rx.exercises
            assert (exercise.movement, exercise.equipment) == ("press", "barbell")
            warmup, working = exercise.groups
            assert warmup.effort_cue == "easy"
            assert (warmup.kind, warmup.count, warmup.reps, warmup.external_kg) == (
                "warmup",
                1,
                fixed(5),
                fixed(D(15)),
            )
            assert (working.kind, working.count, working.reps, working.external_kg) == (
                "working",
                count,
                fixed(reps),
                fixed(D(30)),
            )
            assert (working.max_rpe, working.max_rest_seconds) == (7, 180)
        for slot, weekday, middle in ((Slot.SHORT_RUN, 1, 600), (Slot.LONG_RUN, 5, 900)):
            run = week.session(slot)
            assert (run.day.weekday(), run.start) == (weekday, time(9))
            rx = run.prescription
            assert isinstance(rx, RunSession)
            assert [(s.purpose, s.seconds) for s in rx.segments if isinstance(s, RunStep)] == [
                ("warmup", fixed(300)),
                ("work", fixed(middle)),
                ("cooldown", fixed(300)),
            ]
            assert all(
                isinstance(s, RunStep) and (s.rpe.low, s.rpe.high) == (2, 4) for s in rx.segments
            )
    decision = next(f for f in second.explanation if f.rule == "press-progression")
    assert dict(decision.facts) == {
        "eligible": True,
        "prior_sets": 5,
        "proposed_sets": 6,
        "upper_kg": D(30),
    }


@pytest.mark.parametrize(
    ("review", "rule", "fact", "expected"),
    [
        (None, "manageable-feedback", "both_manageable", None),
        (replace(REVIEW, both_manageable=None), "manageable-feedback", "both_manageable", None),
        (replace(REVIEW, both_manageable=False), "manageable-feedback", "both_manageable", False),
        (replace(REVIEW, first_press=Exposure()), "confirmed-exposure", "completed", None),
        (
            replace(REVIEW, first_press=Exposure(True, (), 3)),
            "confirmed-exposure",
            "inferred_sets",
            3,
        ),
        (
            replace(REVIEW, first_press=Exposure(True, (D(7), None, D(6)))),
            "confirmed-exposure",
            "measured_rpes",
            2,
        ),
        (
            replace(REVIEW, first_press=Exposure(True, (D(7), D(6)))),
            "confirmed-exposure",
            "confirmed_sets",
            2,
        ),
        (
            replace(REVIEW, first_press=Exposure(True, (D(7), D(8), D(6)))),
            "confirmed-exposure",
            "peak_rpe",
            8,
        ),
        (
            replace(REVIEW, first_press=Exposure(False, (D(7), D(6), D(6)))),
            "confirmed-exposure",
            "completed",
            False,
        ),
        (replace(REVIEW, second_press=Exposure()), "press-progression", "eligible", False),
    ],
)
def test_a2_hold_on_missing_or_insufficient_evidence(
    review: WeekReview | None, rule: str, fact: str, expected: object
) -> None:
    result = generate_week(replace(two_inputs(), review=review))
    assert isinstance(result, WeekPlan)
    assert (result.press_sets, result.running_seconds) == (5, 2700)
    assert dict(next(f for f in result.explanation if f.rule == rule).facts)[fact] == expected
    assert (
        result.session(Slot.SECOND_PRESS).prescription
        == week_one().session(Slot.SECOND_PRESS).prescription
    )


def test_a4_infeasible_commitment_and_revision_scope() -> None:
    inputs = two_inputs()
    blocked = replace(AVAILABILITY, overrides=((SATURDAY, None), (SUNDAY, None)))
    result = generate_week(replace(inputs, availability=blocked))
    issue = conflict(result, "distinct-running-days")
    assert dict(issue.facts) == {
        "required_days": 2,
        "available_days": 1,
        "reducing_commitment": "requires-block-revision",
    }
    assert conflict(result, "unavailable").slots == (Slot.LONG_RUN,)
    week = generate_week(inputs)
    assert isinstance(week, WeekPlan)
    revision = change_run_commitment(week, 1)
    assert isinstance(revision, BlockRevisionRequired)
    assert revision.affected_week_numbers == tuple(range(2, 9))
    assert dict(revision.explanation.facts) == {"approved_days": 2, "requested_days": 1}
    assert revision.affected_generated_weeks == (week,)
    first = inputs.previous
    assert first is not None
    from_first = change_run_commitment(first, 1, later_weeks=(week,))
    assert isinstance(from_first, BlockRevisionRequired)
    assert from_first.affected_generated_weeks == (first, week)
    assert change_run_commitment(week, 2) == week
    assert week.inputs.block.version == revision.block_version


def test_weekend_move_revalidates_both_days_and_keeps_block_and_prescriptions() -> None:
    inputs = two_inputs()
    before = generate_week(inputs)
    assert isinstance(before, WeekPlan)
    changed = replace(AVAILABILITY, overrides=((SATURDAY, None),))
    after = propose_move(before, changed, Slot.LONG_RUN, SUNDAY, time(9))
    assert isinstance(after, WeekPlan)
    fallback = generate_week(replace(inputs, availability=changed))
    assert isinstance(fallback, WeekPlan) and fallback.days == after.days
    assert before.session(Slot.LONG_RUN).day == SATURDAY
    assert after.session(Slot.LONG_RUN) == replace(before.session(Slot.LONG_RUN), day=SUNDAY)
    assert after.inputs.block == before.inputs.block
    assert [s for d in after.days for s in d.sessions if s.slot != Slot.LONG_RUN] == [
        s for d in before.days for s in d.sessions if s.slot != Slot.LONG_RUN
    ]
    assert dict(next(f for f in after.explanation if f.rule == "move-session").facts) == {
        "from_day": SATURDAY,
        "from_start": time(9),
        "to_day": SUNDAY,
        "to_start": time(9),
        "seconds": 1500,
        "budget_minutes": 30,
        "old_day_available": False,
    }


def test_a5_legal_sunday_window_still_conflicts_with_fixed_monday() -> None:
    week = generate_week(two_inputs())
    assert isinstance(week, WeekPlan)
    ten = replace(RUN, start=time(10))
    changed = replace(
        AVAILABILITY, overrides=((SUNDAY, ten), (MONDAY, replace(LIFT, start=time(10))))
    )
    assert isinstance(propose_move(week, changed, Slot.LONG_RUN, SUNDAY, time(10)), WeekPlan)
    # A wider availability window cannot move the already scheduled neighboring session.
    fixed_monday = generate_week(replace(two_inputs(), fixed_next_monday_start=time(9)))
    assert isinstance(fixed_monday, WeekPlan)
    result = propose_move(fixed_monday, changed, Slot.LONG_RUN, SUNDAY, time(10))
    issue = conflict(result, "recovery-spacing")
    assert issue.slots == (Slot.LONG_RUN, Slot.FIRST_PRESS)
    assert dict(issue.facts) == {
        "run_day": SUNDAY,
        "press_day": MONDAY,
        "elapsed_seconds": 23 * 3600,
        "required_seconds": 24 * 3600,
    }


def test_a5_individually_permitted_changes_cannot_rise_together() -> None:
    block = replace(
        BLOCK, version="synthetic.wider.v1", thursday_kg_bounds=Target(D(30), D(30), D(32))
    )
    inputs = two_inputs(block)
    load_choice = Target(D(30), D(30), D(32))
    for dose in (PressDose(3, fixed(6), fixed(D(30))), PressDose(2, fixed(6), load_choice)):
        assert isinstance(generate_week(replace(inputs, thursday=dose)), WeekPlan)
    result = generate_week(replace(inputs, thursday=PressDose(3, fixed(6), load_choice)))
    assert conflict(result, "hold-load-when-adding-set").slots == (Slot.SECOND_PRESS,)
    assert isinstance(result, Conflicts) and len(result.findings) == 1


@pytest.mark.parametrize(
    ("dose", "rule"),
    [
        (PressDose(2, Target(6, 6, 7), fixed(D(30))), "press-reps-bounds"),
        (PressDose(2, fixed(6), Target(D(30), D(30), D("30.01"))), "press-external-kg-bounds"),
        (PressDose(2, Target(5, 6, 6), fixed(D(30))), "press-reps-bounds"),
        (PressDose(4, fixed(6), fixed(D(30))), "weekly-press-bounds"),
        (PressDose(0, fixed(6), fixed(D(30))), "weekly-press-bounds"),
    ],
)
def test_a5_worst_execution_endpoints_and_set_limits(dose: PressDose, rule: str) -> None:
    assert conflict(generate_week(replace(two_inputs(), thursday=dose)), rule).slots == (
        Slot.SECOND_PRESS,
    )


def test_explicit_increase_cannot_bypass_missing_feedback() -> None:
    result = generate_week(
        replace(two_inputs(), review=None, thursday=PressDose(3, fixed(6), fixed(D(30))))
    )
    conflict(result, "increase-requires-evidence")


def test_repeatability_including_rationale_and_conflicts() -> None:
    assert generate_week(two_inputs()) == generate_week(two_inputs())
    inputs = replace(two_inputs(), availability=replace(AVAILABILITY, equipment=frozenset()))
    assert generate_week(inputs) == generate_week(inputs)
    conflict(generate_week(inputs), "movement-restriction")


def test_unavailable_dates_distinct_days_and_combined_budget() -> None:
    week = week_one()
    tuesday = START + timedelta(days=1)
    result = propose_move(week, AVAILABILITY, Slot.LONG_RUN, tuesday, time(9))
    assert dict(conflict(result, "day-time-budget").facts) == {
        "day": tuesday,
        "requested_seconds": 2700,
        "available_seconds": 1800,
    }
    assert dict(conflict(result, "distinct-running-days").facts)["scheduled_days"] == 1
    assert conflict(result, "overlapping-sessions").slots == (Slot.SHORT_RUN, Slot.LONG_RUN)
    for day in (START + timedelta(days=2), START + timedelta(days=8)):
        conflict(propose_move(week, AVAILABILITY, Slot.LONG_RUN, day, time(9)), "unavailable")
    inputs = replace(
        week.inputs,
        availability=replace(AVAILABILITY, overrides=((START, replace(LIFT, minutes=39)),)),
    )
    conflict(generate_week(inputs), "day-time-budget")


@pytest.mark.parametrize(
    ("sunday", "wall"),
    [
        (date(2027, 3, 14), time(2, 30)),
        (date(2027, 11, 7), time(1, 30)),
    ],
)
def test_nonexistent_and_ambiguous_local_times(sunday: date, wall: time) -> None:
    first = week_one(replace(BLOCK, start=sunday - timedelta(days=6)))
    availability = replace(AVAILABILITY, overrides=((sunday, replace(RUN, start=wall)),))
    conflict(
        propose_move(first, availability, Slot.LONG_RUN, sunday, wall), "unresolved-local-time"
    )


def test_elapsed_hours_across_spring_clock_change_and_prior_week_recheck() -> None:
    sunday = date(2027, 3, 14)
    block = replace(BLOCK, start=sunday - timedelta(days=6))
    first = week_one(block)
    monday = sunday + timedelta(days=1)
    changed = replace(
        AVAILABILITY,
        overrides=((sunday, replace(RUN, start=time(1))), (monday, replace(LIFT, start=time(1)))),
    )
    result = propose_move(first, changed, Slot.LONG_RUN, sunday, time(1))
    assert dict(conflict(result, "recovery-spacing").facts)["elapsed_seconds"] == 23 * 3600
    moved = propose_move(
        first, replace(changed, overrides=changed.overrides[:1]), Slot.LONG_RUN, sunday, time(1)
    )
    assert isinstance(moved, WeekPlan)
    issue = conflict(generate_week(WeekInputs(block, changed, 2, moved)), "recovery-spacing")
    assert dict(issue.facts)["press_day"] == monday


def test_local_week_crossing_calendar_year() -> None:
    first = week_one(
        replace(BLOCK, start=date(2027, 12, 27)),
        replace(AVAILABILITY, zone=ZoneInfo("Pacific/Kiritimati")),
    )
    assert (first.days[0].day, first.days[-1].day) == (date(2027, 12, 27), date(2028, 1, 2))
    with pytest.raises(ValueError, match="Monday"):
        replace(BLOCK, start=date(2027, 1, 3))


def test_mismatched_generation_inputs() -> None:
    inputs = two_inputs()
    with pytest.raises(ValueError, match="predecessor"):
        generate_week(replace(inputs, previous=None))
    for review in (replace(REVIEW, week_start=MONDAY), replace(REVIEW, block_version="other")):
        with pytest.raises(ValueError, match="predecessor"):
            generate_week(replace(inputs, review=review))
    with pytest.raises(ValueError, match="detailed templates"):
        generate_week(replace(inputs, number=3))


def test_interval_duration_includes_every_recovery_and_bounded_endpoints() -> None:
    effort = Target(D(2), D(3), D(4))
    work = RunStep("work", Target(110, 120, 130), effort)
    recovery = RunStep("recovery", fixed(120), effort)
    run = RunSession(
        (
            RunStep("warmup", fixed(300), effort),
            Intervals(3, (work, recovery)),
            RunStep("cooldown", fixed(300), effort),
        )
    )
    assert run.duration_seconds == Target(1290, 22 * 60, 1350)
    assert run.reserved_seconds == 1350


def test_invalid_inputs_to_prescriptions() -> None:
    for values in ((D("NaN"), D(1), D(1)), (D(3), D(2), D(3)), (D(1), D(2), D("Infinity"))):
        with pytest.raises(ValueError):
            Target(*values)
    with pytest.raises(ValueError):
        RunStep("recovery", fixed(0), fixed(D(3)))
    with pytest.raises(ValueError):
        RunStep("work", fixed(30), fixed(D(11)))
    with pytest.raises(ValueError):
        Intervals(0, ())
    with pytest.raises(ValueError, match="integers"):
        PressDose(3, Target(6, 6, D("6.5")), fixed(D(30)))

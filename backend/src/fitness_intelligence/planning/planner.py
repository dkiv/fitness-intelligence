"""Candidate generation and review for the first two weeks of synthetic cycle A."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from enum import StrEnum
from zoneinfo import ZoneInfo

from .prescriptions import RunSession, StrengthSession, fixed
from .press_block import Availability, PressBlock, PressDose, easy_run, lift

DAY = timedelta(days=1)
RULES = "synthetic.press.e1.v2"


class Slot(StrEnum):
    FIRST_PRESS = "first-press"
    SHORT_RUN = "short-run"
    SECOND_PRESS = "second-press"
    LONG_RUN = "long-run"


@dataclass(frozen=True)
class Exposure:
    """Normalized evidence for one matched press slot.

    completed is the explicit whole-slot outcome (True for complete, False for
    incomplete, None for unknown). confirmed_rpes has one entry per distinct
    prescribed working set whose completion was independently confirmed. None
    in that tuple means its effort is unknown. inferred_sets counts prescribed
    working sets attributed by inference. Any positive count prevents progression
    because this summary has no set identities with which to resolve overlap.
    """

    completed: bool | None = None
    confirmed_rpes: tuple[Decimal | None, ...] = ()
    inferred_sets: int = 0

    def __post_init__(self) -> None:
        if self.inferred_sets < 0 or any(
            r is not None and not (r.is_finite() and 0 <= r <= 10) for r in self.confirmed_rpes
        ):
            raise ValueError("invalid observed count or effort")


@dataclass(frozen=True)
class WeekReview:
    block_version: str
    week_start: date
    as_of: datetime
    first_press: Exposure
    second_press: Exposure
    both_manageable: bool | None

    def __post_init__(self) -> None:
        if self.as_of.utcoffset() is None:
            raise ValueError("review as-of must be an instant")


@dataclass(frozen=True)
class Session:
    slot: Slot
    day: date
    start: time
    prescription: StrengthSession | RunSession


@dataclass(frozen=True)
class PlanDay:
    day: date
    sessions: tuple[Session, ...]  # Empty means explicit rest.

    @property
    def is_rest(self) -> bool:
        return not self.sessions


@dataclass(frozen=True)
class Finding:
    """Rule decision or conflict with affected slots and ordered, unit-labeled facts."""

    rule: str
    slots: tuple[Slot, ...]
    facts: tuple[tuple[str, Fact], ...]


@dataclass(frozen=True)
class WeekInputs:
    block: PressBlock
    availability: Availability
    number: int
    previous: WeekPlan | None = None
    review: WeekReview | None = None
    thursday: PressDose | None = None
    fixed_next_monday_start: time | None = None  # An already scheduled neighboring press.

    @property
    def start(self) -> date:
        return self.block.start + (self.number - 1) * 7 * DAY


@dataclass(frozen=True)
class WeekPlan:
    inputs: WeekInputs
    days: tuple[PlanDay, ...]
    explanation: tuple[Finding, ...]
    rule_version: str = RULES

    def session(self, slot: Slot) -> Session:
        return next(s for day in self.days for s in day.sessions if s.slot == slot)

    @property
    def press_sets(self) -> int:
        return sum(
            s.prescription.working_sets
            for day in self.days
            for s in day.sessions
            if isinstance(s.prescription, StrengthSession)
        )

    @property
    def running_seconds(self) -> int:
        return sum(
            s.prescription.duration_seconds.nominal
            for day in self.days
            for s in day.sessions
            if isinstance(s.prescription, RunSession)
        )


@dataclass(frozen=True)
class Conflicts:
    findings: tuple[Finding, ...]
    explanation: tuple[Finding, ...] = ()
    rule_version: str = RULES


@dataclass(frozen=True)
class BlockRevisionRequired:
    block_version: str
    affected_week_numbers: tuple[int, ...]
    affected_generated_weeks: tuple[WeekPlan, ...]
    explanation: Finding


type Result = WeekPlan | Conflicts
type Fact = bool | str | int | Decimal | date | time | None


def finding(rule: str, *slots: Slot, **facts: Fact) -> Finding:
    return Finding(rule, slots, tuple(facts.items()))


def _review(inputs: WeekInputs) -> tuple[bool, list[Finding]]:
    prior, review = inputs.previous, inputs.review
    if prior is None or prior.inputs.block != inputs.block or prior.inputs.number != 1:
        raise ValueError("week 2 requires the selected week 1 predecessor from this block")
    if prior.inputs.availability.zone != inputs.availability.zone:
        raise ValueError("keep the planning zone across the block")
    if review and (
        review.block_version != inputs.block.version or review.week_start != prior.inputs.start
    ):
        raise ValueError("review must describe the predecessor week and block version")
    reasons = []
    eligible = True
    for slot, exposure in (
        (Slot.FIRST_PRESS, review.first_press if review else Exposure()),
        (Slot.SECOND_PRESS, review.second_press if review else Exposure()),
    ):
        prescription = prior.session(slot).prescription
        assert isinstance(prescription, StrengthSession)
        rpes = exposure.confirmed_rpes
        measured = tuple(r for r in rpes if r is not None)
        peak = max(measured, default=None)
        complete = exposure.completed is True and len(rpes) == prescription.working_sets
        within_cap = (
            peak is not None and len(measured) == len(rpes) and peak <= inputs.block.max_rpe
        )
        slot_eligible = complete and within_cap and exposure.inferred_sets == 0
        eligible &= slot_eligible
        reasons.append(
            finding(
                "confirmed-exposure",
                slot,
                completed=exposure.completed,
                required_sets=prescription.working_sets,
                confirmed_sets=len(rpes),
                inferred_sets=exposure.inferred_sets,
                max_inferred_sets=0,
                measured_rpes=len(measured),
                peak_rpe=peak,
                cap_rpe=inputs.block.max_rpe,
                eligible=slot_eligible,
            )
        )
    feedback = review.both_manageable if review else None
    reasons.append(finding("manageable-feedback", both_manageable=feedback))
    return eligible and feedback is True, reasons


def _dose(inputs: WeekInputs) -> tuple[PressDose, list[Finding], list[Finding]]:
    block = inputs.block
    if inputs.number == 1:
        if inputs.review or inputs.previous or inputs.thursday:
            raise ValueError("week 1 uses the fixed fixture baseline")
        return (
            PressDose(2, fixed(6), fixed(block.baseline_kg)),
            [finding("establish-press", prior_confirmed_sets=5, tolerated_kg=block.baseline_kg)],
            [],
        )
    if inputs.number != 2:
        raise ValueError("only weeks 1 and 2 have detailed templates")
    eligible, reasons = _review(inputs)
    dose = inputs.thursday or PressDose(3 if eligible else 2, fixed(6), fixed(block.baseline_kg))
    intent = block.intents[1]
    assert inputs.previous is not None
    prior_sets = inputs.previous.press_sets
    sets = 3 + dose.sets
    issues = []
    allowed_max = min(intent.max_sets, prior_sets + block.max_added_sets)
    if not intent.min_sets <= sets <= allowed_max:
        issues.append(
            finding(
                "weekly-press-bounds",
                Slot.SECOND_PRESS,
                requested_sets=sets,
                min_sets=intent.min_sets,
                max_sets=allowed_max,
            )
        )
    for name, target, bounds in (
        ("reps", dose.reps, block.thursday_rep_bounds),
        ("external-kg", dose.external_kg, block.thursday_kg_bounds),
    ):
        if target.low < bounds.low or target.high > bounds.high:
            issues.append(
                finding(
                    "press-" + name + "-bounds",
                    Slot.SECOND_PRESS,
                    low=target.low,
                    high=target.high,
                    allowed_low=bounds.low,
                    allowed_high=bounds.high,
                )
            )
    added_load = dose.external_kg.high > block.baseline_kg
    if sets > prior_sets and dose.external_kg != fixed(block.baseline_kg):
        issues.append(
            finding(
                "hold-load-when-adding-set",
                Slot.SECOND_PRESS,
                prior_kg=block.baseline_kg,
                lower_kg=dose.external_kg.low,
                upper_kg=dose.external_kg.high,
                prior_sets=prior_sets,
                requested_sets=sets,
            )
        )
    if not eligible and (sets > prior_sets or added_load or dose.reps.high > 6):
        issues.append(finding("increase-requires-evidence", Slot.SECOND_PRESS))
    reasons.append(
        finding(
            "press-progression",
            Slot.SECOND_PRESS,
            eligible=eligible,
            prior_sets=prior_sets,
            proposed_sets=sets,
            upper_kg=dose.external_kg.high,
        )
    )
    return dose, reasons, issues


def _instant(day: date, start: time, zone: ZoneInfo) -> datetime | None:
    """A local reservation needs exactly one possible UTC instant."""
    if start.tzinfo is not None:
        raise ValueError("session starts must be local wall times")
    wall = datetime.combine(day, start)
    choices = {wall.replace(tzinfo=zone, fold=fold).astimezone(UTC) for fold in (0, 1)}
    valid = [t for t in choices if t.astimezone(zone).replace(tzinfo=None) == wall]
    return valid[0] if len(valid) == 1 else None


def _spacing(run: Session, press_day: date, press_time: time, inputs: WeekInputs) -> Finding:
    zone = inputs.availability.zone
    run_at = _instant(run.day, run.start, zone)
    press_at = _instant(press_day, press_time, zone)
    slots = (run.slot, Slot.FIRST_PRESS)
    if run_at is None or press_at is None:
        return finding(
            "unresolved-local-time",
            *slots,
            run_day=run.day,
            run_time=run.start,
            press_day=press_day,
            press_time=press_time,
            zone=zone.key,
        )
    elapsed = press_at - run_at
    required = inputs.block.hours_before_monday_press * 3600
    return finding(
        "recovery-spacing" if elapsed < timedelta(seconds=required) else "recovery-spacing-met",
        *slots,
        run_day=run.day,
        press_day=press_day,
        elapsed_seconds=Decimal(str(elapsed.total_seconds())),
        required_seconds=required,
    )


def _schedule(inputs: WeekInputs, sessions: tuple[Session, ...], reasons: list[Finding]) -> Result:
    availability = inputs.availability
    days = tuple(inputs.start + i * DAY for i in range(7))
    issues = []
    running_days = sum(
        1 for d in days if (w := availability.window(d)) and w.discipline == "running"
    )
    if running_days < 2:
        issues.append(
            finding(
                "distinct-running-days",
                Slot.SHORT_RUN,
                Slot.LONG_RUN,
                required_days=2,
                available_days=running_days,
                reducing_commitment="requires-block-revision",
            )
        )
    runs = [s for s in sessions if isinstance(s.prescription, RunSession)]
    if running_days >= 2 and len({s.day for s in runs}) < 2:
        issues.append(
            finding(
                "distinct-running-days",
                *(s.slot for s in runs),
                required_days=2,
                scheduled_days=len({s.day for s in runs}),
            )
        )
    for s in sessions:
        w = availability.window(s.day)
        discipline = "running" if isinstance(s.prescription, RunSession) else "strength"
        if s.day not in days or w is None or w.discipline != discipline or w.start != s.start:
            issues.append(
                finding(
                    "unavailable",
                    s.slot,
                    day=s.day,
                    requested_start=s.start,
                    discipline=discipline,
                    available_start=w.start if w else None,
                )
            )
        if _instant(s.day, s.start, availability.zone) is None:
            issues.append(
                finding(
                    "unresolved-local-time",
                    s.slot,
                    day=s.day,
                    start=s.start,
                    zone=availability.zone.key,
                )
            )
        if isinstance(s.prescription, StrengthSession):
            for e in s.prescription.exercises:
                if (
                    e.movement in availability.excluded_movements
                    or e.equipment not in availability.equipment
                ):
                    issues.append(
                        finding(
                            "movement-restriction",
                            s.slot,
                            movement=e.movement,
                            equipment=e.equipment,
                        )
                    )
    calendar = []
    for d in days:
        scheduled = tuple(s for s in sessions if s.day == d)
        calendar.append(PlanDay(d, scheduled))
        slots = tuple(s.slot for s in scheduled)
        if len(scheduled) > 1:
            issues.append(finding("overlapping-sessions", *slots, day=d))
        reserved = sum(s.prescription.reserved_seconds for s in scheduled)
        window = availability.window(d)
        if window and reserved > window.minutes * 60:
            issues.append(
                finding(
                    "day-time-budget",
                    *slots,
                    day=d,
                    requested_seconds=reserved,
                    available_seconds=window.minutes * 60,
                )
            )
    # The next local Monday is a reserved strength boundary even in an intent-only week.
    next_monday = inputs.start + 7 * DAY
    next_window = availability.window(next_monday)
    next_time = (
        next_window.start if next_window and next_window.discipline == "strength" else time(9)
    )
    if inputs.fixed_next_monday_start is not None:
        next_time = inputs.fixed_next_monday_start
    checks = [_spacing(s, next_monday, next_time, inputs) for s in runs]
    if inputs.previous:
        first = next(s for s in sessions if s.slot == Slot.FIRST_PRESS)
        checks.extend(
            _spacing(s, first.day, first.start, inputs)
            for d in inputs.previous.days
            for s in d.sessions
            if isinstance(s.prescription, RunSession)
        )
    for check in checks:
        (reasons if check.rule == "recovery-spacing-met" else issues).append(check)
    if issues:
        return Conflicts(tuple(issues), tuple(reasons))
    reasons.append(
        finding(
            "retain-easy-runs",
            Slot.SHORT_RUN,
            Slot.LONG_RUN,
            distinct_days=2,
            minutes=sum(inputs.block.intents[inputs.number - 1].run_minutes),
        )
    )
    return WeekPlan(inputs, tuple(calendar), tuple(reasons))


def generate_week(inputs: WeekInputs) -> Result:
    return _build_week(inputs, {}, None)


def _build_week(
    inputs: WeekInputs, placements: dict[Slot, tuple[date, time]], move: Finding | None
) -> Result:
    dose, reasons, issues = _dose(inputs)
    if issues:
        return Conflicts(tuple(issues), tuple(reasons))
    block, start = inputs.block, inputs.start
    short, long = block.intents[inputs.number - 1].run_minutes
    saturday = inputs.availability.window(start + 5 * DAY)
    sunday = inputs.availability.window(start + 6 * DAY)
    use_sunday = (saturday is None or saturday.discipline != "running") and (
        sunday is not None and sunday.discipline == "running"
    )
    sessions = []
    for slot, offset, prescription in (
        (Slot.FIRST_PRESS, 0, lift(block, PressDose(3, fixed(5), fixed(block.baseline_kg)))),
        (Slot.SHORT_RUN, 1, easy_run(short)),
        (Slot.SECOND_PRESS, 3, lift(block, dose)),
        (Slot.LONG_RUN, 6 if use_sunday else 5, easy_run(long)),
    ):
        day = start + offset * DAY
        window = inputs.availability.window(day)
        day, start_time = placements.get(slot, (day, window.start if window else time(9)))
        sessions.append(Session(slot, day, start_time, prescription))
    if move:
        reasons.append(move)
    elif use_sunday:
        reasons.append(
            finding(
                "weekend-fallback",
                Slot.LONG_RUN,
                unavailable_day=start + 5 * DAY,
                proposed_day=start + 6 * DAY,
            )
        )
    return _schedule(inputs, tuple(sessions), reasons)


def propose_move(
    plan: WeekPlan, availability: Availability, slot: Slot, day: date, start: time
) -> Result:
    """Revalidate the whole week under current availability and preserve the logical slot."""
    if availability.zone != plan.inputs.availability.zone:
        raise ValueError("a move must retain the planning zone")
    before = plan.session(slot)
    inputs = replace(plan.inputs, availability=availability)
    placements = {s.slot: (s.day, s.start) for d in plan.days for s in d.sessions}
    placements[slot] = (day, start)
    window = availability.window(day)
    old_window = availability.window(before.day)
    move = finding(
        "move-session",
        slot,
        from_day=before.day,
        from_start=before.start,
        to_day=day,
        to_start=start,
        seconds=before.prescription.reserved_seconds,
        budget_minutes=window.minutes if window else None,
        old_day_available=old_window is not None
        and old_window.start == before.start
        and old_window.discipline
        == ("running" if isinstance(before.prescription, RunSession) else "strength"),
    )
    return _build_week(inputs, placements, move)


def change_run_commitment(
    plan: WeekPlan, distinct_days: int, *, later_weeks: tuple[WeekPlan, ...] = ()
) -> WeekPlan | BlockRevisionRequired:
    """Supply any generated later weeks for the review of a change effective from this week."""
    if distinct_days < 0 or distinct_days > 7:
        raise ValueError("distinct running days must be within 0–7")
    if distinct_days == 2:
        return plan
    generated = (plan, *sorted(later_weeks, key=lambda week: week.inputs.number))
    numbers = [w.inputs.number for w in generated]
    if any(w.inputs.block != plan.inputs.block for w in later_weeks) or numbers != sorted(
        set(numbers)
    ):
        raise ValueError("supply distinct later weeks of the same block")
    return BlockRevisionRequired(
        plan.inputs.block.version,
        tuple(range(plan.inputs.number, len(plan.inputs.block.intents) + 1)),
        generated,
        finding("change-running-objective", approved_days=2, requested_days=distinct_days),
    )

"""Cycle A. All programming parameters in this module are synthetic fixture values."""

from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal
from enum import StrEnum
from typing import Literal
from zoneinfo import ZoneInfo

from .prescriptions import Exercise, RunSession, RunStep, SetGroup, StrengthSession, Target, fixed

type Discipline = Literal["strength", "running"]


class Phase(StrEnum):
    ESTABLISH = "establish comparable exposures"
    ACCUMULATE = "accumulate"
    DELOAD = "deload"
    SPECIFICITY = "emphasize assessment movement"
    REDUCE = "reduce volume"
    ASSESS = "assess on second exposure"


@dataclass(frozen=True)
class Goal:
    priority: int
    measure: str


@dataclass(frozen=True)
class WeekIntent:
    phase: Phase
    min_sets: int
    max_sets: int
    run_minutes: tuple[int, int]

    def __post_init__(self) -> None:
        if not 0 < self.min_sets <= self.max_sets or len(self.run_minutes) != 2:
            raise ValueError("the fixture requires ordered press bounds and two run targets")
        if min(self.run_minutes) <= 10:
            raise ValueError("easy runs need work time after warm-up and cool-down")


@dataclass(frozen=True)
class PressBlock:
    """Versioned synthetic press objective, predecessor dose and eight weekly intents."""

    version: str = "synthetic.press.v1"
    start: date = date(2027, 1, 4)
    goals: tuple[Goal, ...] = (
        Goal(1, "Repeat a submaximal press assessment in week 8"),
        Goal(2, "Retain two easy runs each week"),
    )
    objective: str = "Increase comparable press exposure while maintaining two easy runs"
    intents: tuple[WeekIntent, ...] = (
        WeekIntent(Phase.ESTABLISH, 5, 5, (20, 25)),
        WeekIntent(Phase.ACCUMULATE, 5, 6, (20, 25)),
        WeekIntent(Phase.ACCUMULATE, 5, 6, (20, 25)),
        WeekIntent(Phase.DELOAD, 4, 4, (15, 15)),
        WeekIntent(Phase.SPECIFICITY, 5, 6, (20, 20)),
        WeekIntent(Phase.SPECIFICITY, 5, 6, (20, 20)),
        WeekIntent(Phase.REDUCE, 4, 4, (15, 15)),
        WeekIntent(Phase.ASSESS, 3, 3, (15, 15)),
    )
    baseline_kg: Decimal = Decimal(30)
    thursday_kg_bounds: Target[Decimal] = fixed(Decimal(30))
    thursday_rep_bounds: Target[int] = fixed(6)
    max_added_sets: int = 1
    max_rpe: Decimal = Decimal(7)
    hours_before_monday_press: int = 24

    def __post_init__(self) -> None:
        if self.start.weekday() != 0 or len(self.intents) != 8:
            raise ValueError("the fixture block starts on a local Monday and has eight weeks")
        if not self.intents[0].min_sets <= 5 <= self.intents[0].max_sets:
            raise ValueError("week 1 must accommodate the five-set baseline")
        if self.max_added_sets < 0 or self.hours_before_monday_press < 0:
            raise ValueError("progression and spacing limits must be nonnegative")
        if not self.max_rpe.is_finite() or not 0 <= self.max_rpe <= 10:
            raise ValueError("effort cap must be within 0–10")
        if not self.baseline_kg.is_finite():
            raise ValueError("baseline load must be finite")
        if not self.thursday_kg_bounds.low <= self.baseline_kg <= self.thursday_kg_bounds.high:
            raise ValueError("baseline external load must be inside the block envelope")
        if not 1 <= self.thursday_rep_bounds.low <= 6 <= self.thursday_rep_bounds.high:
            raise ValueError("baseline Thursday reps must be inside the block envelope")


@dataclass(frozen=True)
class Window:
    discipline: Discipline
    start: time
    minutes: int

    def __post_init__(self) -> None:
        if self.minutes <= 0 or self.start.tzinfo is not None:
            raise ValueError("windows require positive minutes and a local start")


LIFT = Window("strength", time(9), 40)
RUN = Window("running", time(9), 30)


@dataclass(frozen=True)
class Availability:
    zone: ZoneInfo = ZoneInfo("America/Toronto")
    weekdays: tuple[Window | None, ...] = (LIFT, RUN, None, LIFT, None, RUN, RUN)
    overrides: tuple[tuple[date, Window | None], ...] = ()
    excluded_movements: frozenset[str] = frozenset()
    equipment: frozenset[str] = frozenset({"barbell"})

    def __post_init__(self) -> None:
        if len(self.weekdays) != 7 or len(dict(self.overrides)) != len(self.overrides):
            raise ValueError("supply seven weekdays and at most one override per date")

    def window(self, day: date) -> Window | None:
        return dict(self.overrides).get(day, self.weekdays[day.weekday()])


@dataclass(frozen=True)
class PressDose:
    """Proposed Thursday working sets. Check all execution endpoints against the block."""

    sets: int
    reps: Target[int]
    external_kg: Target[Decimal]

    def __post_init__(self) -> None:
        if type(self.sets) is not int or not self.reps.has_integer_endpoints():
            raise ValueError("press set counts and rep endpoints must be integers")


def lift(block: PressBlock, dose: PressDose) -> StrengthSession:
    groups = (
        SetGroup("warmup", 1, fixed(5), fixed(Decimal(15)), None, None, effort_cue="easy"),
        SetGroup("working", dose.sets, dose.reps, dose.external_kg, block.max_rpe, 180),
    )
    return StrengthSession((Exercise("press", "Press", "barbell", groups),), 40 * 60)


def easy_run(minutes: int) -> RunSession:
    effort = Target(Decimal(2), Decimal(3), Decimal(4))
    return RunSession(
        (
            RunStep("warmup", fixed(300), effort),
            RunStep("work", fixed((minutes - 10) * 60), effort),
            RunStep("cooldown", fixed(300), effort),
        )
    )

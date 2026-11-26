"""Descriptive comparisons over the same accepted facts used by the D1D report."""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import date
from decimal import Context, Decimal, localcontext
from itertools import pairwise
from typing import Literal
from uuid import UUID

from fitness_intelligence.analytics.exposure import ActivityDay, Outing
from fitness_intelligence.analytics.references import (
    RecoveryReference,
    RecoveryRegime,
    RunningReference,
    StrengthConsistency,
    known_context,
    observed_consistency,
    recovery_reference,
    running_references,
    validate_regimes,
)
from fitness_intelligence.analytics.strength import CATEGORIES, StrengthFact, ranked_estimates
from fitness_intelligence.analytics.weekly import WeeklyReport
from fitness_intelligence.domain.endurance import DailyMetric


@dataclass(frozen=True)
class StrengthTask:
    movement: str | None
    variation: str | None
    equipment: str | None
    load_convention: str | None
    role: str | None
    protocol: str | None
    effort_basis: Literal["matched_rpe", "reviewed_protocol"] = "matched_rpe"
    match_ordinal: bool = True

    def __post_init__(self) -> None:
        if type(self.match_ordinal) is not bool:
            raise ValueError("set ordinal policy must be explicit")


@dataclass(frozen=True)
class RunningTask:
    distance_m: Decimal | int | None
    course_or_protocol: str | None
    timing: Literal["elapsed_s", "moving_s", "duration_s"] | None
    effort: str | None
    conditions: str | None
    restrictions_or_interruptions: str | None


@dataclass(frozen=True)
class Review[T]:
    task: T
    evidence: str

    def __post_init__(self) -> None:
        if not known_context(self.evidence):
            raise ValueError("a comparison review requires an evidence reference")


@dataclass(frozen=True)
class StrengthPoint:
    fact: StrengthFact
    review: Review[StrengthTask] | None
    reasons: tuple[str, ...]
    estimated_1rm_kg: Decimal | None = None
    workout_best: bool = False

    @property
    def series_key(self) -> tuple | None:
        if self.review is None or self.reasons:
            return None
        f, task = self.fact, self.review.task
        return (
            f.source,
            f.series,
            f.mapping_version,
            f.hash_contract,
            f.execution,
            f.row.kind,
            task,
            f.row.set_position if task.match_ordinal else None,
        )


def _strength_point(f: StrengthFact, review: Review[StrengthTask] | None) -> StrengthPoint:
    row = f.row
    reasons = []
    if not f.series or not f.series.template_id or not f.mapping_version:
        reasons.append("unverified_movement")
    if f.execution not in ("confirmed", "inferred") or CATEGORIES.get(row.kind) != "working":
        reasons.append("ineligible_working_set")
    if row.distance_m not in (None, 0) or row.duration_seconds not in (None, 0):
        reasons.append("timed_or_distance_task")
    if review is None:
        reasons.append("no_task_review")
    else:
        t = review.task
        if not all(
            known_context(v) for v in (t.movement, t.variation, t.equipment, t.role, t.protocol)
        ):
            reasons.append("incomplete_strength_context")
        if f.load_convention != "external_kg" or t.load_convention != f.load_convention:
            reasons.append("unverified_load_convention")
        if t.effort_basis not in ("matched_rpe", "reviewed_protocol"):
            reasons.append("unknown_effort_basis")
        if t.match_ordinal and row.set_position is None:
            reasons.append("unknown_set_ordinal")
    return StrengthPoint(f, review, tuple(reasons))


@dataclass(frozen=True)
class Delta:
    value: Decimal | int | None
    reasons: tuple[str, ...] = ()


def _change(earlier: Decimal | int, later: Decimal | int) -> Delta:
    with localcontext(Context(prec=38)):
        return Delta(later - earlier)


@dataclass(frozen=True)
class StrengthDifference:
    earlier: StrengthPoint
    later: StrengthPoint
    reps_at_fixed_load: Delta
    kg_at_fixed_reps: Delta
    achieved_rpe_at_fixed_work: Delta
    estimated_1rm_kg: Delta


def compare_strength(a: StrengthPoint, b: StrengthPoint) -> StrengthDifference:
    if a.fact.source != b.fact.source:
        raise ValueError("strength comparison crosses sources")
    x, y = a.fact.row, b.fact.row
    reasons = tuple(dict.fromkeys(a.reasons + b.reasons))
    if not reasons and a.series_key != b.series_key:
        reasons = ("different_strength_series",)
    if x.workout_id == y.workout_id or x.started_at >= y.started_at:
        reasons += ("requires_successive_workouts",)
    if reasons:
        gap = Delta(None, reasons)
        return StrengthDifference(a, b, gap, gap, gap, gap)
    same_load = x.weight_kg is not None and x.weight_kg == y.weight_kg
    same_reps = x.repetitions is not None and x.repetitions == y.repetitions
    effort_known = all(v is not None and v.is_finite() and 0 <= v <= 10 for v in (x.rpe, y.rpe))
    effort = Delta(None, ("missing_or_invalid_rpe",))
    if effort_known:
        effort = (
            _change(x.rpe, y.rpe) if same_load and same_reps else Delta(None, ("different_work",))
        )
    if a.review.task.effort_basis == "matched_rpe" and (not effort_known or x.rpe != y.rpe):
        gap = Delta(None, ("different_rpe" if effort_known else "missing_or_invalid_rpe",))
        return StrengthDifference(a, b, gap, gap, effort, gap)
    reps = Delta(None, ("requires_fixed_load_and_recorded_reps",))
    if same_load and x.repetitions is not None and y.repetitions is not None:
        reps = _change(x.repetitions, y.repetitions)
    load = Delta(None, ("requires_fixed_reps_and_recorded_load",))
    if same_reps and x.weight_kg is not None and y.weight_kg is not None:
        load = _change(x.weight_kg, y.weight_kg)
    estimate = Delta(None, ("requires_eligible_workout_bests",))
    if a.workout_best and b.workout_best:
        estimate = _change(a.estimated_1rm_kg, b.estimated_1rm_kg)
    return StrengthDifference(a, b, reps, load, effort, estimate)


@dataclass(frozen=True)
class RunningPoint:
    fact: Outing
    acquisition_day: ActivityDay
    review: Review[RunningTask] | None
    reasons: tuple[str, ...]

    @property
    def series_key(self) -> tuple | None:
        if self.review is None or self.reasons:
            return None
        return (self.fact.source, self.fact.subtype, self.fact.mapping_version, self.review.task)


def _running_point(f: Outing, day: ActivityDay, review: Review[RunningTask] | None) -> RunningPoint:
    reasons = list(day.discrepancies)
    if f.activity_issues:
        reasons.append("activity_reconciliation_hold")
    if not f.mapping_version or not f.subtype:
        reasons.append("unverified_running_measurement")
    if review is None:
        reasons.append("no_task_review")
    else:
        t = review.task
        if (
            t.distance_m is None
            or not Decimal(t.distance_m).is_finite()
            or t.distance_m <= 0
            or f.distance_m != t.distance_m
        ):
            reasons.append("unverified_equivalent_distance")
        if t.timing not in ("duration_s", "elapsed_s", "moving_s"):
            reasons.append("unknown_timing_convention")
        elif getattr(f, t.timing) is None or getattr(f, t.timing) <= 0:
            reasons.append("missing_or_nonpositive_time")
        for name in ("course_or_protocol", "effort", "conditions", "restrictions_or_interruptions"):
            if not known_context(getattr(t, name)):
                reasons.append("unknown_" + name)
    return RunningPoint(f, day, review, tuple(reasons))


@dataclass(frozen=True)
class RunningDifference:
    earlier: RunningPoint
    later: RunningPoint
    seconds: Delta


def compare_running(a: RunningPoint, b: RunningPoint) -> RunningDifference:
    if a.fact.source != b.fact.source:
        raise ValueError("running comparison crosses sources")
    reasons = tuple(dict.fromkeys(a.reasons + b.reasons))
    if not reasons and a.series_key != b.series_key:
        reasons = ("different_running_task",)
    if a.fact.started_at >= b.fact.started_at:
        reasons += ("requires_successive_outings",)
    if reasons:
        return RunningDifference(a, b, Delta(None, reasons))
    timing = a.review.task.timing
    return RunningDifference(a, b, _change(getattr(a.fact, timing), getattr(b.fact, timing)))


def _estimated_sets(
    points: tuple[StrengthPoint, ...],
    weekly: WeeklyReport,
    rpe_range: tuple[Decimal, Decimal] | None,
) -> tuple[StrengthPoint, ...]:
    # The shared selector orders by the unrounded numerator then set ID, even for rounded ties.
    by_id = {p.fact.row.set_id: p for p in points}
    for tier in ("confirmed", "inferred"):
        progression = ranked_estimates(
            (p.fact for p in points), weekly.period, execution=tier, rpe_range=rpe_range
        )
        selected = set()
        for ident, estimate in progression.select("set_id", "estimated_1rm_kg").iter_rows():
            set_id = UUID(ident)
            point = by_id[set_id]
            group = (point.fact.row.workout_id, point.series_key)
            by_id[set_id] = replace(
                point,
                estimated_1rm_kg=estimate,
                workout_best=point.series_key is not None and group not in selected,
            )
            selected.add(group)
    return tuple(by_id.values())


@dataclass(frozen=True)
class PerformanceReport:
    weekly: WeeklyReport
    strength: tuple[StrengthPoint, ...]
    running: tuple[RunningPoint, ...]
    recovery_regimes: tuple[RecoveryRegime, ...]
    rpe_range: tuple[Decimal, Decimal] | None
    consistency: StrengthConsistency | None
    policy_version: str = "comparable-performance-v1"

    def recovery_reference(self, day: date, metric: DailyMetric) -> RecoveryReference:
        return recovery_reference(self.weekly, day, metric, self.recovery_regimes)

    def running_references(self, comparison_week: date) -> tuple[RunningReference, ...]:
        return running_references(self.weekly, comparison_week)

    def fixed_work_comparisons(
        self, fixed: Literal["load", "repetitions"]
    ) -> tuple[StrengthDifference, ...]:
        """Compare successive like-position sets at one recorded load or rep count."""
        if fixed not in ("load", "repetitions"):
            raise ValueError("select load or repetitions")
        series = defaultdict(list)
        for p in self.strength:
            row = p.fact.row
            value = row.weight_kg if fixed == "load" else row.repetitions
            if p.series_key is not None and value is not None:
                series[p.series_key, row.exercise_position, row.set_position, value].append(p)
        return tuple(
            compare_strength(a, b) for points in series.values() for a, b in pairwise(points)
        )

    @property
    def successive_estimates(self) -> tuple[StrengthDifference, ...]:
        series = defaultdict(list)
        for p in self.strength:
            if p.workout_best:
                series[p.series_key].append(p)
        return tuple(
            compare_strength(a, b) for points in series.values() for a, b in pairwise(points)
        )

    @property
    def successive_runs(self) -> tuple[RunningDifference, ...]:
        series = defaultdict(list)
        for p in self.running:
            if p.series_key is not None:
                series[p.series_key].append(p)
        return tuple(
            compare_running(a, b) for points in series.values() for a, b in pairwise(points)
        )


def analyze_performance(
    weekly: WeeklyReport,
    *,
    strength_reviews: Mapping[StrengthFact, Review[StrengthTask]] | None = None,
    running_reviews: Mapping[Outing, Review[RunningTask]] | None = None,
    recovery_regimes: tuple[RecoveryRegime, ...] = (),
    rpe_range: tuple[Decimal, Decimal] | None = None,
) -> PerformanceReport:
    """Attach reviews to the exact, current D1D facts from the selected snapshot."""
    strengths = sorted(
        (f for w in weekly.weeks if w.strength for f in w.strength.facts if f.row.set_id),
        key=lambda f: (
            f.row.started_at,
            f.row.workout_id,
            f.row.exercise_position,
            f.row.set_position,
            f.row.set_id,
        ),
    )
    run_days = {
        f: day
        for w in weekly.weeks
        if w.endurance
        for day in w.endurance.days
        for f in day.facts
        if f.sport == "running"
    }
    runs = sorted(run_days, key=lambda f: (f.started_at, f.workout_id))
    strength_reviews = strength_reviews or {}
    running_reviews = running_reviews or {}
    if strength_reviews.keys() - set(strengths) or running_reviews.keys() - set(runs):
        raise ValueError("review must identify an exact selected observation")
    regimes = validate_regimes(weekly, recovery_regimes)
    points = tuple(_strength_point(f, strength_reviews.get(f)) for f in strengths)
    return PerformanceReport(
        weekly,
        _estimated_sets(points, weekly, rpe_range),
        tuple(_running_point(f, run_days[f], running_reviews.get(f)) for f in runs),
        regimes,
        rpe_range,
        observed_consistency(weekly),
    )

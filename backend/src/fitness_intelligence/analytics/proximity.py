"""Calendar-qualified co-occurrence of recorded lower-body strength and running."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, timedelta
from decimal import Context, Decimal, localcontext
from uuid import UUID

from fitness_intelligence.analytics.performance import (
    PerformanceReport,
    RunningPoint,
    StrengthPoint,
)
from fitness_intelligence.analytics.strength import DAY
from fitness_intelligence.domain.endurance import Source


@dataclass(frozen=True)
class SessionTiming:
    order: str
    start_to_start_s: Decimal
    end_to_start_s: Decimal | None
    relation: str


def _seconds(delta: timedelta) -> Decimal:
    with localcontext(Context(prec=38)):
        return Decimal(delta // timedelta(microseconds=1)) / 1_000_000


def _timing(strength: StrengthPoint, run: RunningPoint) -> SessionTiming:
    row, outing = strength.fact.row, run.fact
    lift_start, run_start = row.started_at.astimezone(UTC), outing.started_at.astimezone(UTC)
    if lift_start == run_start:
        overlap = all(
            end is not None and end.astimezone(UTC) > run_start
            for end in (row.ended_at, outing.ended_at)
        )
        return SessionTiming("same_start", Decimal(0), None, "overlap" if overlap else "same_start")
    if lift_start < run_start:
        order, earlier_end, later_start, later_end = (
            "strength_first",
            row.ended_at,
            run_start,
            outing.ended_at,
        )
    else:
        order, earlier_end, later_start, later_end = (
            "run_first",
            outing.ended_at,
            lift_start,
            row.ended_at,
        )
    starts = _seconds(abs(run_start - lift_start))
    if earlier_end is None:
        return SessionTiming(order, starts, None, "earlier_end_unknown")
    gap = _seconds(later_start - earlier_end.astimezone(UTC))
    relation = "sequential"
    if gap < 0:
        relation = (
            "overlap"
            if later_end is not None and later_end.astimezone(UTC) > later_start
            else "starts_during_earlier"
        )
    return SessionTiming(order, starts, gap, relation)


@dataclass(frozen=True)
class ProximityPair:
    strength_workout_id: UUID
    running_workout_id: UUID
    strength_source: Source
    running_source: Source
    strength_date: date
    running_date: date
    run_minus_strength_days: int
    evidence: str
    confirmed_sets: tuple[UUID, ...]
    inferred_sets: tuple[UUID, ...]
    exercise_ids: tuple[UUID, ...]
    recorded_reps: int | None
    sets_with_reps: int
    timing: SessionTiming


@dataclass(frozen=True)
class ProximityExclusion:
    running_workout_id: UUID
    provider_date: date
    report_date: date
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class TrainingProximity:
    pairs: tuple[ProximityPair, ...]
    excluded_runs: tuple[ProximityExclusion, ...]


def training_proximity(performance: PerformanceReport) -> TrainingProximity:
    daily = performance.weekly.daily_report
    if daily.hevy_profile is None or daily.endurance_source is None:
        return TrainingProximity((), ())
    # D1D determines evidenced working-set eligibility and reviewed lower-body membership.
    selected: dict[UUID, StrengthPoint] = {p.fact.row.set_id: p for p in performance.strength}
    by_date: dict[date, dict[UUID, list[StrengthPoint]]] = defaultdict(lambda: defaultdict(list))
    for day in daily.days:
        lower = day.strength.lower_body
        for set_id in (*lower.confirmed, *lower.inferred):
            p = selected[set_id]
            if (
                p.fact.source.owner_id != daily.owner_id
                or p.fact.source.source_account_id != daily.hevy_profile.source_account_id
            ):
                raise ValueError("strength source differs from report selection")
            by_date[p.fact.report_date][p.fact.row.workout_id].append(p)

    pairs, withheld = [], []
    for run in performance.running:
        outing, native = run.fact, run.acquisition_day
        if outing.source != daily.endurance_source or outing.source.owner_id != daily.owner_id:
            raise ValueError("running source differs from report selection")
        reasons = list(native.discrepancies)
        if outing.provider_date != outing.report_date:
            reasons.append("provider_report_date_disagreement")
        elif not native.calendar_aligned:
            reasons.append("calendar_alignment_unverified")
        if outing.activity_issues:
            reasons.append("activity_reconciliation_hold")
        if reasons:
            withheld.append(
                ProximityExclusion(
                    outing.workout_id, outing.provider_date, outing.report_date, tuple(reasons)
                )
            )
            continue
        for offset in (-1, 0, 1):
            strength_date = outing.report_date + offset * DAY
            for workout, points in by_date.get(strength_date, {}).items():
                confirmed = tuple(
                    p.fact.row.set_id for p in points if p.fact.execution == "confirmed"
                )
                inferred = tuple(
                    p.fact.row.set_id for p in points if p.fact.execution == "inferred"
                )
                reps = [
                    p.fact.row.repetitions for p in points if p.fact.row.repetitions is not None
                ]
                pairs.append(
                    ProximityPair(
                        workout,
                        outing.workout_id,
                        points[0].fact.source,
                        outing.source,
                        strength_date,
                        outing.report_date,
                        -offset,
                        "confirmed_and_inferred"
                        if confirmed and inferred
                        else "confirmed"
                        if confirmed
                        else "tentative_inferred",
                        confirmed,
                        inferred,
                        tuple(dict.fromkeys(p.fact.row.exercise_id for p in points)),
                        sum(reps) if reps else None,
                        len(reps),
                        _timing(points[0], run),
                    )
                )
    return TrainingProximity(tuple(pairs), tuple(withheld))

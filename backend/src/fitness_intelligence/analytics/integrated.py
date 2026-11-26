"""A compact focus-week view and scoped evidence inspection over a single D1 snapshot."""

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from fitness_intelligence.analytics.exposure import ExposureValue, SportExposure
from fitness_intelligence.analytics.longitudinal import Coverage, ReportDay
from fitness_intelligence.analytics.performance import PerformanceReport, StrengthDifference
from fitness_intelligence.analytics.proximity import TrainingProximity, training_proximity
from fitness_intelligence.analytics.references import (
    REFERENCE_METRICS,
    RecoveryReference,
    RunningReference,
)
from fitness_intelligence.analytics.strength import DAY, monday
from fitness_intelligence.analytics.weekly import Week, WeekCoverage, WeeklyCalories
from fitness_intelligence.domain.endurance import DailyMetric, Source


def _encode(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: getattr(value, f.name) for f in fields(value)}
    if isinstance(value, datetime):
        if value.utcoffset() is None:
            raise ValueError("expected an aware instant")
        return value.astimezone(UTC).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, ZoneInfo):
        return value.key
    if isinstance(value, frozenset):
        return sorted(value)
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, UUID):
        return str(value)
    raise TypeError(f"unsupported report value {type(value).__name__}")


def report_json(view: object) -> str:
    """Serialize a summary or a single inspection without loss of decimal precision."""
    return json.dumps(view, default=_encode, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _amount(v: ExposureValue) -> dict:
    return dict(
        value=v.value,
        status=v.status,
        measured_workouts=v.eligible_count,
        missing_workouts=len(v.missing_workouts),
    )


def _sport(s: SportExposure) -> dict:
    return dict(
        sport=s.sport,
        subtype=s.subtype,
        dates=s.dates,
        sessions=_amount(s.sessions),
        distance_m=_amount(s.distance_m),
        activity_s=_amount(s.duration_s),
        moving_s=_amount(s.moving_s),
        elapsed_s=_amount(s.elapsed_s),
        longest_workout=s.longest_observed.workout_id if s.longest_observed else None,
        reasons=s.reasons,
    )


def _kcal(c: WeeklyCalories) -> dict:
    return dict(
        subtotal_kcal=c.observed_subtotal_kcal,
        mean_kcal=c.mean_per_eligible_date_kcal,
        eligible_dates=c.sample.eligible_dates,
        requested_dates=c.sample.requested_date_count,
        status=c.subtotal_status,
        method=c.method,
        date_statuses=dict(Counter(cell.status for _, cell in c.sample.daily)),
    )


def _reference(r: RunningReference) -> dict:
    return dict(
        metric=r.metric,
        sampled_week_median=r.median,
        comparison_week=r.comparison_week,
        contributing_weeks=[w.monday for w in r.contributing],
        reasons=r.reasons,
        weeks=[
            dict(
                monday=w.monday,
                observed=_amount(w.observed) if w.observed else None,
                exclusions=w.reasons,
            )
            for w in r.weeks
        ],
        habitual_exposure="insufficient_evidence",
    )


def _recovery_ref(r: RecoveryReference) -> dict:
    return dict(
        metric=r.metric,
        unit="s" if r.metric == DailyMetric.SLEEP else "bpm",
        target_date=r.day,
        window_start=r.window_start,
        median=r.median,
        minimum=r.minimum,
        maximum=r.maximum,
        n=r.n,
        reasons=r.reasons,
        regime=r.regime,
    )


def _difference(d: StrengthDifference) -> dict:
    return dict(
        earlier_set=d.earlier.fact.row.set_id,
        later_set=d.later.fact.row.set_id,
        earlier_workout=d.earlier.fact.row.workout_id,
        later_workout=d.later.fact.row.workout_id,
        execution=d.later.fact.execution,
        reps_at_fixed_load=d.reps_at_fixed_load,
        kg_at_fixed_reps=d.kg_at_fixed_reps,
        achieved_rpe_at_fixed_work=d.achieved_rpe_at_fixed_work,
        estimated_1rm_kg=d.estimated_1rm_kg,
    )


def _coverage(week: Week) -> list[dict]:
    groups: dict[tuple[Source, str], list[Coverage]] = defaultdict(list)
    rows = [c for series in week.intake.coverage for c in series.days]
    rows.extend(week.weight.coverage.days)
    if week.expenditure:
        rows.extend(week.expenditure.coverage.days)
    if week.endurance:
        for day in week.endurance.days:
            rows.extend((day.activities, day.instructions))
    if week.recovery:
        rows.extend(week.recovery.coverage)
    for c in rows:
        groups[c.source, c.category].append(c)
    result = []
    for (source, category), days in groups.items():
        series = WeekCoverage(source, tuple(days))
        result.append(
            dict(
                source=source,
                category=category,
                status_counts=dict(series.acquisition_counts),
                open_issue_dates=series.unresolved_dates,
            )
        )
    return result


def _strength_summary(p: PerformanceReport, w: Week) -> dict:
    dates = w.requested_dates
    s = w.strength
    return dict(
        workouts=s.workouts,
        workout_dates=s.workout_dates,
        confirmed_working_sets=len(s.working.confirmed),
        inferred_working_sets=len(s.working.inferred),
        recorded_reps=s.working.repetitions,
        sets_with_reps=len(s.working.recorded_reps),
        lower_body=s.lower_body,
        unclassified_exercises=s.unclassified_exercises,
        acquisition=s.acquisition,
        consistency=dict(
            evidence=p.consistency,
            eligible_weeks=len(p.consistency.eligible_weeks),
            confirmed_weeks=len(p.consistency.confirmed_weeks),
            confirmed_or_inferred_weeks=len(p.consistency.confirmed_or_inferred_weeks),
        ),
        comparisons={
            name: [_difference(d) for d in differences if d.later.fact.report_date in dates]
            for name, differences in (
                ("fixed_load", p.fixed_work_comparisons("load")),
                ("fixed_reps", p.fixed_work_comparisons("repetitions")),
                ("estimated_1rm", p.successive_estimates),
            )
        },
        comparison_exclusions=dict(
            Counter(
                reason for v in p.strength if v.fact.report_date in dates for reason in v.reasons
            )
        ),
    )


def _endurance_summary(p: PerformanceReport, w: Week) -> dict:
    dates = w.requested_dates
    return dict(
        sports=[_sport(sport) for sport in w.endurance.sports],
        acquisition_discrepancies=[
            dict(provider_date=day.activities.provider_date, reasons=day.discrepancies)
            for day in w.endurance.days
            if day.discrepancies
        ],
        comparisons=[
            dict(
                earlier=d.earlier.fact.workout_id,
                later=d.later.fact.workout_id,
                seconds=d.seconds,
                timing=d.later.review.task.timing,
            )
            for d in p.successive_runs
            if d.later.fact.provider_date in dates
        ],
        comparison_exclusions=dict(
            Counter(
                reason for v in p.running if v.fact.provider_date in dates for reason in v.reasons
            )
        ),
        references=[_reference(r) for r in p.running_references(w.monday)],
    )


def _recovery_summary(p: PerformanceReport, w: Week, focus: date) -> dict:
    return dict(
        series=[
            dict(
                metric=r.metric,
                median=r.median,
                minimum=r.minimum,
                maximum=r.maximum,
                unit=r.facts[0].unit,
                sample_dates=r.dates,
                n=r.sample_count,
            )
            for r in w.recovery.series
        ],
        hrv=[
            dict(
                metric=m,
                source_only_dates=[
                    c.day for c in w.recovery.cells if c.metric == m and c.status == "source_only"
                ],
            )
            for m in (DailyMetric.OVERNIGHT_HRV, DailyMetric.WEEKLY_HRV)
        ],
        cell_statuses={
            m: dict(Counter(c.status for c in w.recovery.cells if c.metric == m))
            for m in sorted({c.metric for c in w.recovery.cells})
        },
        references=[_recovery_ref(p.recovery_reference(focus, m)) for m in REFERENCE_METRICS],
    )


@dataclass(frozen=True)
class IntegratedReport:
    performance: PerformanceReport
    proximity: TrainingProximity
    version: str = "integrated-longitudinal-v1"

    def inspect_day(self, day: date) -> ReportDay:
        report = self.performance.weekly.daily_report
        if not report.period.start <= day < report.period.stop:
            raise KeyError(day)
        return report.days[(day - report.period.start).days]

    def inspect_workout(self, workout_id: UUID) -> dict:
        """Resolve a canonical ID only within this owner and selected sources."""
        p = self.performance
        for week in p.weekly.weeks:
            if week.strength and workout_id in week.strength.workouts:
                facts = [f for f in week.strength.facts if f.row.workout_id == workout_id]
                points = {
                    v.fact.row.set_id: v for v in p.strength if v.fact.row.workout_id == workout_id
                }
                detail = []
                for fact in facts:
                    point = points.get(fact.row.set_id)
                    detail.append(
                        dict(
                            fact=fact,
                            execution=fact.execution,
                            load_convention=fact.load_convention,
                            review=point.review if point else None,
                            comparison_exclusions=point.reasons if point else (),
                            estimated_1rm_kg=point.estimated_1rm_kg if point else None,
                            workout_best=point.workout_best if point else False,
                        )
                    )
                return dict(
                    domain="strength",
                    facts=detail,
                    acquisition=week.strength.acquisition,
                    tolerance=None,
                )
            if week.endurance:
                for day in week.endurance.days:
                    for f in day.facts:
                        if f.workout_id == workout_id:
                            point = next(
                                (v for v in p.running if v.fact.workout_id == workout_id), None
                            )
                            return dict(
                                domain="endurance",
                                fact=f,
                                pace_state=f.pace[0],
                                pace_s_per_km=f.pace[1],
                                review=point.review if point else None,
                                comparison_exclusions=point.reasons if point else (),
                                calendar_aligned=day.calendar_aligned
                                and f.provider_date == f.report_date,
                                acquisition_discrepancies=day.discrepancies,
                                acquisition=day.activities,
                                instructions=day.instructions,
                                tolerance=None,
                            )
        raise KeyError(workout_id)

    def inspect_recovery_reference(self, day: date, metric: DailyMetric) -> dict:
        ref = self.performance.recovery_reference(day, metric)
        return _recovery_ref(ref) | dict(
            target=ref.target,
            contributing=ref.facts,
            excluded=ref.excluded,
        )

    def inspect_running_reference(self, comparison_week: date, metric: str) -> dict:
        for ref in self.performance.running_references(comparison_week):
            if ref.metric == metric:
                return _reference(ref) | dict(
                    source=ref.source,
                    candidate_weeks=[
                        dict(
                            monday=w.monday,
                            observed=w.observed,
                            native_dates=[
                                dict(
                                    activity_coverage=d.activities,
                                    scan_started_at=d.scan_started_at,
                                    provider_zone=d.provider_zone,
                                    discrepancies=d.discrepancies,
                                )
                                for d in w.days
                            ],
                        )
                        for w in ref.weeks
                    ],
                )
        raise KeyError(metric)

    def inspect_pair(self, strength_workout_id: UUID, running_workout_id: UUID) -> dict:
        pair = next(
            (
                p
                for p in self.proximity.pairs
                if p.strength_workout_id == strength_workout_id
                and p.running_workout_id == running_workout_id
            ),
            None,
        )
        if pair is None:
            raise KeyError((strength_workout_id, running_workout_id))
        ids = set(pair.confirmed_sets + pair.inferred_sets)
        sets = [p for p in self.performance.strength if p.fact.row.set_id in ids]
        return dict(
            pair=pair,
            lower_body_working_sets=sets,
            running=self.inspect_workout(running_workout_id),
            tolerance=None,
        )

    def summary(self, focus_date: date | None = None) -> dict[str, Any]:
        """Summarize the week containing focus_date. Use that date for prior recovery windows."""
        p = self.performance
        weekly = p.weekly
        daily = weekly.daily_report
        focus = focus_date or (weekly.period.stop - DAY)
        self.inspect_day(focus)
        w = next(w for w in weekly.weeks if w.monday == monday(focus))
        dates = w.requested_dates
        pairs = [pair for pair in self.proximity.pairs if pair.running_date in dates]
        return dict(
            version=self.version,
            policies=(
                daily.contract_version,
                daily.policy_version,
                weekly.policy_version,
                p.policy_version,
            ),
            observation_state=daily.observation_state,
            period=weekly.period,
            owner_id=weekly.owner_id,
            reference_date=weekly.reference_date,
            focus_date=focus,
            weeks=[wk.monday for wk in weekly.weeks],
            week=w.monday,
            requested_dates=dates,
            closed=w.closed,
            fully_requested=w.fully_requested,
            sources=dict(
                hevy=daily.hevy_profile,
                endurance=daily.endurance_source,
                recovery=daily.recovery_source,
                weight=daily.weight_source,
                expenditure=daily.expenditure_source,
                intake="owner_day",
            ),
            source_zones=daily.source_zones,
            calendars=dict(
                strength="workout_start_report_zone",
                garmin="provider_local",
                proximity="aligned_report_dates",
            ),
            coverage=_coverage(w),
            strength=_strength_summary(p, w) if w.strength else None,
            endurance=_endurance_summary(p, w) if w.endurance else None,
            recovery=_recovery_summary(p, w, focus) if w.recovery else None,
            proximity=dict(
                pairs=pairs,
                excluded_runs=[e for e in self.proximity.excluded_runs if e.provider_date in dates],
                selected=w.strength is not None and w.endurance is not None,
            ),
            intake=_kcal(w.intake.calories)
            | dict(logging_completeness=w.intake.logging_completeness_counts),
            expenditure={k: _kcal(getattr(w.expenditure, k)) for k in ("total", "active", "basal")}
            if w.expenditure
            else None,
            weight=dict(
                daily_statuses=dict(Counter(cell.status for _, cell in w.weight.sample.daily)),
                series=[
                    dict(
                        key=r.key,
                        median_kg=r.median_kg,
                        dates=[d.day for d in r.dates],
                        measurements=r.observation_count,
                    )
                    for r in w.weight.series
                ],
                changes=[
                    dict(
                        series=c.later.key if c.later else None,
                        earlier_dates=[d.day for d in c.earlier.dates] if c.earlier else (),
                        later_dates=[d.day for d in c.later.dates] if c.later else (),
                        change_kg=c.change_kg,
                        reasons=c.reasons,
                    )
                    for c in w.weight.changes
                ],
            ),
        )

    def to_json(self, focus_date: date | None = None) -> str:
        return report_json(self.summary(focus_date))

    def render(self, focus_date: date | None = None) -> str:
        view = self.summary(focus_date)

        def show(value: object) -> str:
            if isinstance(value, Decimal):
                whole, _, fraction = format(value, "f").partition(".")
                return (whole + "." + fraction.rstrip("0")).rstrip(".")
            return "unavailable" if value is None else str(value)

        def quantity(cell: dict, unit: str, measurement: str) -> str:
            if cell["value"] is None:
                return f"{measurement} unavailable"
            qualifier = {"lower_bound": "at least ", "observed_only": "retained "}.get(
                cell["status"], ""
            )
            if unit == "sessions" and cell["value"] == 1:
                unit = "session"
            return f"{qualifier}{show(cell['value'])} {unit}"

        lines = [
            f"Week of {view['week']} · {len(view['requested_dates'])} requested dates · "
            f"{'closed' if view['closed'] else 'open'} at {view['reference_date']}"
        ]
        if s := view["strength"]:
            lines.append(
                f"Strength · {len(s['workouts'])} recorded workouts, "
                f"{s['confirmed_working_sets']} confirmed and "
                f"{s['inferred_working_sets']} inferred working sets"
            )
            comparisons = s["comparisons"]
            lines.append(
                f"Reviewed strength comparisons · {len(comparisons['fixed_load'])} fixed load, "
                f"{len(comparisons['fixed_reps'])} fixed reps, "
                f"{len(comparisons['estimated_1rm'])} estimated 1RM"
            )
            c = s["consistency"]
            n = c["eligible_weeks"]
            if n:
                lines.append(
                    f"Observed strength weeks · {c['confirmed_weeks']}/{n} confirmed, "
                    f"{c['confirmed_or_inferred_weeks']}/{n} confirmed or inferred"
                )
            else:
                lines.append("Observed strength weeks · no fully requested closed weeks")
        if e := view["endurance"]:
            for sport in e["sports"]:
                label = (sport["subtype"] or sport["sport"]).replace("_", " ").capitalize()
                lines.append(
                    f"{label} · {quantity(sport['sessions'], 'sessions', 'sessions')}, "
                    f"{quantity(sport['distance_m'], 'm', 'distance')}"
                )
            for comparison in e["comparisons"]:
                delta = comparison["seconds"].value
                lines.append(
                    f"Reviewed run · {comparison['timing'].removesuffix('_s')} time "
                    f"change {show(delta)} s"
                )
            ref = e["references"][0]
            excluded = [
                f"{w['monday']} {show(w['observed']['value'])} "
                f"({w['observed']['status'].replace('_', ' ')})"
                for w in ref["weeks"]
                if w["exclusions"] and w["observed"]
            ]
            lines.append(
                f"Sampled running sessions/week · median {show(ref['sampled_week_median'])} "
                f"from {len(ref['contributing_weeks'])}/4 preceding weeks. "
                "Habitual exposure unknown."
            )
            if excluded:
                lines.append("Excluded weeks, observed sessions · " + ", ".join(excluded))
        if view["proximity"]["selected"]:
            pairs = view["proximity"]["pairs"]
            lines.append(
                f"Aligned strength/run pairs · {len(pairs)}, including "
                f"{sum(p.evidence == 'tentative_inferred' for p in pairs)} tentative"
            )
        if r := view["recovery"]:
            for series in r["series"]:
                metric = series["metric"].replace("_", " ")
                lines.append(
                    f"{metric} observed · median {show(series['median'])} "
                    f"{series['unit']} on {series['n']} dates"
                )
            hrv = ", ".join(
                f"{v['metric'].replace('_', ' ')} {len(v['source_only_dates'])}" for v in r["hrv"]
            )
            lines.append(f"HRV source-only dates · {hrv}")
            for ref in r["references"]:
                value = (
                    "unavailable"
                    if ref["median"] is None
                    else (f"{show(ref['median'])} {ref['unit']}")
                )
                lines.append(
                    f"{ref['metric'].replace('_', ' ')} prior reference · {value} (n={ref['n']})"
                )
        intake = view["intake"]
        lines.append(
            f"Reported intake · {show(intake['subtotal_kcal'])} kcal "
            f"over {len(intake['eligible_dates'])} eligible dates"
        )
        if ex := view["expenditure"]:
            lines.append(
                f"Wearable total · {show(ex['total']['subtotal_kcal'])} kcal "
                f"(eligible dates {len(ex['total']['eligible_dates'])}/"
                f"{len(view['requested_dates'])})"
            )
        masses = [show(s["median_kg"]) for s in view["weight"]["series"]]
        lines.append("Weight median by series (kg) · " + (", ".join(masses) or "unavailable"))
        return "\n".join(lines)


def integrate(performance: PerformanceReport) -> IntegratedReport:
    return IntegratedReport(performance, training_proximity(performance))

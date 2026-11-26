"""Descriptive history windows on the selected D1D source calendars."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from fractions import Fraction

from fitness_intelligence.analytics.exposure import ActivityDay, ExposureValue, RecoveryCell
from fitness_intelligence.analytics.longitudinal import RecoveryObservation, daily_median
from fitness_intelligence.analytics.strength import DAY
from fitness_intelligence.analytics.weekly import WeeklyReport
from fitness_intelligence.domain.endurance import DailyMetric, Source


def known_context(label: str | None) -> bool:
    """Missing or explicitly unknown review dimensions cannot establish equivalence."""
    return bool(
        label
        and label.strip().casefold()
        not in {"", "unknown", "unreported", "unverified", "unspecified"}
    )


@dataclass(frozen=True)
class StrengthConsistency:
    source: Source
    eligible_weeks: tuple[date, ...]
    confirmed_weeks: tuple[date, ...]
    confirmed_or_inferred_weeks: tuple[date, ...]
    excluded: tuple[tuple[date, tuple[str, ...]], ...]
    acquisition: str = "daily_enumeration_unknown"

    @property
    def confirmed_fraction(self) -> Fraction | None:
        return (
            Fraction(len(self.confirmed_weeks), len(self.eligible_weeks))
            if self.eligible_weeks
            else None
        )

    @property
    def confirmed_or_inferred_fraction(self) -> Fraction | None:
        return (
            Fraction(len(self.confirmed_or_inferred_weeks), len(self.eligible_weeks))
            if self.eligible_weeks
            else None
        )


def _week_exclusions(full: bool, closed: bool) -> tuple[str, ...]:
    return tuple(
        reason
        for condition, reason in ((not full, "clipped_week"), (not closed, "open_week"))
        if condition
    )


def observed_consistency(report: WeeklyReport) -> StrengthConsistency | None:
    if report.daily_report.hevy_profile is None:
        return None
    eligible, confirmed, either, excluded = [], [], [], []
    for w in report.weeks:
        reasons = _week_exclusions(w.fully_requested, w.closed)
        if reasons:
            excluded.append((w.monday, reasons))
            continue
        eligible.append(w.monday)
        if w.strength.confirmed_dates:
            confirmed.append(w.monday)
        if w.strength.confirmed_dates or w.strength.inferred_only_dates:
            either.append(w.monday)
    return StrengthConsistency(
        report.weeks[0].strength.source,
        tuple(eligible),
        tuple(confirmed),
        tuple(either),
        tuple(excluded),
    )


@dataclass(frozen=True)
class RunningWeekSample:
    monday: date
    days: tuple[ActivityDay, ...]
    observed: ExposureValue | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RunningReference:
    comparison_week: date
    source: Source
    metric: str
    weeks: tuple[RunningWeekSample, ...]

    @property
    def contributing(self) -> tuple[RunningWeekSample, ...]:
        return tuple(w for w in self.weeks if not w.reasons)

    @property
    def reasons(self) -> tuple[str, ...]:
        return ("fewer_than_two_eligible_weeks",) if len(self.contributing) < 2 else ()

    @property
    def median(self) -> Decimal | None:
        if self.reasons:
            return None
        return daily_median(tuple(Decimal(w.observed.value) for w in self.contributing))


def running_references(report: WeeklyReport, comparison_week: date) -> tuple[RunningReference, ...]:
    weeks = {w.monday: w for w in report.weeks}
    if comparison_week not in weeks:
        raise ValueError("comparison_week must be a requested Monday week")
    source = report.daily_report.endurance_source
    if source is None:
        return ()
    metrics = ("sessions", "distance_m", "duration_s", "moving_s", "elapsed_s")
    samples = {metric: [] for metric in metrics}
    for offset in (4, 3, 2, 1):
        start = comparison_week - 7 * offset * DAY
        week = weeks.get(start)
        reasons = (
            _week_exclusions(week.fully_requested, week.closed) if week else ("outside_request",)
        )
        run = next(r for r in week.endurance.sports if r.sport == "running") if week else None
        for metric in metrics:
            cell = getattr(run, metric) if run else None
            gaps = reasons
            if cell is not None and cell.status != "complete_empty":
                gaps += (cell.status, *run.reasons)
                if cell.missing_workouts:
                    gaps += ("missing_session_measurements",)
            samples[metric].append(
                RunningWeekSample(start, week.endurance.days if week else (), cell, gaps)
            )
    return tuple(RunningReference(comparison_week, source, m, tuple(samples[m])) for m in metrics)


REFERENCE_METRICS = (DailyMetric.SLEEP, DailyMetric.RESTING_HR)


@dataclass(frozen=True)
class RecoveryRegime:
    """Reviewed device/protocol continuity for one source, metric and half-open interval."""

    source: Source
    metric: DailyMetric
    start: date
    stop: date
    regime: str
    evidence: str


def validate_regimes(
    report: WeeklyReport, regimes: tuple[RecoveryRegime, ...]
) -> tuple[RecoveryRegime, ...]:
    ordered = sorted(regimes, key=lambda r: (r.metric, r.start))
    for i, r in enumerate(ordered):
        if (
            r.source != report.daily_report.recovery_source
            or r.metric not in REFERENCE_METRICS
            or r.stop <= r.start
            or not known_context(r.regime)
            or not known_context(r.evidence)
        ):
            raise ValueError("invalid recovery regime for the selected source")
        if i and ordered[i - 1].metric == r.metric and ordered[i - 1].stop > r.start:
            raise ValueError("overlapping recovery regimes")
    return tuple(ordered)


@dataclass(frozen=True)
class ExcludedRecoveryDate:
    cell: RecoveryCell
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RecoveryReference:
    day: date
    metric: DailyMetric
    source: Source
    window_start: date
    target: RecoveryCell
    regime: RecoveryRegime | None
    facts: tuple[RecoveryObservation, ...]
    excluded: tuple[ExcludedRecoveryDate, ...]
    reasons: tuple[str, ...]

    @property
    def dates(self) -> tuple[date, ...]:
        return tuple(f.provider_date for f in self.facts)

    @property
    def missing_dates(self) -> tuple[date, ...]:
        return tuple(e.cell.day for e in self.excluded if e.cell.fact is None)

    @property
    def n(self) -> int:
        return len(self.facts)

    @property
    def median(self) -> Decimal | None:
        return None if self.reasons else daily_median(tuple(f.value for f in self.facts))

    @property
    def minimum(self) -> Decimal | None:
        return None if self.reasons else min(f.value for f in self.facts)

    @property
    def maximum(self) -> Decimal | None:
        return None if self.reasons else max(f.value for f in self.facts)


def _signature(f: RecoveryObservation) -> tuple | None:
    if not (f.source_field and f.mapping_version):
        return None
    return (
        f.identity.source,
        f.component,
        f.unit,
        f.method,
        f.source_field,
        f.mapping_version,
        f.upstream_writer,
    )


def recovery_reference(
    report: WeeklyReport, day: date, metric: DailyMetric, regimes: tuple[RecoveryRegime, ...]
) -> RecoveryReference:
    if metric not in REFERENCE_METRICS or not report.period.start <= day < report.period.stop:
        raise ValueError("reference requires sleep duration or resting HR and a requested date")
    source = report.daily_report.recovery_source
    if source is None:
        raise ValueError("no recovery account selected")
    start = max(report.period.start, day - 28 * DAY)
    regime = next(
        (
            r
            for r in validate_regimes(report, regimes)
            if r.metric == metric and r.start <= day < r.stop
        ),
        None,
    )
    first = (start - report.period.start).days
    last = (day - report.period.start).days
    cells = tuple(
        next(c for c in d.recovery.cells if c.metric == metric)
        for d in report.daily_report.days[first : last + 1]
    )
    target = cells[-1]
    # D can identify a provenance break. Only earlier values enter the sample.
    signature = _signature(target.fact) if target.fact is not None else None
    broken = target.fact is not None and signature is None
    facts, excluded = [], []
    for cell in reversed(cells[:-1]):
        f = cell.fact
        if regime is None:
            reasons = ("unreviewed_measurement_regime",)
        elif cell.day < regime.start:
            reasons = ("outside_measurement_regime",)
        else:
            if f is not None:
                sig = _signature(f)
                if sig is None or (signature is not None and sig != signature):
                    broken = True
                signature = sig
            reasons = ("measurement_regime_break",) if broken else ()
        if cell.status != "eligible":
            reasons += (cell.status, *cell.reasons)
        if reasons:
            excluded.append(ExcludedRecoveryDate(cell, reasons))
        else:
            facts.append(f)
    facts.reverse()
    reasons = []
    if regime is None:
        reasons.append("unreviewed_measurement_regime")
    if len(facts) < 14:
        reasons.append("fewer_than_14_dates")
    if not facts or (facts[-1].provider_date - facts[0].provider_date).days < 14:
        reasons.append("span_under_14_days")
    if reasons and broken:
        reasons.append("measurement_regime_break")
    return RecoveryReference(
        day,
        metric,
        source,
        start,
        target,
        regime,
        tuple(facts),
        tuple(reversed(excluded)),
        tuple(reasons),
    )

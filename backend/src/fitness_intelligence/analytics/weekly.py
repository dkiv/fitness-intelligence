"""Pure Monday-week summaries of the current accepted daily longitudinal projection."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext
from itertools import groupby
from uuid import UUID

from fitness_intelligence.analytics.exposure import (
    EnduranceExposure,
    RecoveryExposure,
    StrengthExposure,
)
from fitness_intelligence.analytics.longitudinal import (
    Coverage,
    LongitudinalReport,
    Metric,
    ObservationId,
    ReportDay,
    WeighIn,
    daily_median,
)
from fitness_intelligence.analytics.strength import DAY, Period, monday
from fitness_intelligence.analytics.weight import SeriesKey, WeightContinuity, partition_weigh_ins
from fitness_intelligence.domain.endurance import Source


@dataclass(frozen=True)
class WeekCoverage:
    source: Source
    days: tuple[Coverage, ...]

    @property
    def acquisition_counts(self) -> tuple[tuple[str, int], ...]:
        return tuple(sorted(Counter(d.status for d in self.days).items()))

    @property
    def unresolved_dates(self) -> tuple[date, ...]:
        return tuple(d.provider_date for d in self.days if d.issues)


@dataclass(frozen=True)
class Sample:
    """The input cells retain exclusions, statuses and account-scoped support."""

    daily: tuple[tuple[date, Metric], ...]

    @property
    def eligible_dates(self) -> tuple[date, ...]:
        return tuple(day for day, metric in self.daily if metric.value is not None)

    @property
    def supporting(self) -> tuple[ObservationId, ...]:
        return tuple(i for _, metric in self.daily for i in metric.supporting)

    @property
    def retained_count(self) -> int:
        return sum(metric.retained_count for _, metric in self.daily)

    @property
    def eligible_observation_count(self) -> int:
        return len(self.supporting)

    @property
    def eligible_date_count(self) -> int:
        return len(self.eligible_dates)

    @property
    def requested_date_count(self) -> int:
        return len(self.daily)

    def dates_with_status(self, status: str) -> tuple[date, ...]:
        return tuple(day for day, metric in self.daily if metric.status == status)

    @property
    def report_calendar_aligned(self) -> bool | None:
        dates = [day == m.report_date for day, m in self.daily if m.value is not None]
        return all(dates) if dates else None


@dataclass(frozen=True)
class WeeklyCalories:
    sample: Sample
    method: str
    observed_subtotal_kcal: Decimal | None
    mean_per_eligible_date_kcal: Decimal | None
    subtotal_status: str


@dataclass(frozen=True)
class WeeklyIntake:
    calories: WeeklyCalories
    logging_completeness_counts: tuple[tuple[str, int], ...]
    coverage: tuple[WeekCoverage, ...]

    @property
    def explicit_zero_dates(self) -> tuple[date, ...]:
        return self.calories.sample.dates_with_status("explicit_zero")


@dataclass(frozen=True)
class WeeklyExpenditure:
    total: WeeklyCalories
    active: WeeklyCalories
    basal: WeeklyCalories
    coverage: WeekCoverage


@dataclass(frozen=True)
class WeightDate:
    day: date
    median_kg: Decimal
    measurements: tuple[WeighIn, ...]


@dataclass(frozen=True)
class WeightSeries:
    key: SeriesKey
    dates: tuple[WeightDate, ...]
    median_kg: Decimal

    @property
    def observation_count(self) -> int:
        return sum(len(d.measurements) for d in self.dates)


@dataclass(frozen=True)
class WeightChange:
    earlier: WeightSeries | None
    later: WeightSeries | None
    change_kg: Decimal | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class WeeklyWeight:
    sample: Sample
    coverage: WeekCoverage
    series: tuple[WeightSeries, ...]
    changes: tuple[WeightChange, ...]


@dataclass(frozen=True)
class Week:
    monday: date
    requested_dates: tuple[date, ...]
    closed: bool
    intake: WeeklyIntake
    expenditure: WeeklyExpenditure | None
    weight: WeeklyWeight
    strength: StrengthExposure | None = None
    endurance: EnduranceExposure | None = None
    recovery: RecoveryExposure | None = None

    @property
    def fully_requested(self) -> bool:
        return len(self.requested_dates) == 7


@dataclass(frozen=True)
class WeeklyReport:
    owner_id: UUID
    period: Period
    reference_date: date
    daily_report: LongitudinalReport
    weeks: tuple[Week, ...]
    weight_continuity: WeightContinuity | None
    policy_version: str = "nutrition-weight-weekly-v1"


def _coverage(rows: Iterable[Coverage]) -> tuple[WeekCoverage, ...]:
    by_source: dict[Source, list[Coverage]] = defaultdict(list)
    for row in rows:
        by_source[row.source].append(row)
    return tuple(
        WeekCoverage(source, tuple(by_source[source]))
        for source in sorted(by_source, key=lambda s: (s.provider, s.source_account_id))
    )


def _calories(sample: Sample, method: str, zones: Mapping[UUID, str]) -> WeeklyCalories:
    values = [m.value for _, m in sample.daily if m.value is not None]
    accounts = {i.source.source_account_id for i in sample.supporting}
    calendars = {zones.get(i) for i in accounts}
    if not values:
        return WeeklyCalories(sample, method, None, None, "no_eligible_dates")
    if len(accounts) > 1 and (None in calendars or len(calendars) != 1):
        return WeeklyCalories(sample, method, None, None, "unverified_common_calendar")
    # The exact numerator and date count also describe a repeating decimal mean.
    with localcontext(Context(prec=38, rounding=ROUND_HALF_EVEN)):
        subtotal = sum(values, start=Decimal(0))
        mean = subtotal / len(values)
    status = "all_requested_dates" if len(values) == len(sample.daily) else "incomplete_subtotal"
    return WeeklyCalories(sample, method, subtotal, mean, status)


def _weekly_expenditure(
    days: Sequence[ReportDay], source: Source | None, zones: Mapping[UUID, str]
) -> WeeklyExpenditure | None:
    if source is None:
        return None
    total = []
    active = []
    basal = []
    coverage = []
    for day in days:
        energy = day.expenditure
        if energy is None or energy.coverage.source != source:
            raise ValueError("missing or mismatched expenditure source on requested date")
        total.append((day.provider_date, energy.total))
        active.append((day.provider_date, energy.active))
        basal.append((day.provider_date, energy.basal))
        coverage.append(energy.coverage)
    return WeeklyExpenditure(
        _calories(Sample(tuple(total)), "wearable_estimate", zones),
        _calories(Sample(tuple(active)), "wearable_estimate", zones),
        _calories(Sample(tuple(basal)), "wearable_estimate", zones),
        WeekCoverage(source, tuple(coverage)),
    )


def _weight_series(
    days: Sequence[ReportDay], continuity: WeightContinuity | None
) -> tuple[WeightSeries, ...]:
    groups: dict[SeriesKey, list[WeightDate]] = defaultdict(list)
    for d in days:
        by_key = partition_weigh_ins(d.weight.measurements, continuity)
        for key, readings in by_key.items():
            # A continuity review may join partitions that the daily report kept separate.
            value = (
                d.weight.metric.value
                if len(by_key) == 1 and d.weight.metric.value is not None
                else daily_median(tuple(w.value for w in readings))
            )
            assert value is not None
            groups[key].append(WeightDate(d.provider_date, value, tuple(readings)))
    series = []
    for key, dates in groups.items():
        median = daily_median(tuple(d.median_kg for d in dates))
        assert median is not None
        series.append(WeightSeries(key, tuple(dates), median))
    # Chronological first appearance, then stable observation identity across simultaneous regimes.
    return tuple(
        sorted(series, key=lambda s: (s.dates[0].day, s.dates[0].measurements[0].identity.id))
    )


def _change(
    previous: Week | None, start: date, full: bool, closed: bool, later: WeightSeries | None
) -> WeightChange:
    reasons = []
    earlier = None
    if previous is None or previous.monday + 7 * DAY != start:
        reasons.append("no_adjacent_week")
    else:
        if not previous.fully_requested:
            reasons.append("earlier_week_clipped")
        if not previous.closed:
            reasons.append("earlier_week_open")
        if later is not None:
            earlier = next((s for s in previous.weight.series if s.key == later.key), None)
            if earlier is None:
                reasons.append("no_comparable_earlier_series")
    if not full:
        reasons.append("later_week_clipped")
    if not closed:
        reasons.append("later_week_open")
    if later is None:
        reasons.append("no_eligible_weight")
    for label, series in (("earlier", earlier), ("later", later)):
        if series is not None:
            if len(series.dates) < 3:
                reasons.append(f"{label}_fewer_than_three_dates")
            if (series.dates[-1].day - series.dates[0].day).days < 3:
                reasons.append(f"{label}_span_under_three_days")
    delta = None
    if not reasons:
        assert earlier is not None and later is not None
        with localcontext(Context(prec=38)):
            delta = later.median_kg - earlier.median_kg
    return WeightChange(earlier, later, delta, tuple(reasons))


def aggregate_weeks(
    report: LongitudinalReport,
    *,
    reference_date: date,
    weight_continuity: WeightContinuity | None = None,
) -> WeeklyReport:
    """reference_date is the first native date not certified closed across the source calendars."""
    if type(reference_date) is not date:
        raise ValueError("supply the reference calendar date explicitly")
    if weight_continuity and weight_continuity.source != report.weight_source:
        raise ValueError("weight continuity must describe the selected owner/account")
    ordered = tuple(sorted(report.days, key=lambda d: d.provider_date))
    if len(ordered) != (report.period.stop - report.period.start).days or any(
        d.provider_date != report.period.start + i * DAY for i, d in enumerate(ordered)
    ):
        raise ValueError("a complete, unique requested date spine is required")
    zones = dict(report.source_zones)
    weeks: list[Week] = []
    for start, group in groupby(ordered, key=lambda d: monday(d.provider_date)):
        days = tuple(group)
        dates = tuple(d.provider_date for d in days)
        closed = start + 7 * DAY <= reference_date
        intake = WeeklyIntake(
            _calories(
                Sample(tuple((d.provider_date, d.intake.metric) for d in days)), "reported", zones
            ),
            tuple(
                sorted(
                    Counter(
                        d.intake.logging_completeness
                        for d in days
                        if d.intake.metric.value is not None
                    ).items()
                )
            ),
            _coverage(c for d in days for c in d.intake.coverage),
        )
        expenditure = _weekly_expenditure(days, report.expenditure_source, zones)
        series = _weight_series(days, weight_continuity)
        changes = tuple(
            _change(weeks[-1] if weeks else None, start, len(dates) == 7, closed, s)
            for s in series or (None,)
        )
        weight = WeeklyWeight(
            Sample(tuple((d.provider_date, d.weight.metric) for d in days)),
            WeekCoverage(report.weight_source, tuple(d.weight.coverage for d in days)),
            series,
            changes,
        )
        strength = None
        if days[0].strength is not None:
            strength = replace(
                days[0].strength,
                dates=dates,
                facts=tuple(f for d in days for f in d.strength.facts),
            )
        endurance = None
        if days[0].endurance is not None:
            endurance = EnduranceExposure(
                tuple(native for d in days for native in d.endurance.days), reference_date
            )
        recovery = None
        if days[0].recovery is not None:
            recovery = RecoveryExposure(
                tuple(c for d in days for c in d.recovery.coverage),
                tuple(c for d in days for c in d.recovery.cells),
            )
        weeks.append(
            Week(start, dates, closed, intake, expenditure, weight, strength, endurance, recovery)
        )
    return WeeklyReport(
        report.owner_id,
        report.period,
        reference_date,
        replace(report, days=ordered),
        tuple(weeks),
        weight_continuity,
    )

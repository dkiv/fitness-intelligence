"""Recorded training exposure. All summaries retain their normalized source facts."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import polars as pl

from fitness_intelligence.analytics.longitudinal import (
    Coverage,
    Issue,
    RecoveryObservation,
    daily_median,
)
from fitness_intelligence.analytics.strength import CATEGORIES, StrengthFact, measured_sum
from fitness_intelligence.domain.endurance import DailyMetric, PaceState, Source, running_pace


@dataclass(frozen=True)
class WorkingSets:
    confirmed: tuple[UUID, ...]
    inferred: tuple[UUID, ...]
    recorded_reps: tuple[tuple[UUID, int], ...]

    @property
    def repetitions(self) -> int | None:
        return sum(reps for _, reps in self.recorded_reps) if self.recorded_reps else None


def _working_sets(facts: tuple[StrengthFact, ...]) -> WorkingSets:
    working = [
        f
        for f in facts
        if CATEGORIES.get(f.row.kind) == "working" and f.execution in ("confirmed", "inferred")
    ]
    return WorkingSets(
        tuple(f.row.set_id for f in working if f.execution == "confirmed"),
        tuple(f.row.set_id for f in working if f.execution == "inferred"),
        tuple((f.row.set_id, f.row.repetitions) for f in working if f.row.repetitions is not None),
    )


@dataclass(frozen=True)
class StrengthExposure:
    source: Source
    account_status: str
    dates: tuple[date, ...]
    facts: tuple[StrengthFact, ...]
    calendar: str = "report_zone_workout_start"
    acquisition: str = "daily_enumeration_unknown"

    @property
    def workouts(self) -> tuple[UUID, ...]:
        return tuple(dict.fromkeys(f.row.workout_id for f in self.facts))

    @property
    def workout_dates(self) -> tuple[date, ...]:
        return tuple(sorted({f.report_date for f in self.facts}))

    def _working_workouts(self, evidence: str) -> tuple[UUID, ...]:
        return tuple(
            dict.fromkeys(
                f.row.workout_id
                for f in self.facts
                if f.execution == evidence and CATEGORIES.get(f.row.kind) == "working"
            )
        )

    @property
    def confirmed_workouts(self) -> tuple[UUID, ...]:
        return self._working_workouts("confirmed")

    @property
    def inferred_only_workouts(self) -> tuple[UUID, ...]:
        confirmed = set(self.confirmed_workouts)
        return tuple(w for w in self._working_workouts("inferred") if w not in confirmed)

    @property
    def confirmed_dates(self) -> tuple[date, ...]:
        ids = set(self.confirmed_workouts)
        return tuple(sorted({f.report_date for f in self.facts if f.row.workout_id in ids}))

    @property
    def inferred_only_dates(self) -> tuple[date, ...]:
        ids = set(self.inferred_only_workouts)
        return tuple(
            sorted(
                {f.report_date for f in self.facts if f.row.workout_id in ids}
                - set(self.confirmed_dates)
            )
        )

    @property
    def working(self) -> WorkingSets:
        return _working_sets(self.facts)

    @property
    def lower_body(self) -> WorkingSets:
        return _working_sets(tuple(f for f in self.facts if f.lower_body is True))

    @property
    def unclassified_exercises(self) -> tuple[UUID, ...]:
        return tuple(
            dict.fromkeys(
                f.row.exercise_id for f in self.facts if f.row.exercise_id and f.lower_body is None
            )
        )

    @property
    def by_movement(self) -> tuple[tuple[str, WorkingSets], ...]:
        groups: dict[str, list[StrengthFact]] = defaultdict(list)
        for f in self.facts:
            if f.movement is not None:
                groups[f.movement].append(f)
        return tuple((key, _working_sets(tuple(groups[key]))) for key in sorted(groups))

    @property
    def warmups(self) -> tuple[UUID, ...]:
        return tuple(
            f.row.set_id
            for f in self.facts
            if f.row.set_id and f.row.kind == "warmup" and f.execution != "unsupported"
        )

    @property
    def unknown_kind(self) -> tuple[UUID, ...]:
        return tuple(
            f.row.set_id
            for f in self.facts
            if f.row.set_id and f.row.kind not in CATEGORIES and f.execution != "unsupported"
        )

    @property
    def unsupported_sets(self) -> tuple[UUID, ...]:
        return tuple(f.row.set_id for f in self.facts if f.execution == "unsupported")


@dataclass(frozen=True)
class FieldProvenance:
    field: str
    source_field: str | None
    retrieved_at: str | None
    source_updated_at: str | None


@dataclass(frozen=True)
class Outing:
    source: Source
    workout_id: UUID
    reference_id: UUID
    external_id: str
    started_at: datetime
    provider_date: date
    report_date: date
    sport: str
    subtype: str | None
    distance_m: Decimal | None
    duration_s: Decimal | None
    moving_s: Decimal | None
    elapsed_s: Decimal | None
    average_speed_mps: Decimal | None
    retrieved_at: datetime
    source_updated_at: datetime | None
    mapping_version: str | None
    fields: tuple[FieldProvenance, ...]
    split_positions: tuple[int, ...] | None
    instruction_positions: tuple[tuple[int, int], ...] | None
    activity_issues: tuple[Issue, ...]
    instruction_issues: tuple[Issue, ...]

    @property
    def split_summary_rows(self) -> int | None:
        return len(self.split_positions) if self.split_positions is not None else None

    @property
    def instruction_rows(self) -> int | None:
        return len(self.instruction_positions) if self.instruction_positions is not None else None

    @property
    def pace(self) -> tuple[PaceState, Decimal | None]:
        return running_pace(self.sport, self.distance_m, self.average_speed_mps)

    @property
    def classification(self) -> tuple[str, str | None]:
        return (self.sport, self.subtype if self.sport == "other" else None)


@dataclass(frozen=True)
class ActivityDay:
    activities: Coverage
    instructions: Coverage
    facts: tuple[Outing, ...]
    calendar_aligned: bool

    @property
    def discrepancies(self) -> tuple[str, ...]:
        c = self.activities
        if c.status == "empty" and self.facts:
            return ("retained_after_empty",)
        if c.status in ("observed", "empty") and c.last_success_count != len(self.facts):
            return ("enumerated_count_mismatch",)
        if c.status == "observed" and not self.facts:
            return ("observed_without_retained_activity",)
        return ()

    @property
    def verified_empty(self) -> bool:
        return self.activities.status == "empty" and not (
            self.facts or self.activities.issues or self.discrepancies
        )


@dataclass(frozen=True)
class ExposureValue:
    value: Decimal | int | None
    status: str
    supporting_workouts: tuple[UUID, ...]
    missing_workouts: tuple[UUID, ...] = ()

    @property
    def eligible_count(self) -> int:
        return len(self.supporting_workouts)


@dataclass(frozen=True)
class SportExposure:
    sport: str
    subtype: str | None
    dates: tuple[date, ...]
    sessions: ExposureValue
    distance_m: ExposureValue
    duration_s: ExposureValue
    moving_s: ExposureValue
    elapsed_s: ExposureValue
    longest_observed: Outing | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class EnduranceExposure:
    days: tuple[ActivityDay, ...]
    reference_date: date | None = None
    calendar: str = "provider_local"

    @property
    def sports(self) -> tuple[SportExposure, ...]:
        groups: dict[tuple[str, str | None], list[Outing]] = defaultdict(list)
        groups["running", None] = []
        reasons = set()
        for d in self.days:
            c = d.activities
            reasons.update(d.discrepancies)
            if c.status == "observed":
                reasons.add("enumerated_identities_not_retained")
            elif c.status != "empty":
                reasons.add(c.status)
            if c.issues:
                reasons.add("open_activity_issue")
            for f in d.facts:
                group = groups[f.classification]
                if f.subtype is None and f.sport == "other":
                    reasons.add("unknown_sport")
                if not f.activity_issues:
                    group.append(f)
        empty = all(d.verified_empty for d in self.days)
        closed = self.reference_date is not None and all(
            d.activities.provider_date < self.reference_date for d in self.days
        )
        observed_status = (
            "observed_only" if any(d.discrepancies for d in self.days) else "lower_bound"
        )

        def value(
            amount: Decimal | int | None, ids: tuple[UUID, ...], missing: tuple[UUID, ...] = ()
        ) -> ExposureValue:
            if empty:
                return ExposureValue(0, "complete_empty" if closed else "empty_at_retrieval", ())
            return ExposureValue(amount, observed_status if ids else "unknown", ids, missing)

        result = []
        for (sport, subtype), rows in sorted(
            groups.items(), key=lambda kv: (kv[0][0], kv[0][1] or "")
        ):
            ids = tuple(f.workout_id for f in rows)

            fields = ("distance_m", "duration_s", "moving_s", "elapsed_s")
            measurements = pl.DataFrame(
                {field: [getattr(f, field) for f in rows] for field in fields},
                schema={field: pl.Decimal(38, 9) for field in fields},
            )
            totals = measurements.select(measured_sum(field) for field in fields).row(0, named=True)

            def subtotal(field: str) -> ExposureValue:
                return value(
                    totals[field],
                    tuple(f.workout_id for f in rows if getattr(f, field) is not None),
                    tuple(f.workout_id for f in rows if getattr(f, field) is None),
                )

            longest = (
                min(
                    (f for f in rows if f.distance_m is not None),
                    key=lambda f: (f.distance_m.copy_negate(), f.started_at, f.workout_id),
                    default=None,
                )
                if sport == "running"
                else None
            )
            result.append(
                SportExposure(
                    sport,
                    subtype,
                    tuple(sorted({f.provider_date for f in rows})),
                    value(len(ids) if ids else None, ids),
                    subtotal("distance_m"),
                    subtotal("duration_s"),
                    subtotal("moving_s"),
                    subtotal("elapsed_s"),
                    longest,
                    tuple(sorted(reasons)),
                )
            )
        return tuple(result)


RECOVERY_CATEGORIES = {
    DailyMetric.SLEEP: "sleep",
    DailyMetric.LIGHT: "sleep",
    DailyMetric.DEEP: "sleep",
    DailyMetric.REM: "sleep",
    DailyMetric.AWAKE: "sleep",
    DailyMetric.RESTING_HR: "resting_hr",
    DailyMetric.OVERNIGHT_HRV: "hrv",
    DailyMetric.WEEKLY_HRV: "hrv",
}


@dataclass(frozen=True)
class RecoveryCell:
    day: date
    metric: DailyMetric
    fact: RecoveryObservation | None
    status: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RecoverySeries:
    metric: DailyMetric
    facts: tuple[RecoveryObservation, ...]
    median: Decimal
    minimum: Decimal
    maximum: Decimal

    @property
    def dates(self) -> tuple[date, ...]:
        return tuple(f.provider_date for f in self.facts)

    @property
    def sample_count(self) -> int:
        return len(self.facts)


@dataclass(frozen=True)
class RecoveryExposure:
    coverage: tuple[Coverage, ...]
    cells: tuple[RecoveryCell, ...]
    calendar: str = "provider_local"

    @property
    def series(self) -> tuple[RecoverySeries, ...]:
        groups: dict[tuple, list[RecoveryObservation]] = defaultdict(list)
        for cell in self.cells:
            f = cell.fact
            if cell.status == "eligible" and f is not None:
                groups[cell.metric, f.unit, f.method, f.source_field, f.mapping_version].append(f)
        result = []
        for key, facts in sorted(groups.items()):
            values = tuple(f.value for f in facts)
            median = daily_median(values)
            assert median is not None
            result.append(RecoverySeries(key[0], tuple(facts), median, min(values), max(values)))
        return tuple(result)

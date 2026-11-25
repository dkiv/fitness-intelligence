"""Normalized snapshots for endurance and recovery. All instants are UTC."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from enum import StrEnum
from uuid import UUID


@dataclass(frozen=True)
class Source:
    owner_id: UUID
    provider: str
    source_account_id: UUID


@dataclass(frozen=True)
class SplitSummary:
    kind: str
    count: int | None
    distance_m: Decimal | None
    duration_s: Decimal | None
    average_speed_mps: Decimal | None


@dataclass(frozen=True)
class PerformedStep:
    workout_index: int
    step_index: int
    intensity: str | None
    duration_type: str | None
    duration_value: Decimal | None
    duration_unit: str | None
    target_type: str | None
    target_zone: int | None
    target_low: Decimal | None
    target_high: Decimal | None
    target_unit: str | None
    repeat_count: int | None


class PaceState(StrEnum):
    DERIVED = "derived"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class Activity:
    source: Source
    external_id: str
    started_at: datetime
    local_date: date
    sport: str
    subtype: str | None
    duration_s: Decimal | None
    elapsed_s: Decimal | None
    moving_s: Decimal | None
    distance_m: Decimal | None
    average_speed_mps: Decimal | None
    average_hr_bpm: Decimal | None
    max_hr_bpm: Decimal | None
    elevation_gain_m: Decimal | None
    elevation_loss_m: Decimal | None
    splits: tuple[SplitSummary, ...] | None
    steps: tuple[PerformedStep, ...] | None
    measurement_sources: tuple[tuple[str, str], ...]
    start_resolution_us: int = 1_000_000

    def running_pace(self) -> tuple[PaceState, Decimal | None]:
        """Seconds/km from reported average m/s, rounded half-even to milliseconds."""
        for value in (self.distance_m, self.average_speed_mps):
            if value is not None and (not value.is_finite() or value < 0):
                raise ValueError("invalid pace input")
        if self.sport != "running" or self.distance_m == 0 or self.average_speed_mps == 0:
            return PaceState.NOT_APPLICABLE, None
        if self.average_speed_mps is None:
            return PaceState.MISSING, None
        pace = Decimal(1000) / self.average_speed_mps
        return PaceState.DERIVED, pace.quantize(Decimal(".001"), rounding=ROUND_HALF_EVEN)


class DailyMetric(StrEnum):
    OVERNIGHT_HRV = "overnight_hrv"
    WEEKLY_HRV = "seven_day_hrv"
    RESTING_HR = "resting_hr"
    SLEEP = "sleep_duration"
    LIGHT = "light_sleep"
    DEEP = "deep_sleep"
    REM = "rem_sleep"
    AWAKE = "awake_during_sleep"
    TOTAL_ENERGY = "total_expenditure"
    ACTIVE_ENERGY = "active_expenditure"
    BASAL_ENERGY = "basal_expenditure"


@dataclass(frozen=True)
class DailyObservation:
    source: Source
    local_date: date
    metric: DailyMetric
    value: Decimal
    unit: str
    method: str
    window_start: datetime | None
    window_end: datetime | None
    source_field: str | None = None

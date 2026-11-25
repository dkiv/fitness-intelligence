"""Pure projection of Personal API v1 DTOs. No enrollment, persistence or transport."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from uuid import UUID

from fitness_intelligence.db.models import SourceAccount
from fitness_intelligence.domain.endurance import (
    Activity,
    DailyMetric,
    DailyObservation,
    PerformedStep,
    Source,
    SplitSummary,
)

type Row = Mapping[str, object]


class MappingError(ValueError):
    """Fixed diagnostic, without source values or identifying information."""


def integer(value: object, *, minimum: int = 0, bits: int = 32) -> int:
    if type(value) is not int or not minimum <= value < 2 ** (bits - 1):
        raise MappingError("invalid integer")
    return value


@dataclass(frozen=True, repr=False)
class GarminBinding:
    """Internal expected identity; construct from a previously verified active account."""

    source: Source
    profile_id: int

    def __post_init__(self) -> None:
        if self.source.provider != "garmin":
            raise MappingError("wrong provider")
        integer(self.profile_id, minimum=1, bits=64)

    @classmethod
    def from_account(cls, *, owner_id: UUID, account: SourceAccount) -> GarminBinding:
        identity = account.provider_account_id
        if (
            account.user_id != owner_id
            or account.provider != "garmin"
            or account.status != "active"
            or not isinstance(account.id, UUID)
            or not isinstance(identity, str)
            or not re.fullmatch(r"[1-9][0-9]{0,18}", identity)
        ):
            raise MappingError("invalid source account")
        return cls(Source(owner_id, account.provider, account.id), int(identity))

    def check(self, row: Row, key: str) -> None:
        if integer(row.get(key), minimum=1, bits=64) != self.profile_id:
            raise MappingError("account mismatch")


def obj(value: object) -> Row:
    if not isinstance(value, Mapping):
        raise MappingError("invalid object")
    return value


def rows(value: object) -> tuple[Row, ...]:
    if not isinstance(value, list):
        raise MappingError("invalid array")
    return tuple(obj(item) for item in value)


def label(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise MappingError("invalid category")
    return value


def source_number(value: object) -> Decimal:
    if type(value) not in (int, float, Decimal):
        raise MappingError("invalid measurement")
    number = Decimal(str(value)) if isinstance(value, float) else Decimal(value)
    if not number.is_finite():
        raise MappingError("invalid measurement")
    return number


def quantity(value: object) -> Decimal | None:
    if value is None:
        return None
    number = source_number(value)
    if number < 0 or number >= 10**13:
        raise MappingError("measurement outside supported range")
    with localcontext() as ctx:
        ctx.prec = 24
        rounded = number.quantize(Decimal(".000000001"), rounding=ROUND_HALF_EVEN)
    if (number and not rounded) or rounded >= 10**13:
        raise MappingError("measurement outside storage precision")
    return rounded


def stamp(value: object, pattern: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(pattern, value, flags=re.ASCII):
        raise MappingError("invalid timestamp")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise MappingError("invalid timestamp") from None


DAY = r"\d{4}-\d{2}-\d{2}"
CLOCK = r"\d{2}:\d{2}:\d{2}"
LIST_STAMP = DAY + " " + CLOCK
DETAIL_STAMP = DAY + "T" + CLOCK + r"\.\d{1,6}"
GMT_STAMP = DAY + "T" + CLOCK + r"(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)?"


def start_times(summary: Row, detail: Row) -> tuple[datetime, date, int]:
    """Compare at the precision shared by the two representations (seconds or finer)."""
    candidates: list[tuple[int, datetime]] = []
    detail_time = detail.get("startTimeGMT")
    if detail_time is not None:
        instant = stamp(detail_time, DETAIL_STAMP).replace(tzinfo=UTC)
        # The regex accepts a fraction of one through six decimal places.
        resolution_us = 10 ** (6 - len(str(detail_time).split(".")[1]))
        candidates.append((resolution_us, instant))
    epoch_ms = summary.get("beginTimestamp")
    if epoch_ms is not None:
        try:
            epoch = datetime(1970, 1, 1, tzinfo=UTC) + timedelta(
                milliseconds=integer(epoch_ms, minimum=-(2**63), bits=64)
            )
        except OverflowError:
            raise MappingError("invalid epoch") from None
        candidates.append((1000, epoch))
    coarse = summary.get("startTimeGMT")
    if coarse is not None:
        candidates.append((1000000, stamp(coarse, LIST_STAMP).replace(tzinfo=UTC)))
    if not candidates:
        raise MappingError("missing UTC start")
    precision, precise = min(candidates)
    for resolution, other in candidates:
        if precise.replace(microsecond=precise.microsecond // resolution * resolution) != other:
            raise MappingError("inconsistent activity start")

    local = None
    if summary.get("startTimeLocal") is not None:
        local = stamp(summary["startTimeLocal"], LIST_STAMP)
    if detail.get("startTimeLocal") is not None:
        detailed = stamp(detail["startTimeLocal"], DETAIL_STAMP).replace(microsecond=0)
        if local and detailed != local:
            raise MappingError("inconsistent local start")
        local = detailed
    if local is None or abs(local - precise.replace(tzinfo=None, microsecond=0)) >= timedelta(
        days=1
    ):
        raise MappingError("missing or incompatible local start")
    return precise, local.date(), precision


def splits(value: object) -> tuple[SplitSummary, ...] | None:
    if value is None:
        return None
    result = []
    for row in rows(value):
        kind = label(row.get("splitType"))
        if kind is None:
            raise MappingError("missing split type")
        count = row.get("noOfSplits")
        result.append(
            SplitSummary(
                kind,
                None if count is None else integer(count),
                quantity(row.get("distance")),
                quantity(row.get("duration")),
                quantity(row.get("averageSpeed")),
            )
        )
    return tuple(result)


@dataclass(frozen=True, repr=False)
class WorkoutResponse:
    """Carry the account and activity from the GET request; this array has no echoed ID."""

    source: Source
    activity_id: int
    payload: object


def whole(value: object) -> int:
    # Counts and indexes must be integral before any measurement rounding.
    number = source_number(value)
    if not 0 <= number <= 2**31 - 1 or number != number.to_integral_value():
        raise MappingError("invalid count")
    return int(number)


def step(row: Row, group: int, sport: str | None) -> PerformedStep:
    index = integer(row.get("stepIndex"))
    duration = label(row.get("durationType"))
    target = label(row.get("targetType"))
    amount, selector, low, high = (
        quantity(row.get(key))
        for key in ("durationValue", "targetValue", "targetValueLow", "targetValueHigh")
    )
    duration_unit = {
        "TIME": "s",
        "DISTANCE": "m",
        "REPS": "count",
        "REPEAT_UNTIL_STEPS_CMPLT": "step_index",
    }.get(duration)
    repeat_count = zone = unit = None
    bounds = (None, None)
    if duration_unit in ("count", "step_index") and amount is not None:
        whole(row["durationValue"])
    if duration == "REPEAT_UNTIL_STEPS_CMPLT":
        repeat_count = None if selector is None else whole(row["targetValue"])
    elif not (duration or "").startswith("REPEAT_") and target in (
        "SPEED",
        "CADENCE",
        "HEART_RATE",
        "POWER",
    ):
        if selector is not None and selector > 0:
            zone = whole(row["targetValue"])
        elif selector == 0 and (low is not None or high is not None):
            if low is None or high is None or low > high:
                raise MappingError("invalid target bounds")
            if target == "SPEED":
                unit = "m/s"
            elif target == "CADENCE" and sport in ("RUNNING", "CYCLING"):
                unit = "steps/min" if sport == "RUNNING" else "rpm"
            elif target == "HEART_RATE":
                if low > 100:
                    low, high, unit = low - 100, high - 100, "bpm"
                elif high <= 100:
                    unit = "percent_max_hr"
                else:
                    raise MappingError("mixed heart rate target units")
            if unit is not None:
                bounds = (low, high)
    return PerformedStep(
        group,
        index,
        label(row.get("intensity")),
        duration,
        amount if duration_unit else None,
        duration_unit if amount is not None else None,
        target,
        zone,
        *bounds,
        unit,
        repeat_count,
    )


def performed_steps(response: WorkoutResponse) -> tuple[PerformedStep, ...] | None:
    groups: set[int] = set()
    result = []
    incomplete = False
    for workout in rows(response.payload):
        group = integer(workout.get("index"))
        if group in groups:
            raise MappingError("duplicate performed workout")
        groups.add(group)
        if workout.get("steps") is None:
            incomplete = True
            continue
        seen: set[int] = set()
        for row in rows(workout["steps"]):
            item = step(row, group, label(workout.get("sport")))
            if item.step_index in seen:
                raise MappingError("duplicate step")
            seen.add(item.step_index)
            result.append(item)
    return (
        None if incomplete else tuple(sorted(result, key=lambda s: (s.workout_index, s.step_index)))
    )


def map_activity(
    binding: GarminBinding,
    summary: Row,
    *,
    detail: Row | None = None,
    workouts: WorkoutResponse | None = None,
) -> Activity:
    summary = obj(summary)
    binding.check(summary, "ownerId")
    activity_id = integer(summary.get("activityId"), minimum=1, bits=64)
    detail_summary: Row = {}
    kind = (
        label(obj(summary["activityType"]).get("typeKey"))
        if summary.get("activityType") is not None
        else None
    )
    split_data = summary.get("splitSummaries")
    if detail is not None:
        detail = obj(detail)
        binding.check(detail, "userProfileId")
        if integer(detail.get("activityId"), minimum=1, bits=64) != activity_id:
            raise MappingError("activity mismatch")
        if detail.get("summaryDTO") is not None:
            detail_summary = obj(detail["summaryDTO"])
        if detail.get("activityTypeDTO") is not None:
            detail_kind = label(obj(detail["activityTypeDTO"]).get("typeKey"))
            if kind and detail_kind and kind != detail_kind:
                raise MappingError("activity type mismatch")
            kind = detail_kind or kind
        if detail.get("splitSummaries") is not None:
            split_data = detail["splitSummaries"]
    when, local_date, precision = start_times(summary, detail_summary)
    sport = {
        "squash": "squash",
        "running": "running",
        "ultimate": "ultimate_frisbee",
        "ultimate_disc": "ultimate_frisbee",
        "ultimate_frisbee": "ultimate_frisbee",
    }.get(kind, "other")
    if kind in ("trail_running", "treadmill_running", "track_running", "indoor_running"):
        sport = "running"
    if workouts is not None and (
        workouts.source != binding.source
        or integer(workouts.activity_id, minimum=1, bits=64) != activity_id
    ):
        raise MappingError("performed workout request mismatch")

    measurements: dict[str, Decimal | None] = {}
    origins = []
    for field, key in (
        ("duration_s", "duration"),
        ("elapsed_s", "elapsedDuration"),
        ("moving_s", "movingDuration"),
        ("distance_m", "distance"),
        ("average_speed_mps", "averageSpeed"),
        ("average_hr_bpm", "averageHR"),
        ("max_hr_bpm", "maxHR"),
        ("elevation_gain_m", "elevationGain"),
        ("elevation_loss_m", "elevationLoss"),
    ):
        value = summary.get(key)
        path = f"SummarizedActivityDTO.{key}"
        if value is None:
            value = detail_summary.get(key)
            path = f"ActivitySummaryDTO.summaryDTO.{key}"
        measurements[field] = quantity(value)
        if value is not None:
            origins.append((field, path))

    return Activity(
        source=binding.source,
        external_id=str(activity_id),
        started_at=when,
        local_date=local_date,
        sport=sport,
        subtype=kind,
        splits=splits(split_data),
        steps=None if workouts is None else performed_steps(workouts),
        measurement_sources=tuple(origins),
        start_resolution_us=precision,
        **measurements,
    )


def map_activities(binding: GarminBinding, payload: object) -> tuple[Activity, ...]:
    seen: set[str] = set()
    mapped = []
    for row in rows(payload):
        item = map_activity(binding, row)
        if item.external_id in seen:
            raise MappingError("duplicate activity")
        seen.add(item.external_id)
        mapped.append(item)
    return tuple(mapped)


def window(row: Row, start_key: str, end_key: str) -> tuple[datetime | None, datetime | None]:
    def instant(value: object) -> datetime | None:
        if value is None:
            return None
        result = stamp(value, GMT_STAMP)
        # Offsetless timestamps are accepted exclusively in named GMT fields.
        try:
            return result.replace(tzinfo=UTC) if result.tzinfo is None else result.astimezone(UTC)
        except OverflowError:
            raise MappingError("invalid UTC window") from None

    start, end = instant(row.get(start_key)), instant(row.get(end_key))
    if start and end and end < start:
        raise MappingError("reversed measurement window")
    return start, end


def map_day(
    binding: GarminBinding,
    day: date,
    *,
    daily: Row | None = None,
    sleep: Row | None = None,
    hrv: Row | None = None,
) -> tuple[DailyObservation, ...]:
    """One requested provider day. An absent endpoint or metric yields no observation."""
    observations = []

    def check_day(row: Row) -> None:
        if row.get("calendarDate") != day.isoformat():
            raise MappingError("observation date mismatch")

    def add(
        row: Row,
        key: str,
        metric: DailyMetric,
        unit: str,
        method: str,
        interval: tuple[datetime | None, datetime | None],
        *,
        integral: bool = True,
    ) -> None:
        value = row.get(key)
        if value is not None:
            measured = quantity(integer(value) if integral else value)
            assert measured is not None
            observations.append(
                DailyObservation(
                    binding.source, day, metric, measured, unit, method, *interval, f"{dto}.{key}"
                )
            )

    if daily is not None:
        dto = "UserDailySummaryDto"
        daily = obj(daily)
        binding.check(daily, "userProfileId")
        check_day(daily)
        interval = window(daily, "wellnessStartTimeGmt", "wellnessEndTimeGmt")
        add(daily, "restingHeartRate", DailyMetric.RESTING_HR, "bpm", "reported", interval)
        for key, metric in (
            ("totalKilocalories", DailyMetric.TOTAL_ENERGY),
            ("activeKilocalories", DailyMetric.ACTIVE_ENERGY),
            ("bmrKilocalories", DailyMetric.BASAL_ENERGY),
        ):
            add(daily, key, metric, "kcal", "wearable_estimate", interval, integral=False)
    if sleep is not None:
        dto = "DailySleepDTO"
        sleep = obj(sleep)
        binding.check(sleep, "userProfilePK")
        check_day(sleep)
        interval = window(sleep, "sleepStartTimestampGMT", "sleepEndTimestampGMT")
        for key, metric in (
            ("sleepTimeSeconds", DailyMetric.SLEEP),
            ("lightSleepSeconds", DailyMetric.LIGHT),
            ("deepSleepSeconds", DailyMetric.DEEP),
            ("remSleepSeconds", DailyMetric.REM),
            ("awakeSleepSeconds", DailyMetric.AWAKE),
        ):
            add(sleep, key, metric, "s", "reported", interval)
    if hrv is not None:
        dto = "HrvChartDTO.hrvSummary"
        hrv = obj(hrv)
        binding.check(hrv, "userProfilePk")
        if hrv.get("hrvSummary") is not None:
            summary = obj(hrv["hrvSummary"])
            check_day(summary)
            interval = window(hrv, "startTimestampGMT", "endTimestampGMT")
            add(
                summary,
                "lastNightAvg",
                DailyMetric.OVERNIGHT_HRV,
                "source_unit_unverified",
                "reported_average",
                interval,
            )
            # The DTO defines a trailing seven-day average, without exact UTC endpoints.
            add(
                summary,
                "weeklyAvg",
                DailyMetric.WEEKLY_HRV,
                "source_unit_unverified",
                "reported_average",
                (None, None),
            )
    return tuple(observations)

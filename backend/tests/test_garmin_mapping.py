"""Invented records using the published Personal API DTO shapes."""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from fitness_intelligence.adapters.garmin.mapping import (
    GarminBinding,
    MappingError,
    WorkoutResponse,
    map_activities,
    map_activity,
    map_day,
)
from fitness_intelligence.db.models import SourceAccount
from fitness_intelligence.domain.endurance import DailyMetric, PaceState, Source

BINDING = GarminBinding(Source(uuid4(), "garmin", uuid4()), 81)
DAY = date(2024, 11, 3)
SUMMARY = {
    "ownerId": 81,
    "activityId": 7,
    "activityType": {"typeKey": "trail_running"},
    "startTimeGMT": "2024-11-03 05:30:00",
    "startTimeLocal": "2024-11-03 01:30:00",
}
DETAIL = {"activityId": 7, "userProfileId": 81}


def test_replay_and_dst_fold() -> None:
    epoch = datetime(2024, 11, 3, 5, 30, tzinfo=UTC)
    ms = int(epoch.timestamp()) * 1000 + 123
    first = dict(SUMMARY, beginTimestamp=ms)
    second = dict(
        SUMMARY, activityId=8, startTimeGMT="2024-11-03 06:30:00", beginTimestamp=ms + 3600000
    )
    items = map_activities(BINDING, [first, second])
    assert items == map_activities(BINDING, [first, second])
    assert items[0].local_date == items[1].local_date == DAY
    assert items[1].started_at - items[0].started_at == timedelta(hours=1)
    assert items[0].started_at == epoch + timedelta(milliseconds=123)
    assert items[0].source == BINDING.source
    assert items[0].external_id == "7"
    assert map_activity(BINDING, dict(first, startTimeLocal="2024-11-02 22:30:00")).local_date < DAY
    with pytest.raises(MappingError, match="duplicate activity"):
        map_activities(BINDING, [first, first])


def test_measurements_precision_and_source_selection() -> None:
    detail = dict(
        DETAIL,
        summaryDTO={
            "startTimeGMT": "2024-11-03T05:30:00.123456",
            "distance": 100,
            "averageSpeed": 2.5,
            "maxHR": 158,
        },
    )
    item = map_activity(
        BINDING,
        dict(
            SUMMARY,
            beginTimestamp=1730611800123,
            duration=1000.5,
            elapsedDuration=1100,
            movingDuration=988,
            distance=Decimal("2480.1234567885"),
            averageHR=140.5,
            elevationGain=114.4245,
            elevationLoss=0,
        ),
        detail=detail,
    )
    assert item.started_at.microsecond == 123456
    assert item.distance_m == Decimal("2480.123456788")
    assert (item.sport, item.subtype) == ("running", "trail_running")
    assert (item.duration_s, item.elapsed_s, item.moving_s) == (1000.5, 1100, 988)
    assert (item.average_hr_bpm, item.max_hr_bpm) == (140.5, 158)
    assert (item.elevation_gain_m, item.elevation_loss_m) == (Decimal("114.4245"), 0)
    assert item.running_pace() == (PaceState.DERIVED, 400)
    assert map_activity(BINDING, SUMMARY).running_pace() == (PaceState.MISSING, None)
    for key in ("distance", "averageSpeed"):
        zero = map_activity(BINDING, dict(SUMMARY, **({"averageSpeed": 2.5} | {key: 0})))
        assert zero.running_pace() == (PaceState.NOT_APPLICABLE, None)


@pytest.mark.parametrize(
    "key,value",
    [
        ("ownerId", 82),
        ("ownerId", None),
        ("activityId", True),
        ("activityId", "7"),
        ("activityId", 2**63),
        ("activityId", 0),
        ("startTimeLocal", "2024-11-03"),
        ("startTimeGMT", "2024-11-03 01:30:00-04:00"),
        ("beginTimestamp", 0),
        ("beginTimestamp", 2**62),
        ("startTimeGMT", None),
        ("distance", "1.2"),
        ("averageSpeed", -1),
        ("averageHR", True),
        ("distance", float("nan")),
        ("duration", float("inf")),
        ("duration", Decimal("1e-100000")),
        ("duration", Decimal("9999999999999.9999999999")),
        ("activityType", "running"),
    ],
)
def test_invalid_activity(key: str, value: object) -> None:
    with pytest.raises(MappingError):
        map_activity(BINDING, SUMMARY | {key: value})


@pytest.mark.parametrize(
    "updates",
    [
        {"activityId": 8},
        {"userProfileId": 82},
        {"summaryDTO": []},
        {"summaryDTO": {"startTimeGMT": "2024-11-03T06:30:00.000"}},
        {"summaryDTO": {"startTimeLocal": "2024-11-03T02:30:00.000"}},
        {"activityTypeDTO": {"typeKey": "squash"}},
    ],
)
def test_detail_join_checks(updates: dict) -> None:
    with pytest.raises(MappingError):
        map_activity(BINDING, SUMMARY, detail=DETAIL | updates)


@pytest.mark.parametrize(
    "key,sport",
    [
        ("squash", "squash"),
        ("ultimate_disc", "ultimate_frisbee"),
        ("new_activity", "other"),
        ("new_running", "other"),
    ],
)
def test_sports_and_missing_values(key: str, sport: str) -> None:
    item = map_activity(BINDING, dict(SUMMARY, activityType={"typeKey": key}, distance=None))
    assert (item.sport, item.subtype, item.distance_m, item.splits, item.steps) == (
        sport,
        key,
        None,
        None,
        None,
    )
    assert item.running_pace() == (PaceState.NOT_APPLICABLE, None)


def response(steps: list) -> WorkoutResponse:
    return WorkoutResponse(BINDING.source, 7, [{"index": 0, "sport": "RUNNING", "steps": steps}])


def test_splits_and_performed_targets() -> None:
    record = {
        "splitType": "RUN_ACTIVE",
        "noOfSplits": 3,
        "distance": 850.125,
        "duration": 250,
        "averageSpeed": 3.4,
    }
    steps = [
        {
            "stepIndex": 2,
            "durationType": "REPEAT_UNTIL_STEPS_CMPLT",
            "durationValue": 0,
            "targetValue": 3,
        },
        {
            "stepIndex": 1,
            "durationType": "DISTANCE",
            "durationValue": 300,
            "targetType": "SPEED",
            "targetValue": 0,
            "targetValueLow": 2.5,
            "targetValueHigh": 3.125,
        },
        {
            "stepIndex": 0,
            "intensity": "WARMUP",
            "durationType": "TIME",
            "durationValue": 300,
            "targetType": "HEART_RATE",
            "targetValue": 0,
            "targetValueLow": 240,
            "targetValueHigh": 255,
        },
    ]
    item = map_activity(
        BINDING,
        dict(SUMMARY, splitSummaries=[record]),
        detail=dict(DETAIL, splitSummaries=[record]),
        workouts=response(steps),
    )
    assert len(item.splits) == 1
    (split,) = item.splits
    assert (
        split.kind,
        split.count,
        split.distance_m,
        split.duration_s,
        split.average_speed_mps,
    ) == ("RUN_ACTIVE", 3, Decimal("850.125"), 250, Decimal("3.4"))
    warm, run, repeat = item.steps
    assert (warm.intensity, warm.duration_unit, warm.duration_value) == ("WARMUP", "s", 300)
    assert (warm.target_low, warm.target_high, warm.target_unit) == (140, 155, "bpm")
    assert (run.duration_unit, run.target_low, run.target_high, run.target_unit) == (
        "m",
        2.5,
        3.125,
        "m/s",
    )
    assert (repeat.duration_unit, repeat.duration_value, repeat.repeat_count) == (
        "step_index",
        0,
        3,
    )
    assert repeat.target_zone is None


def test_sparse_steps_and_request_correlation() -> None:
    item = map_activity(
        BINDING,
        SUMMARY,
        workouts=response(
            [
                {"stepIndex": 2, "targetType": "HEART_RATE", "targetValue": 3},
                {"stepIndex": 1, "durationType": "OPEN", "targetType": "NEW", "targetValue": 2},
            ]
        ),
    )
    unsupported, zoned = item.steps
    assert unsupported.target_type == "NEW" and unsupported.target_zone is None
    assert unsupported.duration_value is None
    assert zoned.target_zone == 3
    for reply in (
        replace(response([]), activity_id=8),
        replace(response([]), source=replace(BINDING.source, source_account_id=uuid4())),
        response([{"stepIndex": 0}, {"stepIndex": 0}]),
        WorkoutResponse(BINDING.source, 7, [{"index": 1, "steps": []}, {"index": 1, "steps": []}]),
        response(
            [
                {
                    "stepIndex": 0,
                    "targetType": "SPEED",
                    "targetValue": 0,
                    "targetValueLow": 3,
                    "targetValueHigh": 2,
                }
            ]
        ),
    ):
        with pytest.raises(MappingError):
            map_activity(BINDING, SUMMARY, workouts=reply)
    assert map_activity(BINDING, SUMMARY, workouts=response([])).steps == ()


def test_trusted_account_scope() -> None:
    account = SourceAccount(
        id=BINDING.source.source_account_id,
        user_id=BINDING.source.owner_id,
        status="active",
        provider="garmin",
        provider_account_id="81",
    )
    assert GarminBinding.from_account(owner_id=account.user_id, account=account) == BINDING
    with pytest.raises(MappingError):
        GarminBinding.from_account(owner_id=uuid4(), account=account)
    for field, value in (
        ("status", "disconnected"),
        ("provider_account_id", "display name"),
        ("provider", "hevy"),
    ):
        original = getattr(account, field)
        setattr(account, field, value)
        with pytest.raises(MappingError):
            GarminBinding.from_account(owner_id=account.user_id, account=account)
        setattr(account, field, original)


def test_daily_grains_windows_units_and_provenance() -> None:
    daily = {
        "userProfileId": 81,
        "calendarDate": DAY.isoformat(),
        "restingHeartRate": 58,
        "totalKilocalories": 1740.75,
        "activeKilocalories": 240.75,
        "bmrKilocalories": 1500,
        "wellnessStartTimeGmt": "2024-11-03T04:01:00Z",
        "consumedKilocalories": 1900,
    }
    sleep = {
        "userProfilePK": 81,
        "calendarDate": DAY.isoformat(),
        "sleepTimeSeconds": 25000,
        "deepSleepSeconds": 2400,
        "remSleepSeconds": 5000,
        "lightSleepSeconds": 17600,
        "awakeSleepSeconds": 0,
        "sleepStartTimestampGMT": "2024-11-02T23:15:00-04:00",
        "sleepEndTimestampGMT": "2024-11-03T06:20:00-05:00",
        "sleepScores": {"overall": 80},
    }
    hrv = {
        "userProfilePk": 81,
        "hrvSummary": {"calendarDate": DAY.isoformat(), "lastNightAvg": 44, "weeklyAvg": 48},
        "startTimestampGMT": "2024-11-03T04:00:00.000",
        "endTimestampGMT": "2024-11-03T10:15:00.000",
    }
    result = map_day(BINDING, DAY, daily=daily, sleep=sleep, hrv=hrv)
    assert result == map_day(BINDING, DAY, daily=daily, sleep=sleep, hrv=hrv | {"hrvReadings": []})
    metrics = {item.metric: item for item in result}
    assert len(metrics) == len(result) == len(DailyMetric)
    assert all(x.local_date == DAY and x.source == BINDING.source for x in result)
    total = metrics[DailyMetric.TOTAL_ENERGY]
    assert (total.value, total.unit, total.method) == (
        Decimal("1740.75"),
        "kcal",
        "wearable_estimate",
    )
    assert metrics[DailyMetric.AWAKE].value == 0
    assert metrics[DailyMetric.SLEEP].window_start == datetime(2024, 11, 3, 3, 15, tzinfo=UTC)
    assert metrics[DailyMetric.SLEEP].window_end == datetime(2024, 11, 3, 11, 20, tzinfo=UTC)
    assert metrics[DailyMetric.OVERNIGHT_HRV].unit == "source_unit_unverified"
    assert metrics[DailyMetric.WEEKLY_HRV].window_start is None
    assert total.window_end is None


def test_sparse_and_malformed_wellness() -> None:
    daily = {"calendarDate": DAY.isoformat(), "userProfileId": 81, "activeKilocalories": None}
    assert map_day(BINDING, DAY, daily=daily) == ()
    assert map_day(BINDING, DAY, hrv={"userProfilePk": 81, "hrvSummary": None}) == ()
    for payload in (
        {"daily": daily | {"calendarDate": "2024-11-04"}},
        {"daily": daily | {"restingHeartRate": True}},
        {"daily": daily | {"bmrKilocalories": -1}},
        {"daily": daily | {"userProfileId": "81"}},
        {"sleep": {"userProfilePK": 82, "calendarDate": DAY.isoformat()}},
        {"hrv": {"userProfilePk": 81, "hrvSummary": {"weeklyAvg": 42}}},
        {
            "daily": daily
            | {
                "wellnessStartTimeGmt": "2024-11-04T00:00:00Z",
                "wellnessEndTimeGmt": "2024-11-03T00:00:00Z",
            }
        },
    ):
        with pytest.raises(MappingError):
            map_day(BINDING, DAY, **payload)


def test_partial_precision_and_measurement_provenance() -> None:
    item = map_activity(
        BINDING,
        dict(SUMMARY, startTimeLocal=None, beginTimestamp=1730611800123, distance=0),
        detail=dict(
            DETAIL,
            summaryDTO={
                "startTimeGMT": "2024-11-03T05:30:00.1",
                "startTimeLocal": "2024-11-03T01:30:00.1",
                "averageSpeed": 2,
            },
        ),
    )
    assert item.started_at.microsecond == 123000
    assert dict(item.measurement_sources) == {
        "distance_m": "SummarizedActivityDTO.distance",
        "average_speed_mps": "ActivitySummaryDTO.summaryDTO.averageSpeed",
    }
    with pytest.raises(ValueError, match="invalid pace input"):
        replace(item, average_speed_mps=Decimal("NaN")).running_pace()


@pytest.mark.parametrize(
    "sport,target,low,high,unit",
    [
        ("RUNNING", "CADENCE", 150, 180, "steps/min"),
        ("CYCLING", "CADENCE", 75, 90, "rpm"),
        ("RUNNING", "HEART_RATE", 60, 75, "percent_max_hr"),
        ("RUNNING", "POWER", 1250, 1300, None),
    ],
)
def test_custom_target_units(
    sport: str, target: str, low: int, high: int, unit: str | None
) -> None:
    reply = WorkoutResponse(
        BINDING.source,
        7,
        [
            {
                "index": 1,
                "sport": sport,
                "steps": [
                    {
                        "stepIndex": 0,
                        "durationType": "OPEN",
                        "targetType": target,
                        "targetValue": 0,
                        "targetValueLow": low,
                        "targetValueHigh": high,
                    }
                ],
            }
        ],
    )
    (item,) = map_activity(BINDING, SUMMARY, workouts=reply).steps
    assert item.target_unit == unit
    assert (item.target_low, item.target_high) == ((low, high) if unit else (None, None))


def test_fractional_selector_is_never_rounded_into_a_zone() -> None:
    with pytest.raises(MappingError, match="invalid count"):
        map_activity(
            BINDING,
            SUMMARY,
            workouts=response(
                [
                    {
                        "stepIndex": 0,
                        "targetType": "HEART_RATE",
                        "targetValue": Decimal("1.0000000001"),
                    }
                ]
            ),
        )


@pytest.mark.parametrize(
    "start,end",
    [
        (1_730_591_852_123, 1_730_617_741_987),
        ("2024-11-02T23:57:32.123Z", "2024-11-03T07:09:01.987"),
        ("2024-11-03T01:57:32.123+02:00", "2024-11-03T02:09:01.987-05:00"),
    ],
)
def test_sleep_window_encodings_across_midnight(start: int | str, end: int | str) -> None:
    (obs,) = map_day(
        BINDING,
        DAY,
        sleep={
            "calendarDate": DAY.isoformat(),
            "userProfilePK": 81,
            "sleepTimeSeconds": 18000,
            "sleepStartTimestampGMT": start,
            "sleepEndTimestampGMT": end,
        },
    )
    assert obs.local_date == DAY
    assert obs.window_start == datetime(2024, 11, 2, 23, 57, 32, 123000, tzinfo=UTC)
    assert obs.window_end == datetime(2024, 11, 3, 7, 9, 1, 987000, tzinfo=UTC)


@pytest.mark.parametrize("have_start,have_end", [(True, False), (False, True), (False, False)])
def test_sleep_epoch_partial_window(have_start: bool, have_end: bool) -> None:
    sleep = {"calendarDate": DAY.isoformat(), "userProfilePK": 81, "sleepTimeSeconds": 18000}
    if have_start:
        sleep["sleepStartTimestampGMT"] = 1_730_591_852_123
    if have_end:
        sleep["sleepEndTimestampGMT"] = 1_730_617_741_987
    (obs,) = map_day(BINDING, DAY, sleep=sleep)
    assert obs.window_start == (
        datetime(2024, 11, 2, 23, 57, 32, 123000, tzinfo=UTC) if have_start else None
    )
    assert obs.window_end == (
        datetime(2024, 11, 3, 7, 9, 1, 987000, tzinfo=UTC) if have_end else None
    )


@pytest.mark.parametrize(
    "invalid",
    [
        True,
        0,
        -1_730_591_852_123,
        1_730_591_852,
        1_730_591_852_123_000,
        1_730_591_852_123_000_000,
        "1730591852123",
        Decimal("1730591852123.0"),
        Decimal("1730591852123.25"),
        "2024-11-02 23:57:32",
        "2024-11-02T23:57:32.1234567Z",
    ],
)
def test_reject_unsupported_sleep_instant(invalid: object) -> None:
    with pytest.raises(MappingError):
        map_day(
            BINDING,
            DAY,
            sleep={
                "calendarDate": DAY.isoformat(),
                "userProfilePK": 81,
                "sleepEndTimestampGMT": invalid,
            },
        )


def test_sleep_epoch_rejects_reversed_window_and_other_feed_encodings() -> None:
    with pytest.raises(MappingError, match="reversed measurement window"):
        map_day(
            BINDING,
            DAY,
            sleep={
                "calendarDate": DAY.isoformat(),
                "userProfilePK": 81,
                "sleepStartTimestampGMT": 1_730_617_741_987,
                "sleepEndTimestampGMT": 1_730_591_852_123,
            },
        )
    with pytest.raises(MappingError, match="invalid timestamp"):
        map_day(
            BINDING,
            DAY,
            daily={
                "calendarDate": DAY.isoformat(),
                "userProfileId": 81,
                "wellnessEndTimeGmt": 1_730_617_741_987,
            },
        )
    with pytest.raises(MappingError, match="invalid timestamp"):
        map_day(
            BINDING,
            DAY,
            hrv={
                "userProfilePk": 81,
                "hrvSummary": {"calendarDate": DAY.isoformat()},
                "startTimestampGMT": 1_730_591_852_123,
            },
        )

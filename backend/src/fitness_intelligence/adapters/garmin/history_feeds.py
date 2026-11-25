"""Strict historical DTO projections. Range omission is endpoint-specific."""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from fitness_intelligence.db.endurance_models import DailyRecoveryObservation
from fitness_intelligence.db.nutrition_models import DailyIntakeObservation
from fitness_intelligence.domain.endurance import DailyMetric, DailyObservation

from .binding import Feed, feed_for
from .client import Endpoint, GarminClient, GarminError
from .history_state import Category, account_key, close_issues, days, issue
from .mapping import GarminBinding, MappingError, Row, integer, map_day, obj, rows, window
from .nutrition import Intake, account_scoped, daily_intake, food_intake
from .persistence import save_observation

DAILY = (Category.EXPENDITURE, Category.RESTING, Category.INTAKE)
ENERGY = {
    "burnedTotal": DailyMetric.TOTAL_ENERGY,
    "burnedActive": DailyMetric.ACTIVE_ENERGY,
    "burnedResting": DailyMetric.BASAL_ENERGY,
}
V2 = "UserDailySummaryV2DTO.calories."


def read_range(
    client: GarminClient, binding: GarminBinding, endpoint: Endpoint, first: date, last: date
) -> dict[date, list[Row]]:
    params = {"startDate": first.isoformat(), "endDate": last.isoformat()}
    try:
        if endpoint in (Endpoint.HRV_RANGE, Endpoint.WEIGHT_RANGE):
            payload = client.read(endpoint, day=first.isoformat(), end_day=last.isoformat())
        else:
            payload = client.read(endpoint, params=params)
    except GarminError as exc:
        if endpoint == Endpoint.HRV_RANGE and str(exc) == "no_content":
            return {d: [] for d in days(first, last)}
        raise
    if endpoint == Endpoint.HRV_RANGE:
        wrapper = obj(payload)
        binding.check(wrapper, "userProfilePk")
        payload = wrapper.get("hrvSummaries")
    if endpoint == Endpoint.DAILY_RANGE:
        payload = obj(payload).get("data")
    by_day: dict[date, list[Row]] = defaultdict(list)
    for row in rows(payload):
        try:
            day = date.fromisoformat(row["calendarDate"])
            if row["calendarDate"] != day.isoformat() or not first <= day <= last:
                raise ValueError
        except (ValueError, KeyError, TypeError):
            raise MappingError("range date mismatch") from None
        if endpoint == Endpoint.DAILY_RANGE:
            binding.check(row, "userProfilePk")
        elif endpoint == Endpoint.SLEEP_RANGE:
            binding.check(row, "userProfilePK")
        else:
            account_scoped(row)
        if by_day[day] and endpoint not in (Endpoint.WEIGHT_RANGE, Endpoint.DAILY_RANGE):
            raise MappingError("duplicate daily summary")
        by_day[day].append(row)
    return dict(by_day)


def calories(series: Sequence[Row]) -> Row:
    if len(series) != 1 or str(series[0].get("source", "")).lower() != "garmin":
        return {}
    nested = series[0].get("calories")
    values = obj(nested) if nested is not None else {}
    if any("includesCalorieConsumedData" in r for r in (series[0], values)):
        raise MappingError("unreviewed v2 intake presence")
    return values


def expenditure(binding: GarminBinding, day: date, series: Sequence[Row]) -> list[DailyObservation]:
    fields = calories(series)
    if not fields:
        return []
    chronology = series[0].get("wellnessChronology")
    interval = window(
        obj(chronology) if chronology is not None else {}, "startTimestampGmt", "endTimestampGmt"
    )
    return [
        DailyObservation(
            binding.source,
            day,
            metric,
            Decimal(integer(fields[key])),
            "kcal",
            "wearable_estimate",
            *interval,
            V2 + key,
        )
        for key, metric in ENERGY.items()
        if fields.get(key) is not None
    ]


def v2_intake(series: Sequence[Row]) -> Intake | None:
    raw = calories(series).get("consumedValue")
    if raw is None:
        return None
    kcal = integer(raw)
    return Intake(V2 + "consumedValue", Decimal(kcal), None) if kcal else None


def targeted_intake(
    client: GarminClient, binding: GarminBinding, day: date, daily: Row
) -> list[Intake]:
    first = daily_intake(binding, day, daily)
    food = obj(
        client.read(
            Endpoint.FOOD,
            day=day.isoformat(),
            params={"includeGoals": "false", "includeMedia": "false", "includeNutrition": "true"},
        )
    )
    second = food_intake(day, food)
    return [total for total in (first, second) if total is not None]


def intake_conflict(
    session: Session, binding: GarminBinding, day: date, when: datetime, positive: bool
) -> bool:
    observations = session.scalars(
        select(DailyIntakeObservation).filter_by(**account_key(binding.source), local_date=day)
    ).all()
    values = {r.source_field: str(r.reported_kcal) for r in observations}
    if len({r.reported_kcal for r in observations}) > 1:
        issue(
            session,
            binding.source,
            Category.INTAKE,
            day,
            "day",
            "source_disagreement",
            values,
            when,
        )
        return True
    if positive:
        close_issues(
            session, binding.source, Category.INTAKE, day, "day", ("source_disagreement",), when
        )
    return False


def recovery(
    client: GarminClient,
    binding: GarminBinding,
    category: Category,
    day: date,
    series: list[Row] | None,
) -> Sequence[DailyObservation]:
    if category == Category.SLEEP:
        row = series[0] if series else feed_for(client, binding, day, Feed.SLEEP)
        return map_day(binding, day, sleep=row)
    if series is None:
        try:
            return map_day(binding, day, hrv=feed_for(client, binding, day, Feed.HRV))
        except GarminError as exc:
            if str(exc) == "no_content":
                return ()
            raise
    if not series:
        return ()
    wrapper = {"userProfilePk": binding.profile_id, "hrvSummary": series[0]}
    return [
        replace(
            obs, source_field="HrvDailySummaryDTO.hrvSummaries." + obs.source_field.split(".")[-1]
        )
        for obs in map_day(binding, day, hrv=wrapper)
    ]


def save_recovery(session: Session, obs: DailyObservation, when: datetime) -> str:
    if obs.window_start is None and obs.window_end is None:
        prior = session.scalar(
            select(DailyRecoveryObservation).filter_by(
                **account_key(obs.source), local_date=obs.local_date, metric=obs.metric.value
            )
        )
        if (
            prior
            and (prior.window_start or prior.window_end)
            and prior.source_field != obs.source_field
            and (prior.value, prior.method, prior.unit) == (obs.value, obs.method, obs.unit)
        ):
            # Keep the stronger original observation and its actual retrieval provenance.
            return "unchanged"
    return save_observation(session, obs, when)

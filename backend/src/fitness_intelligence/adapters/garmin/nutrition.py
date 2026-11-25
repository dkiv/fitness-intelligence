"""Bounded projections of Garmin daily calorie totals and individual weight entries."""

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import select
from sqlalchemy.orm import Session

from fitness_intelligence.db.nutrition_models import BodyWeightObservation, DailyIntakeObservation

from .binding import Feed, VerifiedSample, feed_for
from .client import Endpoint, GarminClient, GarminError
from .mapping import GarminBinding, MappingError, Row, integer, obj, quantity, rows

VERSION = "garmin-personal-b3.2-v1"


@dataclass(frozen=True)
class Intake:
    field: str
    kcal: Decimal
    presence: bool | None


class WeightUnit(StrEnum):
    GRAMS = "g"
    KILOGRAMS = "kg"


@dataclass(frozen=True)
class WeighIn:
    instant: datetime
    source_value: Decimal
    unit: WeightUnit
    kg: Decimal


def amount(raw: object) -> Decimal:
    measured = quantity(raw)
    if measured is None or measured != raw:
        raise MappingError("unsupported measurement precision")
    return measured


def daily_intake(binding: GarminBinding, day: date, row: Row) -> Intake | None:
    binding.check(row, "userProfileId")
    if row.get("calendarDate") != day.isoformat():
        raise MappingError("intake date mismatch")
    flag = row.get("includesCalorieConsumedData")
    if flag is not None and type(flag) is not bool:
        raise MappingError("invalid intake presence flag")
    raw = row.get("consumedKilocalories")
    if raw is None:
        return None
    kcal = amount(raw)
    if flag is False and kcal:
        raise MappingError("contradictory intake presence")
    if not kcal and flag is not True:
        return None
    return Intake("UserDailySummaryDto.consumedKilocalories", kcal, flag)


def account_scoped(row: Row) -> None:
    # These DTOs document no identity echo. A newly supplied owner field needs review
    # before its namespace can be compared with the pin.
    if any(
        row.get(key) is not None
        for key in (
            "ownerId",
            "userId",
            "userProfileId",
            "userProfilePk",
            "userProfilePK",
            "profileId",
        )
    ):
        raise MappingError("unreviewed account evidence")


def food_intake(day: date, row: Row) -> Intake | None:
    account_scoped(row)
    content = row.get("dailyNutritionContent")
    if row.get("mealDate") != day.isoformat() and (row.get("mealDate") is not None or content):
        raise MappingError("food log date mismatch")
    if content is None:
        return None
    raw = obj(content).get("calories")
    if raw is None:
        return None
    kcal = Decimal(integer(raw))
    if not kcal:
        # An empty nutrition template can report zero. Require a positive logging event.
        meals = rows(row["mealDetails"]) if row.get("mealDetails") is not None else ()
        if not any(rows(meal["loggedFoods"]) for meal in meals if meal.get("loggedFoods")):
            return None
    return Intake("DailyNutritionSummaryDTO.dailyNutritionContent.calories", kcal, None)


def read_intake(
    client: GarminClient, sample: VerifiedSample, day: date, anchor: date
) -> list[Intake]:
    daily = sample.feeds.get(Feed.DAILY) if day == anchor else None
    if daily is None:
        try:
            daily = feed_for(client, sample.binding, day, Feed.DAILY)
        except GarminError as exc:
            if str(exc) not in ("no_content", "not_found"):
                raise
    observations = []
    if daily is not None and (summary := daily_intake(sample.binding, day, daily)) is not None:
        observations.append(summary)
    try:
        food = obj(
            client.read(
                Endpoint.FOOD,
                day=day.isoformat(),
                params={
                    "includeGoals": "false",
                    "includeMedia": "false",
                    "includeNutrition": "true",
                },
            )
        )
    except GarminError as exc:
        if str(exc) not in ("no_content", "not_found"):
            raise
    else:
        if (entry := food_intake(day, food)) is not None:
            observations.append(entry)
    return observations


def map_weights(day: date, payload: object, unit: WeightUnit) -> tuple[list[WeighIn], int]:
    candidates = []
    unresolved = 0
    instants: Counter[datetime] = Counter()
    for row in rows(payload):
        account_scoped(row)
        if row.get("calendarDate") != day.isoformat():
            raise MappingError("weight date mismatch")
        raw = row.get("weight")
        value = amount(raw) if raw is not None else None
        if value is not None and value <= 0:
            raise MappingError("invalid weight")
        stamp = row.get("timestampGMT")
        if stamp is None:
            if raw is not None:
                unresolved += 1
            continue
        ms = integer(stamp, bits=64)
        if not 10**12 <= ms < 10**13:
            raise MappingError("unsupported weight epoch milliseconds")
        instant = datetime(1970, 1, 1, tzinfo=UTC) + timedelta(milliseconds=ms)
        instants[instant] += 1
        if value is not None:
            kg = amount(value / 1000) if unit == WeightUnit.GRAMS else value
            candidates.append(WeighIn(instant, value, unit, kg))
    unique = [c for c in candidates if instants[c.instant] == 1]
    return unique, unresolved + len(candidates) - len(unique)


def save_intake(
    session: Session, binding: GarminBinding, day: date, intake: Intake, retrieved: datetime
) -> str:
    source = binding.source
    key = dict(
        user_id=source.owner_id,
        provider=source.provider,
        source_account_id=source.source_account_id,
        local_date=day,
        source_field=intake.field,
    )
    row = session.scalar(select(DailyIntakeObservation).filter_by(**key))
    presence = intake.presence
    if row is None:
        row = DailyIntakeObservation(**key, completeness="unknown")
        session.add(row)
        result = "created"
    else:
        if row.reported_kcal == intake.kcal and presence is None:
            presence = row.source_data_present
        if row.reported_kcal != intake.kcal:
            row.completeness, row.upstream_writer = "unknown", None
        result = (
            "unchanged"
            if (row.reported_kcal, row.source_data_present, row.mapping_version)
            == (intake.kcal, presence, VERSION)
            else "updated"
        )
    row.reported_kcal, row.source_data_present = intake.kcal, presence
    row.retrieved_at, row.mapping_version = retrieved, VERSION
    return result


def save_weight(
    session: Session, binding: GarminBinding, day: date, entry: WeighIn, retrieved: datetime
) -> str:
    source = binding.source
    key = dict(
        user_id=source.owner_id,
        provider=source.provider,
        source_account_id=source.source_account_id,
        measured_at=entry.instant,
        upstream_id=None,
    )
    row = session.scalar(select(BodyWeightObservation).filter_by(**key))
    if row is None:
        session.add(
            BodyWeightObservation(
                **key,
                mass_kg=entry.kg,
                source_value=entry.source_value,
                source_unit=entry.unit.value,
                documented_source_unit="kg",
                time_resolution_us=1000,
                source_field="DateWeightDTO.weight",
                retrieved_at=retrieved,
                local_date=day,
                mapping_version=VERSION,
            )
        )
        return "created"
    if (row.mass_kg, row.source_value, row.source_unit, row.local_date, row.mapping_version) != (
        entry.kg,
        entry.source_value,
        entry.unit.value,
        day,
        VERSION,
    ):
        # A changed value at this instant could be a different weigh-in.
        return "unresolved"
    row.retrieved_at = retrieved
    return "unchanged"

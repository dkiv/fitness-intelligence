"""Two date samples. Only fixed field names and aggregate counts leave this module."""

import math
from collections import Counter
from collections.abc import Iterator
from datetime import date, timedelta
from typing import Any

from .client import Endpoint, GarminClient, GarminError, TokenExchangeError

# Paths cross arrays of objects (e.g. meals and their foods) without retaining their contents.
# The leaf type keeps a provider error object or string from passing as a measurement.
SCHEMA: dict[Endpoint, dict[str, str]] = {
    Endpoint.TYPES: {"text": "key parent"},
    Endpoint.ZONES: {
        "text": "sport trainingMethod",
        "number": "zone1Floor zone2Floor zone3Floor zone4Floor zone5Floor maxHeartRateUsed",
    },
    Endpoint.ACTIVITIES: {
        "number": (
            "activityId ownerId distance duration elapsedDuration movingDuration "
            "averageSpeed averageHR maxHR lapCount activityType.parentTypeId hrTimeInZone_1 "
            "hrTimeInZone_2 hrTimeInZone_3 hrTimeInZone_4 hrTimeInZone_5"
        ),
        "text": "activityType.typeKey startTimeLocal startTimeGMT",
        "list": "splitSummaries",
    },
    Endpoint.DETAIL: {
        "number": (
            "activityId userProfileId summaryDTO.distance summaryDTO.duration "
            "summaryDTO.averageSpeed summaryDTO.averageHR summaryDTO.maxHR "
            "metadataDTO.lapCount splitSummaries.noOfSplits"
        ),
        "text": (
            "activityTypeDTO.typeKey metadataDTO.fileFormat.formatKey metadataDTO.lastUpdateDate"
        ),
        "list": "splitSummaries",
    },
    Endpoint.WORKOUTS: {
        "list": "steps",
        "text": "sport steps.intensity steps.durationType steps.targetType",
        "number": "steps.stepIndex steps.durationValue steps.targetValue",
    },
    Endpoint.DAILY: {
        "number": (
            "userProfileId restingHeartRate totalKilocalories activeKilocalories "
            "bmrKilocalories consumedKilocalories"
        ),
        "flag": "includesCalorieConsumedData",
    },
    Endpoint.HRV: {
        "number": "hrvSummary.lastNightAvg hrvSummary.weeklyAvg hrvReadings.hrvValue",
        "list": "hrvReadings",
    },
    Endpoint.SLEEP: {
        "number": (
            "sleepTimeSeconds deepSleepSeconds lightSleepSeconds remSleepSeconds "
            "awakeSleepSeconds averageSpO2Value averageRespirationValue avgHeartRate"
        ),
        "object": "sleepScores",
    },
    Endpoint.HEART: {
        "number": "restingHeartRate minHeartRate maxHeartRate",
        "list": "heartRateValues heartRateValueDescriptors",
    },
    Endpoint.BATTERY: {"number": "charged drained", "list": "bodyBatteryValuesArray"},
    Endpoint.FOOD: {
        "number": (
            "dailyNutritionContent.calories dailyNutritionContent.protein "
            "dailyNutritionContent.carbs dailyNutritionContent.fat "
            "mealDetails.mealNutritionContent.calories "
            "mealDetails.mealNutritionContent.protein "
            "mealDetails.mealNutritionContent.carbs mealDetails.mealNutritionContent.fat"
        ),
        "list": "mealDetails mealDetails.loggedFoods",
        "text": (
            "mealDetails.loggedFoods.logSource mealDetails.loggedFoods.foodMetaData.source "
            "loggedFoodsWithServingSizes.foodMetaData.source"
        ),
    },
    Endpoint.WEIGHT: {"number": "weight timestampGMT", "text": "calendarDate"},
}

ARRAYS = {
    Endpoint.TYPES,
    Endpoint.ZONES,
    Endpoint.ACTIVITIES,
    Endpoint.WORKOUTS,
    Endpoint.BATTERY,
    Endpoint.WEIGHT,
}
MISSING = object()
INVALID = object()


def leaves(obj: Any, parts: list[str]) -> Iterator[Any]:
    if not parts or obj is None or obj is MISSING:
        yield obj
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                yield from leaves(item, parts)
            else:
                yield INVALID
    elif isinstance(obj, dict):
        yield from leaves(obj.get(parts[0], MISSING), parts[1:])
    else:
        yield INVALID


def state(value: Any, kind: str) -> str:
    if value is MISSING:
        return "missing"
    if value is None:
        return "null"
    if kind == "number" and (type(value) is int or type(value) is float and math.isfinite(value)):
        return "zero" if value == 0 else "present"
    if kind == "flag" and type(value) is bool:
        return "true" if value else "false"
    container = {"text": str, "list": list, "object": dict}.get(kind)
    if container is not None and isinstance(value, container):
        return "present" if value else "empty"
    return "invalid"


def records(endpoint: Endpoint, data: Any) -> list[dict[str, Any]]:
    if endpoint in ARRAYS:
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return data
    elif isinstance(data, dict):
        return [data] if data else []
    raise GarminError("unexpected_schema")


def series_readings(
    rows: list[dict[str, Any]],
    samples: str,
    descriptors: str,
    key_field: str,
    index_field: str,
    metric: str,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        values = row.get(samples)
        if not isinstance(values, list) or not values:
            continue
        columns = row.get(descriptors)
        indexes = (
            [
                col.get(index_field)
                for col in columns
                if isinstance(col, dict) and col.get(key_field) == metric
            ]
            if isinstance(columns, list)
            else []
        )
        if len(indexes) != 1 or type(indexes[0]) is not int or indexes[0] < 0:
            counts["unresolved_column"] += len(values)
            continue
        index = indexes[0]
        for entry in values:
            value = entry[index] if isinstance(entry, list) and index < len(entry) else INVALID
            counts[state(value, "number")] += 1
    return counts


def summarize(endpoint: Endpoint, rows: list[dict[str, Any]]) -> dict[str, Any]:
    fields = {}
    for kind, paths in SCHEMA[endpoint].items():
        for path in paths.split():
            fields[path] = Counter(state(v, kind) for v in leaves(rows, path.split(".")))
    result: dict[str, Any] = {"status": "ok", "records": len(rows), "fields": fields}
    if any(counts.get("invalid") for counts in fields.values()):
        result["status"] = "unexpected_field_type"
    elif rows and all(all(k == "missing" for k in counts) for counts in fields.values()):
        result["status"] = "unrecognized_fields"
    if endpoint in {Endpoint.ACTIVITIES, Endpoint.TYPES}:
        path = "activityType.typeKey" if endpoint is Endpoint.ACTIVITIES else "key"
        keys = {k.lower() for k in leaves(rows, path.split(".")) if isinstance(k, str)}
        result["sport_keys_in_sample"] = {
            "running": any(k == "running" or k.endswith("_running") for k in keys),
            "squash": "squash" in keys,
            "ultimate_frisbee": bool(keys & {"ultimate", "ultimate_disc", "ultimate_frisbee"}),
        }
    if endpoint is Endpoint.DETAIL:
        speeds = leaves(rows, ["summaryDTO", "averageSpeed"])
        result["pace_derivable_from_speed"] = any(
            state(v, "number") == "present" and v > 0 for v in speeds
        )
        result["fit_format_declared"] = any(
            isinstance(v, str) and v.lower() == "fit"
            for v in leaves(rows, "metadataDTO.fileFormat.formatKey".split("."))
        )
    if endpoint is Endpoint.HEART:
        result["reading_states"] = series_readings(
            rows, "heartRateValues", "heartRateValueDescriptors", "key", "index", "heartrate"
        )
    if endpoint is Endpoint.BATTERY:
        result["reading_states"] = series_readings(
            rows,
            "bodyBatteryValuesArray",
            "bodyBatteryValueDescriptorDTOList",
            "bodyBatteryValueDescriptorKey",
            "bodyBatteryValueDescriptorIndex",
            "bodyBatteryLevel",
        )
    if endpoint is Endpoint.WEIGHT:
        # Exploratory names only. DateWeightDTO specifies no originating app or device.
        result["undocumented_source_fields"] = {
            key: {
                "nonempty": sum(isinstance(row.get(key), str) and bool(row[key]) for row in rows),
                "renpho_marker": sum(
                    isinstance(row.get(key), str)
                    and row[key].casefold() in {"renpho", "renpho health"}
                    for row in rows
                ),
            }
            for key in ("source", "sourceName", "deviceName")
        }
    if endpoint is Endpoint.FOOD:
        result["myfitnesspal_markers"] = {
            path: sum(
                isinstance(v, str) and v.lower() in ("myfitnesspal", "my_fitness_pal", "mfp")
                for v in leaves(rows, path.split("."))
            )
            for path in SCHEMA[endpoint]["text"].split()
        }
    return result


# Daily endpoint envelopes have different calendar fields. Trust only a matching date.
DATE_FIELDS = {
    Endpoint.DAILY: "calendarDate",
    Endpoint.HRV: "hrvSummary.calendarDate",
    Endpoint.SLEEP: "calendarDate",
    Endpoint.HEART: "calendarDate",
    Endpoint.BATTERY: "date",
    Endpoint.FOOD: "mealDate",
    Endpoint.WEIGHT: "calendarDate",
}


def date_evidence(rows: list[dict[str, Any]], path: str, day: str) -> dict[str, int]:
    evidence: Counter[str] = Counter()
    for value in leaves(rows, path.split(".")):
        # DailyHeartRateDTO also permits a ConnectDate wrapper.
        if path == "calendarDate" and isinstance(value, dict):
            value = value.get("date")
        if not isinstance(value, str):
            evidence["unknown"] += 1
        elif value == day or value.startswith(day + "T"):
            evidence["matched"] += 1
        else:
            evidence["mismatch"] += 1
    return evidence


FATAL = {
    "rate_limited",
    "unauthorized",
    "token_exchange_failed",
    "invalid_token_response",
    "budget_exhausted",
    "transport_error",
}


class Probe:
    def __init__(self, client: GarminClient) -> None:
        self.client = client
        self.partial = False

    def sample(
        self, out: dict[str, Any], endpoint: Endpoint, **kwargs: Any
    ) -> list[dict[str, Any]]:
        name = endpoint.name.lower()
        try:
            data = self.client.read(endpoint, **kwargs)
            if endpoint is Endpoint.ORIGINAL:
                out[name] = {"status": "archive_headers_received"}
                return []
            rows = records(endpoint, data)
            out[name] = summarize(endpoint, rows)
            if endpoint in DATE_FIELDS:
                query = kwargs.get("params", {})
                day = (
                    kwargs.get("day")
                    or query.get("calendarDate")
                    or query.get("date")
                    or query["startDate"]
                )
                dates = date_evidence(rows, DATE_FIELDS[endpoint], day)
                out[name]["record_dates"] = dates
                if dates.get("mismatch"):
                    out[name]["status"] = "date_mismatch"
            if out[name]["status"] != "ok":
                self.partial = True
            return rows
        except GarminError as exc:
            out[name] = {"status": str(exc)}
            if str(exc) in FATAL:
                raise
            if str(exc) != "no_content":
                self.partial = True
            return []

    def activities(self, out: dict[str, Any], day: date) -> None:
        endpoint = Endpoint.ACTIVITIES
        start = day - timedelta(days=6)
        pages: list[dict[str, Any]] = []
        out["activity_pages"] = pages
        items: list[dict[str, Any]] = []
        seen: set[int] = set()
        for offset in (0, 3):
            page: dict[str, Any] = {}
            pages.append(page)
            rows = self.sample(
                page,
                endpoint,
                params={
                    "startDate": start.isoformat(),
                    "endDate": day.isoformat(),
                    "start": offset,
                    "limit": 3,
                },
            )
            for row in rows:
                ident = row.get("activityId")
                local = row.get("startTimeLocal")
                try:
                    within = (
                        isinstance(local, str) and start <= date.fromisoformat(local[:10]) <= day
                    )
                except ValueError:
                    within = False
                if (
                    len(rows) > 3
                    or type(ident) is not int
                    or not 0 < ident < 2**63
                    or ident in seen
                    or not within
                ):
                    page["activities"] = {"status": "invalid_activity_page"}
                    self.partial = True
                    return
                seen.add(ident)
            items.extend(rows)
            if len(rows) < 3:
                break
        if items:
            # Prefer a run for pace inputs while leaving other sports visible in the page summaries.
            chosen = next(
                (
                    row
                    for row in items
                    if any(
                        isinstance(k, str) and (k == "running" or k.endswith("_running"))
                        for k in leaves(row, ["activityType", "typeKey"])
                    )
                ),
                items[0],
            )
            out["selected_sport_keys"] = summarize(endpoint, [chosen])["sport_keys_in_sample"]
            ident = chosen["activityId"]
            details = self.sample(out, Endpoint.DETAIL, activity_id=ident)
            if details and (
                type(details[0].get("activityId")) is not int or details[0]["activityId"] != ident
            ):
                out["detail"] = {"status": "activity_id_mismatch"}
                self.partial = True
                return
            self.sample(out, Endpoint.WORKOUTS, activity_id=ident)
            self.sample(out, Endpoint.ORIGINAL, activity_id=ident)

    def run(self, recent: date, older: date) -> dict[str, Any]:
        report: dict[str, Any] = {"current": {}}
        try:
            self.sample(report["current"], Endpoint.TYPES)
            self.sample(report["current"], Endpoint.ZONES, params={"generateDefaults": "false"})
            for label, anchor in (("recent", recent), ("older", older)):
                out: dict[str, Any] = {}
                report[label] = out
                self.activities(out, anchor)
                day = anchor.isoformat()
                self.sample(out, Endpoint.DAILY, params={"calendarDate": day})
                self.sample(out, Endpoint.HRV, day=day)
                self.sample(out, Endpoint.SLEEP, params={"date": day})
                self.sample(out, Endpoint.HEART, params={"date": day})
                self.sample(
                    out, Endpoint.BATTERY, params={"startDate": day, "endDate": day, "chunks": 1}
                )
                self.sample(
                    out,
                    Endpoint.FOOD,
                    day=day,
                    params={
                        "includeNutrition": "true",
                        "includeGoals": "false",
                        "includeMedia": "false",
                    },
                )
                self.sample(out, Endpoint.WEIGHT, day=day)
        except GarminError as exc:
            report["stopped"] = str(exc)
            if isinstance(exc, TokenExchangeError):
                report["token_http_status"] = exc.http_status
            self.partial = True
        report["requests"] = self.client.requests
        report["status"] = "partial" if self.partial else "complete"
        return report

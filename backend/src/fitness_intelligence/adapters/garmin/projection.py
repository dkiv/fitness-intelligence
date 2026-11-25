"""Allowlisted replay inputs. Identity comes from the verified account and reference."""

import re
from decimal import Decimal
from typing import Any

from fitness_intelligence.db.models import ExternalReference
from fitness_intelligence.domain.endurance import Activity

from .mapping import GarminBinding, MappingError, Row, WorkoutResponse, map_activity, obj, rows

VERSION = "garmin-personal-b3.1-v1"


def category(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,95}", value):
        raise MappingError("unsupported category encoding")
    return value


def number(value: object) -> int | dict[str, str]:
    if type(value) is int:
        return value
    if isinstance(value, Decimal) and value.is_finite():
        # JSONB/JSON serializers must not round through a binary float.
        return {"decimal": str(value)}
    raise MappingError("invalid projection quantity")


def fields(row: Row, numbers: str, categories: str = "") -> dict[str, Any]:
    projected = {key: number(row[key]) for key in numbers.split() if row.get(key) is not None}
    projected.update(
        {key: category(row[key]) for key in categories.split() if row.get(key) is not None}
    )
    return projected


def activity_inputs(
    item: Activity, summary: Row, detail: Row, workouts: WorkoutResponse | None
) -> dict[str, Any]:
    # map_activity has validated both named timestamps at each level. Preserve original precision.
    detail_summary = obj(detail["summaryDTO"]) if detail.get("summaryDTO") is not None else {}
    listing = fields(summary, "beginTimestamp")
    detail_values: dict[str, Any] = {}
    for original, result in ((summary, listing), (detail_summary, detail_values)):
        for key in ("startTimeLocal", "startTimeGMT"):
            if original.get(key) is not None:
                result[key] = original[key]
    for _, path in item.measurement_sources:
        key = path.rsplit(".", 1)[1]
        if path.startswith("SummarizedActivityDTO."):
            listing[key] = number(summary[key])
        else:
            detail_values[key] = number(detail_summary[key])
    projected_detail: dict[str, Any] = {"summaryDTO": detail_values}
    for row, target, field in (
        (summary, listing, "activityType"),
        (detail, projected_detail, "activityTypeDTO"),
    ):
        if row.get(field) is not None:
            target[field] = fields(obj(row[field]), "", "typeKey")
    if item.splits is not None:
        row, target = (
            (detail, projected_detail)
            if detail.get("splitSummaries") is not None
            else (summary, listing)
        )
        target["splitSummaries"] = [
            fields(split, "noOfSplits distance duration averageSpeed", "splitType")
            for split in rows(row["splitSummaries"])
        ]
    projection: dict[str, Any] = {"search": listing, "detail": projected_detail}
    if workouts is not None and item.steps is not None:
        groups = []
        for group in rows(workouts.payload):
            entry = fields(group, "index", "sport")
            entry["steps"] = [
                fields(
                    step,
                    "stepIndex durationValue targetValue targetValueLow targetValueHigh",
                    "intensity durationType targetType",
                )
                for step in rows(group["steps"])
            ]
            groups.append(entry)
        projection["workouts"] = groups
    return projection


def replay_activity(binding: GarminBinding, reference: ExternalReference) -> Activity:
    """Remap the latest accepted retrieval from its bound workout reference."""
    source = binding.source
    if (
        reference.user_id != source.owner_id
        or reference.provider != source.provider
        or reference.source_account_id != source.source_account_id
        or reference.entity_type != "workout"
        or (reference.sync_metadata or {}).get("mapping_version") != VERSION
        or not re.fullmatch(r"[1-9][0-9]{0,18}", reference.external_id)
    ):
        raise MappingError("invalid replay reference")
    activity_id = int(reference.external_id)
    projection = reference.raw_payload["source"]

    def restore(value: Any) -> Any:
        if isinstance(value, dict):
            if set(value) == {"decimal"}:
                return Decimal(value["decimal"])
            return {key: restore(child) for key, child in value.items()}
        if isinstance(value, list):
            return [restore(child) for child in value]
        return value

    listing = restore(projection["search"]) | {
        "activityId": activity_id,
        "ownerId": binding.profile_id,
    }
    detail = restore(projection["detail"]) | {
        "activityId": activity_id,
        "userProfileId": binding.profile_id,
    }
    workouts = (
        WorkoutResponse(binding.source, activity_id, restore(projection["workouts"]))
        if "workouts" in projection
        else None
    )
    return map_activity(binding, listing, detail=detail, workouts=workouts)

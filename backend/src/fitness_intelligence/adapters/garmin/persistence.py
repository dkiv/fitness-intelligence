"""Persist validated page/day snapshots in the caller's locked transaction."""

from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from fitness_intelligence.db.endurance_models import (
    ActivitySplit,
    ActivityStep,
    DailyRecoveryObservation,
    EnduranceActivity,
)
from fitness_intelligence.db.models import ExternalReference, Workout
from fitness_intelligence.domain.endurance import Activity, DailyObservation

from .client import GarminError
from .projection import VERSION


@dataclass(frozen=True, repr=False)
class Snapshot:
    activity: Activity
    updated: datetime | None
    split_source: str | None
    replay_inputs: dict[str, Any]


def child_values(item: Activity) -> dict[str, list[dict[str, Any]]]:
    collections = {}
    if item.splits is not None:
        collections["splits"] = [dict(position=i, **asdict(s)) for i, s in enumerate(item.splits)]
    if item.steps is not None:
        collections["steps"] = [asdict(s) for s in item.steps]
    return collections


def ambiguous_children(name: str, prior: list[dict], current: list[dict]) -> bool:
    """A sparse child in a nonempty reply cannot erase previously populated columns."""
    keys = ("position", "kind") if name == "splits" else ("workout_index", "step_index")
    previous = {tuple(row[k] for k in keys): row for row in prior}
    for row in current:
        old = previous.get(tuple(row[k] for k in keys), {})
        # A positively changed step instruction can legitimately have different units/fields.
        same_instruction = all(
            old.get(k) == row.get(k) or row.get(k) is None for k in ("duration_type", "target_type")
        )
        if same_instruction and any(
            value is None and old.get(k) is not None for k, value in row.items()
        ):
            return True
    return False


def merged_start(
    item: Activity, previous: dict[str, Any], same_version: bool
) -> tuple[datetime, int]:
    if not previous:
        return item.started_at, item.start_resolution_us
    old_start = datetime.fromisoformat(previous["started_at"])
    old_resolution = previous["start_resolution_us"]
    common = max(old_resolution, item.start_resolution_us)

    def rounded(instant: datetime) -> datetime:
        return instant.replace(microsecond=instant.microsecond // common * common)

    if rounded(old_start) == rounded(item.started_at):
        if old_resolution < item.start_resolution_us:
            return old_start, old_resolution
    elif same_version:
        raise GarminError("conflicting activity version")
    return item.started_at, item.start_resolution_us


def store_children(
    session: Session,
    snapshot: Snapshot,
    workout: Workout,
    projection: dict[str, Any],
    provenance: dict[str, Any],
    retrieved: datetime,
    same_version: bool,
) -> bool:
    complete = True
    for name, children in child_values(snapshot.activity).items():
        canonical = [
            {k: str(v) if isinstance(v, Decimal) else v for k, v in row.items()} for row in children
        ]
        prior = projection.get(name)
        if prior and ambiguous_children(name, prior, canonical):
            complete = False
            continue
        if prior != canonical:
            if (
                same_version
                and prior is not None
                and (
                    len(prior) != len(canonical)
                    or any(
                        value is not None and new[key] != value
                        for old, new in zip(prior, canonical, strict=True)
                        for key, value in old.items()
                    )
                )
            ):
                raise GarminError("conflicting activity version")
            model = ActivitySplit if name == "splits" else ActivityStep
            session.execute(
                delete(model).where(
                    model.user_id == workout.user_id, model.workout_id == workout.id
                )
            )
            session.add_all(
                model(user_id=workout.user_id, workout_id=workout.id, **row) for row in children
            )
        projection[name] = canonical
        provenance[name] = {
            "source": snapshot.split_source if name == "splits" else "ActivityWorkoutDTO.steps",
            "retrieved_at": retrieved.isoformat(),
            "source_updated_at": snapshot.updated.isoformat() if snapshot.updated else None,
        }
    return complete


def save_activity(session: Session, snapshot: Snapshot, retrieved: datetime) -> str:
    item = snapshot.activity
    source = item.source
    ref = session.scalar(
        select(ExternalReference).filter_by(
            user_id=source.owner_id,
            provider=source.provider,
            source_account_id=source.source_account_id,
            entity_type="workout",
            external_id=item.external_id,
        )
    )
    creating = ref is None
    if ref is None:
        workout = Workout(
            user_id=source.owner_id, title="Garmin activity", started_at=item.started_at
        )
        session.add(workout)
        session.flush()
        ref = ExternalReference(
            user_id=source.owner_id,
            provider=source.provider,
            source_account_id=source.source_account_id,
            entity_type="workout",
            external_id=item.external_id,
            workout_id=workout.id,
            raw_payload={},
            first_imported_at=retrieved,
        )
        session.add(ref)
        session.flush()
        activity = EnduranceActivity(
            user_id=source.owner_id,
            workout_id=workout.id,
            reference_id=ref.id,
            local_date=item.local_date,
            sport=item.sport,
        )
        session.add(activity)
    else:
        if ref.source_updated_at and (
            snapshot.updated is None or snapshot.updated < ref.source_updated_at
        ):
            return "unresolved" if snapshot.updated is None else "older"
        workout = session.scalars(
            select(Workout).filter_by(user_id=source.owner_id, id=ref.workout_id)
        ).one()
        activity = session.scalars(
            select(EnduranceActivity).filter_by(
                user_id=source.owner_id, workout_id=workout.id, reference_id=ref.id
            )
        ).one()
        other = session.scalar(
            select(ExternalReference.id)
            .where(
                ExternalReference.user_id == source.owner_id,
                ExternalReference.workout_id == workout.id,
                ExternalReference.id != ref.id,
            )
            .limit(1)
        )
        if other or workout.deleted_at or ref.source_deleted_at:
            raise GarminError("shared or inactive workout")
        if (ref.sync_metadata or {}).get("mapping_version") != VERSION:
            raise GarminError("unknown stored projection")

    projection = dict(ref.raw_payload.get("canonical", {}))
    previous = dict(projection)
    provenance = dict((ref.sync_metadata or {}).get("fields", {}))
    same_version = snapshot.updated is not None and snapshot.updated == ref.source_updated_at
    started, resolution = merged_start(item, previous, same_version)
    projection.update(
        started_at=started.isoformat(),
        start_resolution_us=resolution,
        local_date=item.local_date.isoformat(),
    )
    workout.started_at, activity.local_date = started, item.local_date
    if creating or item.subtype is not None:
        activity.sport, activity.subtype = item.sport, item.subtype
        projection.update(sport=item.sport, subtype=item.subtype)
    for field, path in item.measurement_sources:
        value = getattr(item, field)
        setattr(activity, field, value)
        projection[field] = str(value)
        provenance[field] = {
            "source": path,
            "retrieved_at": retrieved.isoformat(),
            "source_updated_at": snapshot.updated.isoformat() if snapshot.updated else None,
        }

    if same_version and any(
        value is not None and projection[key] != value
        for key, value in previous.items()
        if key not in {"start_resolution_us", "started_at", "sport"}
    ):
        raise GarminError("conflicting activity version")
    session.flush()
    complete = store_children(
        session, snapshot, workout, projection, provenance, retrieved, same_version
    )
    changed = projection != previous or ref.source_updated_at != snapshot.updated
    ref.raw_payload = {"canonical": projection, "source": snapshot.replay_inputs}
    ref.sync_metadata = {"mapping_version": VERSION, "fields": provenance}
    ref.source_updated_at, ref.last_synced_at = snapshot.updated, retrieved
    if not complete:
        return "partial"
    if creating:
        return "created"
    return "updated" if changed else "unchanged"


def save_observation(session: Session, obs: DailyObservation, retrieved: datetime) -> str:
    key = dict(
        user_id=obs.source.owner_id,
        provider=obs.source.provider,
        source_account_id=obs.source.source_account_id,
        local_date=obs.local_date,
        metric=obs.metric.value,
    )
    row = session.scalar(select(DailyRecoveryObservation).filter_by(**key))
    if row is None:
        row = DailyRecoveryObservation(**key)
        session.add(row)
        result = "created"
    else:
        result = "unchanged"
    start, end = obs.window_start, obs.window_end
    if start is None and end is None:
        start, end = row.window_start, row.window_end
    elif start == row.window_start and end is None:
        end = row.window_end
    elif end == row.window_end and start is None:
        start = row.window_start
    values = dict(
        value=obs.value,
        unit=obs.unit,
        method=obs.method,
        window_start=start,
        window_end=end,
        source_field=obs.source_field,
        mapping_version=VERSION,
    )
    if result == "unchanged" and any(getattr(row, k) != v for k, v in values.items()):
        result = "updated"
    for key_name, value in values.items():
        setattr(row, key_name, value)
    row.retrieved_at = retrieved
    return result

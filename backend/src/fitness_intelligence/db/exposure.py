"""Select active, owner/account scoped evidence from the report's existing transaction."""

from collections import defaultdict
from collections.abc import Mapping
from datetime import date
from uuid import UUID

from sqlalchemy import Text, and_, func, select
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.orm import Session
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.selectable import ScalarSelect

from fitness_intelligence.analytics.exposure import (
    RECOVERY_CATEGORIES,
    FieldProvenance,
    Outing,
    RecoveryCell,
    RecoveryExposure,
)
from fitness_intelligence.analytics.longitudinal import (
    Coverage,
    Issue,
    ObservationId,
    RecoveryObservation,
)
from fitness_intelligence.analytics.strength import Period
from fitness_intelligence.db.endurance_models import (
    ActivitySplit,
    ActivityStep,
    DailyRecoveryObservation,
    EnduranceActivity,
)
from fitness_intelligence.db.models import ExternalReference, Workout
from fitness_intelligence.domain.endurance import DailyMetric, Source


def read_outings(
    db: Session,
    source: Source,
    period: Period,
    issues: Mapping[tuple[UUID, str, date], list[Issue]],
) -> dict[date, list[Outing]]:
    activity, ref = EnduranceActivity, ExternalReference

    def child_evidence(
        model: type[ActivitySplit | ActivityStep], key: ColumnElement, *order: ColumnElement
    ) -> ScalarSelect:
        # Aggregate each collection independently to avoid multiplying split and step rows.
        content = func.to_jsonb(model.__table__.table_valued()).cast(Text)
        digest = func.encode(func.sha256(func.convert_to(content, "UTF8")), "hex")
        row = func.jsonb_build_array(key, digest)
        return (
            select(func.jsonb_agg(aggregate_order_by(row, *order)))
            .select_from(model)
            .where(model.user_id == source.owner_id, model.workout_id == activity.workout_id)
            .correlate(activity)
            .scalar_subquery()
        )

    stmt = (
        select(
            activity,
            Workout.started_at,
            ref.id,
            ref.external_id,
            ref.last_synced_at,
            ref.source_updated_at,
            ref.sync_metadata,
            child_evidence(ActivitySplit, ActivitySplit.position, ActivitySplit.position),
            child_evidence(
                ActivityStep,
                func.jsonb_build_array(ActivityStep.workout_index, ActivityStep.step_index),
                ActivityStep.workout_index,
                ActivityStep.step_index,
            ),
        )
        .select_from(activity)
        .join(Workout, and_(Workout.user_id == source.owner_id, Workout.id == activity.workout_id))
        .join(
            ref,
            and_(
                ref.user_id == source.owner_id,
                ref.id == activity.reference_id,
                ref.workout_id == activity.workout_id,
            ),
        )
        .where(
            activity.user_id == source.owner_id,
            activity.local_date >= period.start,
            activity.local_date < period.stop,
            ref.provider == source.provider,
            ref.source_account_id == source.source_account_id,
            ref.entity_type == "workout",
            Workout.deleted_at.is_(None),
            ref.source_deleted_at.is_(None),
        )
        .order_by(activity.local_date, Workout.started_at, activity.workout_id)
    )
    result = defaultdict(list)
    for a, start, ident, external, retrieved, revision, metadata, splits, steps in db.execute(stmt):
        meta = metadata or {}
        fields = meta.get("fields", {})

        def applicable(category: str) -> tuple[Issue, ...]:
            entries = issues.get((source.source_account_id, category, a.local_date), ())
            return tuple(i for i in entries if i.subject == external or not i.subject.isdecimal())

        result[a.local_date].append(
            Outing(
                source=source,
                workout_id=a.workout_id,
                reference_id=ident,
                external_id=external,
                started_at=start,
                provider_date=a.local_date,
                report_date=start.astimezone(period.zone).date(),
                sport=a.sport,
                subtype=a.subtype,
                distance_m=a.distance_m,
                duration_s=a.duration_s,
                moving_s=a.moving_s,
                elapsed_s=a.elapsed_s,
                average_speed_mps=a.average_speed_mps,
                retrieved_at=retrieved,
                source_updated_at=revision,
                mapping_version=meta.get("mapping_version"),
                fields=tuple(
                    FieldProvenance(
                        k, v.get("source"), v.get("retrieved_at"), v.get("source_updated_at")
                    )
                    for k, v in sorted(fields.items())
                    if isinstance(v, dict)
                ),
                split_positions=tuple(key for key, _ in splits or ())
                if splits or "splits" in fields
                else None,
                split_content_digests=tuple(digest for _, digest in splits or ()),
                instruction_content_digests=tuple(digest for _, digest in steps or ()),
                instruction_positions=tuple(tuple(key) for key, _ in (steps or ()))
                if steps or "steps" in fields
                else None,
                activity_issues=applicable("activities"),
                instruction_issues=applicable("running_steps"),
            )
        )
    return result


def recovery_fact(
    row: DailyRecoveryObservation, source: Source, aligned: bool
) -> RecoveryObservation:
    return RecoveryObservation(
        identity=ObservationId(source, "daily_recovery", row.id),
        provider_date=row.local_date,
        report_date=row.local_date if aligned else None,
        occurred_at=None,
        retrieved_at=row.retrieved_at,
        recorded_at=None,
        value=row.value,
        unit=row.unit,
        method=row.method,
        source_field=row.source_field,
        mapping_version=row.mapping_version,
        upstream_writer=None,
        component=row.metric,
        window_start=row.window_start,
        window_end=row.window_end,
    )


def recovery_day(
    rows: Mapping[str, DailyRecoveryObservation], coverage: Mapping[str, Coverage], aligned: bool
) -> RecoveryExposure:
    cells = []
    for metric, category in RECOVERY_CATEGORIES.items():
        c = coverage[category]
        row = rows.get(metric)
        fact = recovery_fact(row, c.source, aligned) if row is not None else None
        reasons = {
            i.reason
            for i in c.issues
            if i.subject == metric or i.subject not in RECOVERY_CATEGORIES
        }
        if fact is None:
            status = "missing"
            reasons.update(("no_metric_observation", c.status))
        elif reasons:
            status = "withheld"
        elif metric in (DailyMetric.OVERNIGHT_HRV, DailyMetric.WEEKLY_HRV):
            status = "source_only"
            reasons.add(
                "source_unit_unverified"
                if fact.unit == "source_unit_unverified"
                else "hrv_source_only"
            )
        elif not (fact.mapping_version and fact.source_field):
            status = "source_only"
            reasons.add("comparability_unverified")
        else:
            status = "eligible"
        cells.append(RecoveryCell(c.provider_date, metric, fact, status, tuple(sorted(reasons))))
    return RecoveryExposure(tuple(coverage.values()), tuple(cells))

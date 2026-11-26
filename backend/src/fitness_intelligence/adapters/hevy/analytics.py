"""Read-only historical strength profile for one trusted owner's Hevy account."""

from dataclasses import dataclass
from decimal import Decimal
from itertools import groupby
from operator import itemgetter
from uuid import UUID

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session, aliased

from fitness_intelligence.analytics.strength import (
    ExerciseSeries,
    Observation,
    Period,
    StrengthFact,
    StrengthReport,
    analyze_strength,
)
from fitness_intelligence.db.models import ExternalReference, Workout, WorkoutExercise
from fitness_intelligence.db.strength_analytics import active_strength_statement
from fitness_intelligence.domain.endurance import Source


@dataclass(frozen=True)
class HevyHistoryProfile:
    source_account_id: UUID
    external_load_templates: frozenset[str] = frozenset()
    lower_body_templates: frozenset[str] = frozenset()
    non_lower_body_templates: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        for templates in (
            self.external_load_templates,
            self.lower_body_templates,
            self.non_lower_body_templates,
        ):
            if not isinstance(templates, frozenset) or not all(
                isinstance(key, str) and key.strip() for key in templates
            ):
                raise ValueError("template classifications require a frozenset of nonblank IDs")
        if self.lower_body_templates & self.non_lower_body_templates:
            raise ValueError("contradictory lower-body classification")


def _template_series(
    profile: HevyHistoryProfile, occurrences: dict[int, tuple[UUID, object, object]]
) -> dict[UUID, ExerciseSeries]:
    # The importer writes the sorted projection and dense canonical positions atomically.
    previous_index = -1
    mapped = {}
    for expected, (position, (exercise_id, index, template)) in enumerate(occurrences.items()):
        if position != expected or type(index) is not int or index <= previous_index:
            return {}
        previous_index = index
        if isinstance(template, str) and template.strip():
            mapped[exercise_id] = ExerciseSeries(
                f"hevy:{profile.source_account_id}:{template}",
                external_load=template in profile.external_load_templates,
                template_id=template,
            )
    return mapped


def read_hevy_facts(
    session: Session, *, owner_id: UUID, period: Period, profile: HevyHistoryProfile
) -> tuple[StrengthFact, ...]:
    ref = ExternalReference
    other = aliased(ExternalReference)
    shared = (
        select(other.id)
        .where(other.user_id == owner_id, other.workout_id == Workout.id, other.id != ref.id)
        .correlate(Workout, ref)
        .exists()
    )
    exercises = ref.raw_payload["exercises"]
    entry = exercises[WorkoutExercise.position]
    length = case((func.json_typeof(exercises) == "array", func.json_array_length(exercises)))
    base = active_strength_statement(owner_id, period)
    observation_columns = base.selected_columns.keys()
    statement = (
        base.join(ref, and_(ref.user_id == owner_id, ref.workout_id == Workout.id))
        .where(
            ref.provider == "hevy",
            ref.source_account_id == profile.source_account_id,
            ref.source_deleted_at.is_(None),
            ~shared,
        )
        .add_columns(
            ref.id.label("reference_id"),
            ref.external_id,
            ref.last_synced_at,
            ref.source_updated_at,
            ref.sync_metadata["adapter"].as_string().label("adapter"),
            ref.sync_metadata["content_hash"].as_string().label("content_hash"),
            ref.sync_metadata["hash_contract"].as_string().label("hash_contract"),
            length.label("length"),
            entry["index"].label("source_index"),
            entry["exercise_template_id"].label("template"),
            and_(
                ref.sync_metadata["adapter"].as_string() == "hevy-importer-v1",
                ref.sync_metadata["hash_contract"].as_string() == "hevy-semantic-v2",
                ref.raw_payload["id"].as_string() == ref.external_id,
            ).label("recognized"),
        )
        .order_by(
            Workout.started_at,
            Workout.id,
            WorkoutExercise.position,
            base.selected_columns.set_position,
            base.selected_columns.set_id,
        )
    )
    source = Source(owner_id, "hevy", profile.source_account_id)
    facts = []
    for _, grouped in groupby(session.execute(statement).mappings(), key=itemgetter("workout_id")):
        rows = list(grouped)
        day = rows[0].started_at.astimezone(period.zone).date()
        if not period.start <= day < period.stop:
            continue
        occurrences = {
            r.exercise_position: (r.exercise_id, r.source_index, r.template)
            for r in rows
            if r.recognized and r.exercise_id is not None
        }
        series = (
            _template_series(profile, occurrences) if len(occurrences) == rows[0].length else {}
        )
        for row in rows:
            movement = series.get(row.exercise_id)
            lower_body = None
            if movement and movement.template_id in profile.lower_body_templates:
                lower_body = True
            elif movement and movement.template_id in profile.non_lower_body_templates:
                lower_body = False
            facts.append(
                StrengthFact(
                    source=source,
                    report_date=day,
                    row=Observation(**{k: row[k] for k in observation_columns}),
                    series=movement,
                    reference_id=row.reference_id,
                    external_id=row.external_id,
                    retrieved_at=row.last_synced_at,
                    source_updated_at=row.source_updated_at,
                    mapping_version=row.adapter,
                    content_hash=row.content_hash,
                    hash_contract=row.hash_contract,
                    lower_body=lower_body,
                )
            )
    return tuple(facts)


def query_hevy_history(
    session: Session,
    *,
    owner_id: UUID,
    period: Period,
    profile: HevyHistoryProfile,
    rpe_range: tuple[Decimal, Decimal] | None = None,
    top_only: bool = True,
) -> StrengthReport:
    """Infer eligible completions and group comparable movements within this source account."""
    facts = read_hevy_facts(session, owner_id=owner_id, period=period, profile=profile)
    series = {f.row.exercise_id: f.series for f in facts if f.row.exercise_id and f.series}
    return analyze_strength(
        (f.row for f in facts),
        period,
        series=series,
        infer_completion=True,
        rpe_range=rpe_range,
        top_only=top_only,
    )

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
    StrengthReport,
    analyze_strength,
)
from fitness_intelligence.db.models import ExternalReference, Workout, WorkoutExercise
from fitness_intelligence.db.strength_analytics import active_strength_statement


@dataclass(frozen=True)
class HevyHistoryProfile:
    source_account_id: UUID
    external_load_templates: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.external_load_templates, frozenset) or not all(
            isinstance(key, str) and key.strip() for key in self.external_load_templates
        ):
            raise ValueError("external_load_templates must be a frozenset of nonblank template IDs")


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
            )
    return mapped


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
            WorkoutExercise.position,
            length.label("length"),
            entry["index"].label("source_index"),
            entry["exercise_template_id"].label("template"),
            and_(
                ref.sync_metadata["adapter"].as_string() == "hevy-importer-v1",
                ref.sync_metadata["hash_contract"].as_string() == "hevy-semantic-v2",
                ref.raw_payload["id"].as_string() == ref.external_id,
            ).label("recognized"),
        )
        .order_by(Workout.id, WorkoutExercise.position)
    )
    observations = []
    series: dict[UUID, ExerciseSeries] = {}

    for _, workout_rows in groupby(
        session.execute(statement).mappings(), key=itemgetter("workout_id")
    ):
        occurrences = {}
        projected_count = None
        for row in workout_rows:
            if not period.start <= row.started_at.astimezone(period.zone).date() < period.stop:
                continue
            observations.append(Observation(**{key: row[key] for key in observation_columns}))
            if row.recognized and row.exercise_id is not None:
                projected_count = row.length
                occurrences[row.position] = (row.exercise_id, row.source_index, row.template)
        if not occurrences or len(occurrences) != projected_count:
            continue
        series.update(_template_series(profile, occurrences))
    return analyze_strength(
        observations,
        period,
        series=series,
        infer_completion=True,
        rpe_range=rpe_range,
        top_only=top_only,
    )

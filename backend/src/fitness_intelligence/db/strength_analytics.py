"""Internal read model. The calling application must resolve ownership before querying."""

from collections.abc import Iterator, Mapping
from datetime import UTC, datetime, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, and_, select
from sqlalchemy.orm import Session

from fitness_intelligence.analytics.strength import (
    DAY,
    ExerciseSeries,
    Observation,
    Period,
    StrengthReport,
    analyze_strength,
)
from fitness_intelligence.db.endurance_models import EnduranceActivity
from fitness_intelligence.db.models import ExerciseSet, ExternalReference, Workout, WorkoutExercise


def active_strength_statement(owner_id: UUID, period: Period) -> Select:
    """Base projection, including a UTC envelope around the requested local dates."""
    refs = (
        select(ExternalReference.id)
        .where(ExternalReference.user_id == owner_id, ExternalReference.workout_id == Workout.id)
        .correlate(Workout)
    )
    # Cover every possible local UTC offset, including days with a midnight transition.
    lower = datetime.combine(period.start, time.min, UTC) - DAY
    upper = datetime.combine(period.stop, time.min, UTC) + DAY
    return (
        select(
            Workout.id.label("workout_id"),
            Workout.started_at,
            Workout.ended_at,
            WorkoutExercise.id.label("exercise_id"),
            WorkoutExercise.name,
            WorkoutExercise.position.label("exercise_position"),
            ExerciseSet.position.label("set_position"),
            ExerciseSet.id.label("set_id"),
            ExerciseSet.kind,
            ExerciseSet.repetitions,
            ExerciseSet.weight_kg,
            ExerciseSet.rpe,
            ExerciseSet.distance_m,
            ExerciseSet.duration_seconds,
            ExerciseSet.completed_at,
        )
        .select_from(Workout)
        .outerjoin(
            WorkoutExercise,
            and_(WorkoutExercise.user_id == owner_id, WorkoutExercise.workout_id == Workout.id),
        )
        .outerjoin(
            ExerciseSet,
            and_(ExerciseSet.user_id == owner_id, ExerciseSet.exercise_id == WorkoutExercise.id),
        )
        .where(
            Workout.user_id == owner_id,
            Workout.deleted_at.is_(None),
            WorkoutExercise.id.is_not(None)
            | ~select(EnduranceActivity.workout_id)
            .where(
                EnduranceActivity.user_id == owner_id, EnduranceActivity.workout_id == Workout.id
            )
            .exists(),
            Workout.started_at >= lower,
            Workout.started_at < upper,
            ~refs.exists() | refs.where(ExternalReference.source_deleted_at.is_(None)).exists(),
        )
        .execution_options(yield_per=1000)
    )


def strength_observations(
    session: Session, *, owner_id: UUID, period: Period
) -> Iterator[Observation]:
    """Stream one owner's active canonical observations, including workouts without children."""
    for row in session.execute(active_strength_statement(owner_id, period)).mappings():
        if period.start <= row["started_at"].astimezone(period.zone).date() < period.stop:
            yield Observation(**row)


def query_strength(
    session: Session,
    *,
    owner_id: UUID,
    period: Period,
    series: Mapping[UUID, ExerciseSeries] | None = None,
    infer_completion: bool = False,
    rpe_range: tuple[Decimal, Decimal] | None = None,
    top_only: bool = True,
) -> StrengthReport:
    """Calculate all metrics from one owner-scoped statement in the caller's session."""
    return analyze_strength(
        strength_observations(session, owner_id=owner_id, period=period),
        period,
        series=series,
        infer_completion=infer_completion,
        rpe_range=rpe_range,
        top_only=top_only,
    )

"""Strength metrics on a single owner's canonical workout observations."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

import polars as pl

from fitness_intelligence.domain.endurance import Source


@dataclass(frozen=True)
class Period:
    start: date
    stop: date
    zone: ZoneInfo = ZoneInfo("UTC")

    def __post_init__(self) -> None:
        if self.stop <= self.start:
            raise ValueError("stop must follow start")


@dataclass(frozen=True)
class ExerciseSeries:
    """Explicit comparable movement key and interpretation of its recorded kilograms."""

    key: str
    external_load: bool = False
    template_id: str | None = None


@dataclass(frozen=True)
class Observation:
    """One canonical set, or one placeholder for an empty workout/exercise."""

    workout_id: UUID
    started_at: datetime
    ended_at: datetime | None
    exercise_id: UUID | None = None
    name: str | None = None
    set_id: UUID | None = None
    kind: str | None = None
    repetitions: int | None = None
    weight_kg: Decimal | None = None
    rpe: Decimal | None = None
    distance_m: Decimal | None = None
    duration_seconds: Decimal | None = None
    completed_at: datetime | None = None
    deleted: bool = False
    exercise_position: int | None = None
    set_position: int | None = None


@dataclass(frozen=True)
class StrengthReport:
    weekly_activity: pl.DataFrame
    weekly_volume: pl.DataFrame
    progression: pl.DataFrame


DAY = timedelta(days=1)
CATEGORIES = {"warmup": "warmup", "normal": "working", "drop": "working", "failure": "working"}
KG = pl.Decimal(38, 4)
SET_SCHEMA = {
    "week": pl.Date,
    "started_at": pl.Datetime("us", "UTC"),
    "workout_id": pl.String,
    "exercise_key": pl.String,
    "exercise_id": pl.String,
    "name": pl.String,
    "set_id": pl.String,
    "kind": pl.String,
    "category": pl.String,
    "completion_inferred": pl.Boolean,
    "repetitions": pl.Int64,
    "weight_kg": KG,
    "rpe": pl.Decimal(4, 2),
    "volume_load_kg": KG,
    "epley_numerator": KG,
}


def monday(day: date) -> date:
    return day - DAY * day.weekday()


def positive(value: Decimal | None) -> bool:
    return value is not None and value.is_finite() and value > 0


def completion_evidence(row: Observation, *, infer_completion: bool) -> str:
    if row.set_id is None:
        return "not_applicable"
    if row.completed_at is not None:
        return "confirmed"
    if (
        infer_completion
        and row.ended_at is not None
        and (
            (row.repetitions is not None and row.repetitions > 0)
            or positive(row.distance_m)
            or positive(row.duration_seconds)
        )
    ):
        return "inferred"
    return "unsupported"


def movement_key(exercise_id: UUID, movement: ExerciseSeries | None) -> str:
    return f"series:{movement.key}" if movement else f"occurrence:{exercise_id}"


@dataclass(frozen=True)
class StrengthFact:
    """One current, active, solely supported workout/exercise/set row (including placeholders)."""

    source: Source
    report_date: date
    row: Observation
    series: ExerciseSeries | None
    reference_id: UUID
    external_id: str
    retrieved_at: datetime
    source_updated_at: datetime | None
    mapping_version: str | None
    content_hash: str | None
    hash_contract: str | None
    lower_body: bool | None
    source_support: str = "active_sole_reference"

    @property
    def execution(self) -> str:
        return completion_evidence(self.row, infer_completion=True)

    @property
    def load_convention(self) -> str:
        return "external_kg" if self.series and self.series.external_load else "unclassified"

    @property
    def movement(self) -> str | None:
        return movement_key(self.row.exercise_id, self.series) if self.row.exercise_id else None


def measured_sum(column: str) -> pl.Expr:
    return pl.when(pl.col(column).count() > 0).then(pl.col(column).sum()).alias(column)


def analyze_strength(
    rows: Iterable[Observation],
    period: Period,
    *,
    series: Mapping[UUID, ExerciseSeries] | None = None,
    infer_completion: bool = False,
    rpe_range: tuple[Decimal, Decimal] | None = None,
    top_only: bool = True,
) -> StrengthReport:
    """Analyze unique canonical set rows. Effort and top selection affect progression only."""
    sets, workouts = _normalized_sets(rows, period, series, infer_completion, rpe_range)
    return StrengthReport(
        _weekly_activity(sets, workouts, period),
        _weekly_volume(sets),
        _progression(sets, top_only),
    )


def ranked_estimates(
    facts: Iterable[StrengthFact],
    period: Period,
    *,
    execution: Literal["confirmed", "inferred"],
    rpe_range: tuple[Decimal, Decimal] | None = None,
) -> pl.DataFrame:
    """All eligible sets of one tier in the original unrounded workout/series ranking."""
    selected = [f for f in facts if f.execution == execution]
    series = {f.row.exercise_id: f.series for f in selected if f.series is not None}
    sets, _ = _normalized_sets(
        (f.row for f in selected), period, series, execution == "inferred", rpe_range
    )
    return _progression(sets, top_only=False)


def _normalized_sets(
    rows: Iterable[Observation],
    period: Period,
    series: Mapping[UUID, ExerciseSeries] | None,
    infer_completion: bool,
    rpe_range: tuple[Decimal, Decimal] | None,
) -> tuple[pl.DataFrame, dict[UUID, date]]:
    if rpe_range is not None and not (
        all(v.is_finite() for v in rpe_range) and 0 <= rpe_range[0] <= rpe_range[1] <= 10
    ):
        raise ValueError("RPE interval must be ordered and within 0 to 10")
    workouts: dict[UUID, date] = {}
    records = []
    seen: set[UUID] = set()
    for row in rows:
        if row.started_at.utcoffset() is None:
            raise ValueError("an aware workout start is required")
        day = row.started_at.astimezone(period.zone).date()
        if row.deleted or not period.start <= day < period.stop:
            continue
        week = monday(day)
        workouts[row.workout_id] = week
        if row.exercise_id is None or row.set_id is None:
            continue
        if row.set_id in seen:
            raise ValueError("duplicate canonical set")
        seen.add(row.set_id)
        reps = row.repetitions
        if completion_evidence(row, infer_completion=infer_completion) == "unsupported":
            continue
        movement = (series or {}).get(row.exercise_id)
        key = movement_key(row.exercise_id, movement)
        category = CATEGORIES.get(row.kind, "unknown")
        weight = row.weight_kg
        known_reps = reps is not None and reps >= 0
        loaded = (
            movement is not None
            and movement.external_load
            and known_reps
            and weight is not None
            and weight.is_finite()
            and weight >= 0
            and row.distance_m in (None, 0)
            and row.duration_seconds in (None, 0)
        )
        valid_rpe = row.rpe is None or (row.rpe.is_finite() and 0 <= row.rpe <= 10)
        effort = rpe_range is None or (
            valid_rpe and row.rpe is not None and rpe_range[0] <= row.rpe <= rpe_range[1]
        )
        estimate = (
            loaded
            and weight > 0
            and 1 <= reps <= 10
            and category == "working"
            and valid_rpe
            and effort
        )
        with localcontext() as ctx:
            ctx.prec = 38
            records.append(
                (
                    week,
                    row.started_at,
                    str(row.workout_id),
                    key,
                    str(row.exercise_id),
                    row.name,
                    str(row.set_id),
                    row.kind,
                    category,
                    row.completed_at is None,
                    reps if known_reps else None,
                    weight if loaded else None,
                    row.rpe if valid_rpe else None,
                    weight * reps if loaded else None,
                    weight * (30 + reps) if estimate else None,
                )
            )
    return pl.DataFrame(records, schema=SET_SCHEMA, orient="row"), workouts


def _weekly_volume(sets: pl.DataFrame) -> pl.DataFrame:
    return (
        sets.group_by("week", "exercise_key", "category")
        .agg(
            pl.len().alias("completed_sets"),
            pl.col("completion_inferred").sum().alias("inferred_sets"),
            pl.col("workout_id").n_unique().alias("workouts"),
            pl.col("name").drop_nulls().unique().sort().alias("names"),
            pl.col("repetitions").count().alias("sets_with_reps"),
            measured_sum("repetitions"),
            pl.col("volume_load_kg").count().alias("sets_with_load"),
            measured_sum("volume_load_kg"),
        )
        .sort("week", "exercise_key", "category")
    )


def _progression(sets: pl.DataFrame, top_only: bool) -> pl.DataFrame:
    progression = sets.filter(pl.col("epley_numerator").is_not_null()).sort(
        ["started_at", "workout_id", "exercise_key", "epley_numerator", "set_id"],
        descending=[False, False, False, True, False],
    )
    if top_only:
        progression = progression.unique(["workout_id", "exercise_key"], maintain_order=True)
    with localcontext() as ctx:
        ctx.prec = 38
        estimates = [
            (n / 30).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            for n in progression["epley_numerator"]
        ]
    return progression.drop("category", "epley_numerator", "volume_load_kg").with_columns(
        pl.Series("estimated_1rm_kg", estimates, dtype=pl.Decimal(38, 2))
    )


def _weekly_activity(
    sets: pl.DataFrame, workouts: dict[UUID, date], period: Period
) -> pl.DataFrame:
    weeks = pl.date_range(monday(period.start), monday(period.stop - DAY), "1w", eager=True)
    return (
        pl.DataFrame({"week": weeks})
        .join(
            pl.Series("week", list(workouts.values()), dtype=pl.Date)
            .to_frame()
            .group_by("week")
            .len("workouts"),
            on="week",
            how="left",
        )
        .join(
            sets.group_by("week").agg(
                pl.col("exercise_key").n_unique().alias("exercises_performed"),
                pl.len().alias("completed_sets"),
                pl.col("completion_inferred").sum().alias("inferred_sets"),
            ),
            on="week",
            how="left",
        )
        .fill_null(0)
        .sort("week")
        .with_columns(pl.col("workouts").cast(pl.Int64).diff().alias("workout_change"))
    )

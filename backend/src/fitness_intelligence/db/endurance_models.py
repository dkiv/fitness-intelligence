"""Endurance measurements share the workout and its owner-scoped source reference."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .models import Base, OwnedRecord

Quantity = Annotated[Decimal, mapped_column(Numeric(22, 9))]


def nonnegative(*columns: str) -> CheckConstraint:
    # The upper bound also excludes PostgreSQL numeric NaN.
    return CheckConstraint(
        " AND ".join(
            f"({col} IS NULL OR ({col} >= 0 AND {col} < 10000000000000))" for col in columns
        ),
        name="valid_quantities",
    )


class EnduranceActivity(Base):
    __tablename__ = "endurance_activities"
    __table_args__ = (
        UniqueConstraint("user_id", "workout_id"),
        ForeignKeyConstraint(
            ["user_id", "workout_id", "reference_id"],
            [
                "external_references.user_id",
                "external_references.workout_id",
                "external_references.id",
            ],
            name="fk_endurance_workout_reference",
        ),
        CheckConstraint("length(sport) > 0", name="nonempty_sport"),
        nonnegative(
            "duration_s",
            "elapsed_s",
            "moving_s",
            "distance_m",
            "average_speed_mps",
            "average_hr_bpm",
            "max_hr_bpm",
            "elevation_gain_m",
            "elevation_loss_m",
        ),
    )
    workout_id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    reference_id: Mapped[UUID]
    local_date: Mapped[date]
    sport: Mapped[str]
    subtype: Mapped[str | None]
    duration_s: Mapped[Quantity | None]
    elapsed_s: Mapped[Quantity | None]
    moving_s: Mapped[Quantity | None]
    distance_m: Mapped[Quantity | None]
    average_speed_mps: Mapped[Quantity | None]
    average_hr_bpm: Mapped[Quantity | None]
    max_hr_bpm: Mapped[Quantity | None]
    elevation_gain_m: Mapped[Quantity | None]
    elevation_loss_m: Mapped[Quantity | None]


def activity_parent() -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["user_id", "workout_id"],
        ["endurance_activities.user_id", "endurance_activities.workout_id"],
    )


class ActivitySplit(Base):
    __tablename__ = "activity_split_summaries"
    __table_args__ = (
        activity_parent(),
        CheckConstraint(
            "position >= 0 AND (count IS NULL OR count >= 0)", name="valid_position_count"
        ),
        nonnegative("distance_m", "duration_s", "average_speed_mps"),
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    workout_id: Mapped[UUID] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str]
    count: Mapped[int | None]
    distance_m: Mapped[Quantity | None]
    duration_s: Mapped[Quantity | None]
    average_speed_mps: Mapped[Quantity | None]


class ActivityStep(Base):
    __tablename__ = "activity_performed_steps"
    __table_args__ = (
        activity_parent(),
        CheckConstraint("workout_index >= 0 AND step_index >= 0", name="positions"),
        CheckConstraint("target_zone > 0 AND repeat_count >= 0", name="counts"),
        CheckConstraint(
            "(duration_value IS NULL) = (duration_unit IS NULL)", name="duration_units"
        ),
        CheckConstraint(
            "(target_low IS NULL) = (target_high IS NULL) AND "
            "(target_low IS NULL) = (target_unit IS NULL) AND target_low <= target_high "
            "AND (target_zone IS NULL OR target_low IS NULL)",
            name="range_units",
        ),
        nonnegative("duration_value", "target_low", "target_high"),
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    workout_id: Mapped[UUID] = mapped_column(primary_key=True)
    workout_index: Mapped[int] = mapped_column(primary_key=True)
    step_index: Mapped[int] = mapped_column(primary_key=True)
    intensity: Mapped[str | None]
    duration_type: Mapped[str | None]
    duration_value: Mapped[Quantity | None]
    duration_unit: Mapped[str | None]
    target_type: Mapped[str | None]
    target_zone: Mapped[int | None]
    target_low: Mapped[Quantity | None]
    target_high: Mapped[Quantity | None]
    target_unit: Mapped[str | None]
    repeat_count: Mapped[int | None]


class DailyRecoveryObservation(OwnedRecord, Base):
    __tablename__ = "daily_recovery_observations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
        ),
        UniqueConstraint(
            "user_id",
            "provider",
            "source_account_id",
            "local_date",
            "metric",
            name="uq_recovery_account_day_metric",
        ),
        CheckConstraint("window_end >= window_start", name="window_order"),
        CheckConstraint(
            "(metric IN ('overnight_hrv','seven_day_hrv') "
            "AND unit IN ('ms','source_unit_unverified') "
            "AND method = 'reported_average') OR "
            "(metric = 'resting_hr' AND unit = 'bpm' AND method = 'reported') OR "
            "(metric IN ('sleep_duration','light_sleep','deep_sleep','rem_sleep',"
            "'awake_during_sleep') "
            "AND unit = 's' AND method = 'reported') OR "
            "(metric IN ('total_expenditure','active_expenditure','basal_expenditure') "
            "AND unit = 'kcal' AND method IN ('wearable_estimate','measured'))",
            name="metric_unit_method",
        ),
        nonnegative("value"),
    )
    provider: Mapped[str]
    source_account_id: Mapped[UUID]
    local_date: Mapped[date]
    metric: Mapped[str]
    value: Mapped[Quantity]
    unit: Mapped[str]
    method: Mapped[str]
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

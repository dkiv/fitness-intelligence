"""Owner- and account-scoped source observations for intake and body mass."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .endurance_models import Quantity
from .models import Base, OwnedRecord


def source_account() -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["user_id", "provider", "source_account_id"],
        ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
    )


class NutritionRecord(OwnedRecord):
    provider: Mapped[str]
    source_account_id: Mapped[UUID]
    local_date: Mapped[date]
    source_field: Mapped[str]
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    mapping_version: Mapped[str]
    upstream_writer: Mapped[str | None]


class DailyIntakeObservation(NutritionRecord, Base):
    __tablename__ = "daily_intake_observations"
    __table_args__ = (
        source_account(),
        UniqueConstraint(
            "user_id",
            "provider",
            "source_account_id",
            "local_date",
            "source_field",
            name="uq_intake_source_day_field",
        ),
        CheckConstraint("reported_kcal >= 0 AND reported_kcal < 10000000000000", name="valid_kcal"),
        CheckConstraint(
            "completeness IN ('unknown','partial','athlete_confirmed')", name="completeness"
        ),
    )
    reported_kcal: Mapped[Quantity]
    completeness: Mapped[str]
    # Presence flag returned with this particular observed total, when available.
    source_data_present: Mapped[bool | None]


class BodyWeightObservation(NutritionRecord, Base):
    __tablename__ = "body_weight_observations"
    __table_args__ = (
        source_account(),
        UniqueConstraint(
            "user_id",
            "provider",
            "source_account_id",
            "upstream_id",
            name="uq_weight_source_record",
        ),
        Index(
            "uq_weight_unidentified_instant",
            "user_id",
            "provider",
            "source_account_id",
            "measured_at",
            unique=True,
            postgresql_where=text("upstream_id IS NULL"),
        ),
        CheckConstraint(
            "upstream_id IS NOT NULL OR measured_at IS NOT NULL", name="weight_identity"
        ),
        CheckConstraint(
            "(measured_at IS NULL) = (time_resolution_us IS NULL) AND time_resolution_us > 0",
            name="time_precision",
        ),
        CheckConstraint(
            "mass_kg > 0 AND mass_kg < 10000000000000 "
            "AND source_value > 0 AND source_value < 10000000000000",
            name="valid_mass",
        ),
    )
    mass_kg: Mapped[Quantity]
    source_value: Mapped[Quantity]
    source_unit: Mapped[str]
    documented_source_unit: Mapped[str | None]
    measured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    time_resolution_us: Mapped[int | None]
    upstream_id: Mapped[str | None]

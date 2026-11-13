from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    MetaData,
    Numeric,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
        }
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    workouts: Mapped[list["Workout"]] = relationship(back_populates="user")
    external_references: Mapped[list["ExternalReference"]] = relationship(back_populates="user")


class OwnedRecord:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)


class Workout(OwnedRecord, Base):
    __tablename__ = "workouts"
    __table_args__ = (
        UniqueConstraint("user_id", "id"),
        CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="time_order"),
        Index("ix_workouts_user_started", "user_id", "started_at"),
    )

    title: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped["User"] = relationship(back_populates="workouts")
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout",
        order_by="WorkoutExercise.position",
        cascade="all, delete-orphan",
    )


class WorkoutExercise(OwnedRecord, Base):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("user_id", "id"),
        UniqueConstraint("user_id", "workout_id", "position", name="uq_workout_exercises_position"),
        ForeignKeyConstraint(["user_id", "workout_id"], ["workouts.user_id", "workouts.id"]),
        CheckConstraint("position >= 0", name="position_nonnegative"),
    )

    workout_id: Mapped[UUID] = mapped_column(nullable=False)
    position: Mapped[int]
    name: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    superset_group: Mapped[str | None]
    workout: Mapped[Workout] = relationship(back_populates="exercises")
    user: Mapped["User"] = relationship(overlaps="exercises,workout")
    sets: Mapped[list["ExerciseSet"]] = relationship(
        back_populates="exercise",
        order_by="ExerciseSet.position",
        cascade="all, delete-orphan",
        overlaps="user",
    )


class ExerciseSet(OwnedRecord, Base):
    __tablename__ = "exercise_sets"
    __table_args__ = (
        UniqueConstraint("user_id", "id"),
        UniqueConstraint("user_id", "exercise_id", "position", name="uq_exercise_sets_position"),
        ForeignKeyConstraint(
            ["user_id", "exercise_id"], ["workout_exercises.user_id", "workout_exercises.id"]
        ),
        CheckConstraint("position >= 0", name="position_nonnegative"),
        CheckConstraint("repetitions >= 0", name="repetitions_nonnegative"),
        CheckConstraint("weight_kg >= 0", name="weight_nonnegative"),
        CheckConstraint("distance_m >= 0", name="distance_nonnegative"),
        CheckConstraint("duration_seconds >= 0", name="duration_nonnegative"),
        CheckConstraint("rpe >= 0 AND rpe <= 10", name="rpe_range"),
    )

    exercise_id: Mapped[UUID] = mapped_column(nullable=False)
    position: Mapped[int]
    kind: Mapped[str | None]  # e.g. normal, warmup, failure, drop
    repetitions: Mapped[int | None]
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    distance_m: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    duration_seconds: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    rpe: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    source_measurements: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    exercise: Mapped[WorkoutExercise] = relationship(back_populates="sets", overlaps="user")
    user: Mapped["User"] = relationship(overlaps="exercise,sets")


class ExternalReference(OwnedRecord, Base):
    __tablename__ = "external_references"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "source_account_id", "entity_type", "external_id"),
        ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
        ),
        ForeignKeyConstraint(["user_id", "workout_id"], ["workouts.user_id", "workouts.id"]),
        ForeignKeyConstraint(
            ["user_id", "exercise_id"], ["workout_exercises.user_id", "workout_exercises.id"]
        ),
        ForeignKeyConstraint(["user_id", "set_id"], ["exercise_sets.user_id", "exercise_sets.id"]),
        CheckConstraint(
            "(entity_type = 'workout' AND workout_id IS NOT NULL "
            "AND exercise_id IS NULL AND set_id IS NULL) OR "
            "(entity_type = 'exercise' AND exercise_id IS NOT NULL "
            "AND workout_id IS NULL AND set_id IS NULL) OR "
            "(entity_type = 'set' AND set_id IS NOT NULL "
            "AND workout_id IS NULL AND exercise_id IS NULL)",
            name="target_matches_type",
        ),
        CheckConstraint(
            "length(provider) > 0 AND length(external_id) > 0", name="identity_nonempty"
        ),
        Index("ix_external_references_user_workout", "user_id", "workout_id"),
        Index("ix_external_references_user_exercise", "user_id", "exercise_id"),
        Index("ix_external_references_user_set", "user_id", "set_id"),
    )

    source_account_id: Mapped[UUID]
    provider: Mapped[str]
    entity_type: Mapped[str]
    external_id: Mapped[str]
    workout_id: Mapped[UUID | None]
    exercise_id: Mapped[UUID | None]
    set_id: Mapped[UUID | None]
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    first_imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    source_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_version: Mapped[str | None]
    sync_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    user: Mapped["User"] = relationship(back_populates="external_references")


class SourceAccount(OwnedRecord, Base):
    __tablename__ = "source_accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "id"),
        CheckConstraint("length(provider) > 0", name="provider_nonempty"),
        CheckConstraint(
            "(status = 'legacy_unresolved' AND provider_account_id IS NULL) OR "
            "(status IN ('active', 'disconnected') AND "
            "provider_account_id IS NOT NULL AND length(provider_account_id) > 0)",
            name="identity_state",
        ),
        Index(
            "uq_source_accounts_verified",
            "user_id",
            "provider",
            "provider_account_id",
            unique=True,
            postgresql_where=text("provider_account_id IS NOT NULL"),
            sqlite_where=text("provider_account_id IS NOT NULL"),
        ),
        Index(
            "uq_source_accounts_legacy",
            "user_id",
            "provider",
            unique=True,
            postgresql_where=text("provider_account_id IS NULL"),
            sqlite_where=text("provider_account_id IS NULL"),
        ),
    )
    provider: Mapped[str]
    provider_account_id: Mapped[str | None]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AccountSyncState(OwnedRecord, Base):
    __tablename__ = "account_sync_states"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "source_account_id"),
        ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
        ),
        CheckConstraint(
            "(initialized AND checkpoint IS NOT NULL) OR (NOT initialized AND checkpoint IS NULL)",
            name="checkpoint_state",
        ),
    )
    provider: Mapped[str]
    source_account_id: Mapped[UUID]
    initialized: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    checkpoint: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WorkoutTombstone(OwnedRecord, Base):
    __tablename__ = "workout_tombstones"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "source_account_id", "external_id"),
        ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
        ),
        CheckConstraint("length(external_id) > 0", name="identity_nonempty"),
    )
    provider: Mapped[str]
    source_account_id: Mapped[UUID]
    external_id: Mapped[str]
    source_deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pending: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

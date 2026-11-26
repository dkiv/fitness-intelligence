"""PostgreSQL owns approval transitions. See migration e201 for the row guards."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .models import Base, OwnedRecord

snapshot_type = JSON().with_variant(JSONB(), "postgresql")


class AthleteContext(OwnedRecord, Base):
    __tablename__ = "athlete_contexts"
    __table_args__ = (
        UniqueConstraint("user_id", "id"),
        UniqueConstraint("user_id", "sequence", name="uq_context_sequence"),
        CheckConstraint("sequence > 0", name="positive_sequence"),
    )

    sequence: Mapped[int]
    snapshot: Mapped[dict[str, Any]] = mapped_column(snapshot_type)


class TrainingPlan(OwnedRecord, Base):
    """One cycle with one fixed, versioned E1 block."""

    __tablename__ = "training_plans"
    __table_args__ = (
        UniqueConstraint("user_id", "id"),
        ForeignKeyConstraint(
            ["user_id", "id", "head_id", "head_choice"],
            [
                "plan_decisions.user_id",
                "plan_decisions.plan_id",
                "plan_decisions.revision_id",
                "plan_decisions.choice",
            ],
            name="fk_plan_approved_head",
            use_alter=True,
        ),
        CheckConstraint("head_choice = 'approve'", name="approved_only"),
    )

    block: Mapped[dict[str, Any]] = mapped_column(snapshot_type)
    head_id: Mapped[UUID | None]
    head_choice: Mapped[str] = mapped_column(server_default="approve")


class PlanRevision(OwnedRecord, Base):
    __tablename__ = "plan_revisions"
    __table_args__ = (
        UniqueConstraint("user_id", "id"),
        UniqueConstraint("user_id", "plan_id", "id", name="uq_plan_revision_lineage"),
        ForeignKeyConstraint(
            ["user_id", "plan_id"], ["training_plans.user_id", "training_plans.id"]
        ),
        ForeignKeyConstraint(
            ["user_id", "context_id"], ["athlete_contexts.user_id", "athlete_contexts.id"]
        ),
        ForeignKeyConstraint(
            ["user_id", "plan_id", "base_id"],
            ["plan_revisions.user_id", "plan_revisions.plan_id", "plan_revisions.id"],
            name="fk_revision_base",
        ),
        CheckConstraint("id <> base_id", name="distinct_base"),
    )

    plan_id: Mapped[UUID]
    context_id: Mapped[UUID]
    base_id: Mapped[UUID | None]
    rationale: Mapped[dict[str, Any] | None] = mapped_column(snapshot_type, nullable=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(snapshot_type)


class PlanDecision(OwnedRecord, Base):
    __tablename__ = "plan_decisions"
    __table_args__ = (
        UniqueConstraint("user_id", "id"),
        UniqueConstraint("user_id", "command_id", name="uq_plan_decision_command"),
        UniqueConstraint("revision_id"),
        UniqueConstraint(
            "user_id", "plan_id", "revision_id", "choice", name="uq_plan_decision_head"
        ),
        ForeignKeyConstraint(
            ["user_id", "plan_id", "revision_id"],
            ["plan_revisions.user_id", "plan_revisions.plan_id", "plan_revisions.id"],
        ),
        CheckConstraint("choice IN ('approve','decline')", name="valid_choice"),
    )

    plan_id: Mapped[UUID]
    revision_id: Mapped[UUID]
    command_id: Mapped[UUID]
    choice: Mapped[str]
    reason: Mapped[str | None]
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.clock_timestamp()
    )


class SessionOutcome(OwnedRecord, Base):
    """One immutable athlete attestation or correction for a logical calendar slot."""

    __tablename__ = "session_outcomes"
    __table_args__ = (
        UniqueConstraint("user_id", "command_id", name="uq_outcome_command"),
        UniqueConstraint("supersedes_id", name="uq_outcome_successor"),
        UniqueConstraint("user_id", "plan_id", "week", "slot", "id", name="uq_outcome_slot_id"),
        Index(
            "uq_outcome_root",
            "user_id",
            "plan_id",
            "week",
            "slot",
            unique=True,
            postgresql_where=text("supersedes_id IS NULL"),
            sqlite_where=text("supersedes_id IS NULL"),
        ),
        ForeignKeyConstraint(
            ["user_id", "plan_id", "revision_id", "choice"],
            [
                "plan_decisions.user_id",
                "plan_decisions.plan_id",
                "plan_decisions.revision_id",
                "plan_decisions.choice",
            ],
            name="fk_outcome_approval",
        ),
        ForeignKeyConstraint(["user_id", "workout_id"], ["workouts.user_id", "workouts.id"]),
        ForeignKeyConstraint(
            ["user_id", "plan_id", "week", "slot", "supersedes_id"],
            [
                "session_outcomes.user_id",
                "session_outcomes.plan_id",
                "session_outcomes.week",
                "session_outcomes.slot",
                "session_outcomes.id",
            ],
            name="fk_outcome_supersedes",
        ),
        CheckConstraint("choice = 'approve'", name="approved"),
        ForeignKeyConstraint(
            ["user_id", "plan_id", "origin_revision_id", "choice"],
            [
                "plan_decisions.user_id",
                "plan_decisions.plan_id",
                "plan_decisions.revision_id",
                "plan_decisions.choice",
            ],
            name="fk_outcome_origin_approval",
        ),
        CheckConstraint(
            "(outcome_version = 1 AND origin_revision_id IS NULL AND week IN (1, 2) AND "
            "slot IN ('first-press','second-press','short-run','long-run')) OR "
            "(outcome_version = 2 AND origin_revision_id IS NOT NULL AND week > 0 "
            "AND workout_id IS NULL)",
            name="versioned_scope",
        ),
        CheckConstraint("occurred_at <= recorded_at", name="elapsed"),
        CheckConstraint("id <> supersedes_id", name="distinct_correction"),
    )

    outcome_version: Mapped[int] = mapped_column(server_default=text("1"))
    origin_revision_id: Mapped[UUID | None]
    plan_id: Mapped[UUID]
    revision_id: Mapped[UUID]
    choice: Mapped[str] = mapped_column(server_default="approve")
    week: Mapped[int]
    slot: Mapped[str]
    command_id: Mapped[UUID]
    supersedes_id: Mapped[UUID | None]
    workout_id: Mapped[UUID | None]
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual: Mapped[dict[str, Any]] = mapped_column(snapshot_type)

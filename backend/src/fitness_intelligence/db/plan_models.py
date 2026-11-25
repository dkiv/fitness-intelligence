"""PostgreSQL owns approval transitions. See migration e201 for the row guards."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKeyConstraint, UniqueConstraint, func
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

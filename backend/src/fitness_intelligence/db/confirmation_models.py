"""Immutable scoped athlete receipts and their per-member correction edges."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from .models import Base
from .plan_models import snapshot_type


class ConfirmationReceipt(Base):
    __tablename__ = "confirmation_receipts"
    __table_args__ = (
        CheckConstraint(
            "actor = user_id AND user_id = 'c13399d0-4e41-50ef-b9e4-25fff100dadd'",
            name="synthetic_actor",
        ),
        CheckConstraint(
            "payload->'schema_version' IS NOT DISTINCT FROM '1'::jsonb", name="version"
        ).ddl_if(dialect="postgresql"),
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    command: Mapped[UUID] = mapped_column(primary_key=True)
    actor: Mapped[UUID]
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    intent_digest: Mapped[str]
    payload: Mapped[dict[str, Any]] = mapped_column(snapshot_type)


class ConfirmationMember(Base):
    __tablename__ = "confirmation_members"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "command"],
            ["confirmation_receipts.user_id", "confirmation_receipts.command"],
        ),
        ForeignKeyConstraint(
            ["user_id", "account", "workout", "member", "supersedes"],
            [
                f"confirmation_members.{key}"
                for key in ("user_id", "account", "workout", "member", "command")
            ],
            name="fk_confirmation_member_predecessor",
        ),
        CheckConstraint("command <> supersedes", name="distinct_predecessor"),
        Index(
            "uq_confirmation_root",
            "user_id",
            "member",
            unique=True,
            postgresql_where=text("supersedes IS NULL"),
            sqlite_where=text("supersedes IS NULL"),
        ),
        Index("uq_confirmation_successor", "user_id", "member", "supersedes", unique=True),
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    account: Mapped[UUID] = mapped_column(primary_key=True)
    workout: Mapped[UUID] = mapped_column(primary_key=True)
    member: Mapped[UUID] = mapped_column(primary_key=True)
    command: Mapped[UUID] = mapped_column(primary_key=True)
    supersedes: Mapped[UUID | None]
    outcome: Mapped[UUID | None] = mapped_column(ForeignKey("session_outcomes.id"))

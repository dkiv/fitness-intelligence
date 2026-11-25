"""Garmin acquisition progress and independently scoped reconciliation evidence."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .models import Base
from .nutrition_models import source_account


class HistoryDay:
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    provider: Mapped[str] = mapped_column(primary_key=True)
    source_account_id: Mapped[UUID] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(primary_key=True)
    local_date: Mapped[date] = mapped_column(primary_key=True)


class GarminCoverage(HistoryDay, Base):
    __tablename__ = "garmin_history_coverage"
    __table_args__ = (
        source_account(),
        CheckConstraint("provider = 'garmin'", name="garmin_source"),
        CheckConstraint("status IN ('observed','empty','failed','partial')", name="status"),
        CheckConstraint("eligible_count >= 0", name="positive_count"),
    )
    status: Mapped[str]
    pass_key: Mapped[str]
    policy: Mapped[str]
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_success: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    eligible_count: Mapped[int | None]
    # Activity detail receipts, intake source outcomes, or a retryable acquisition gap.
    receipts: Mapped[dict[str, dict]] = mapped_column(JSON)


class GarminIssue(HistoryDay, Base):
    __tablename__ = "garmin_history_issues"
    __table_args__ = (
        source_account(),
        CheckConstraint("provider = 'garmin'", name="garmin_source"),
    )
    subject: Mapped[str] = mapped_column(primary_key=True)
    reason: Mapped[str] = mapped_column(primary_key=True)
    evidence_digest: Mapped[str]
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

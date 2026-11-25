"""Select at most one reported total for a trusted owner's provider-local day."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fitness_intelligence.db.history_models import GarminIssue
from fitness_intelligence.db.nutrition_models import DailyIntakeObservation


@dataclass(frozen=True)
class IntakeSelection:
    status: str
    reported_kcal: Decimal | None
    completeness: str
    observation_ids: tuple[UUID, ...]


def select_daily_intake(session: Session, owner_id: UUID, day: date) -> IntakeSelection:
    # Read the hold and the current source values in the same database snapshot.
    hold = (
        select(GarminIssue.reason)
        .filter_by(
            user_id=owner_id,
            local_date=day,
            category="intake",
            reason="source_disagreement",
            resolved_at=None,
        )
        .exists()
    )
    obs = DailyIntakeObservation
    rows = session.execute(
        select(obs.id, obs.reported_kcal, obs.completeness, hold.label("held"))
        .where(obs.user_id == owner_id, obs.local_date == day)
        .order_by(obs.id)
    ).all()
    if not rows:
        return IntakeSelection("missing", None, "unknown", ())
    evidence = tuple(row.id for row in rows)
    totals = {row.reported_kcal for row in rows}
    if len(totals) != 1 or rows[0].held:
        return IntakeSelection("conflict", None, "unknown", evidence)
    states = {row.completeness for row in rows}
    completeness = "partial" if "partial" in states else "unknown"
    if states == {"athlete_confirmed"}:
        completeness = "athlete_confirmed"
    total = totals.pop()
    return IntakeSelection("reported" if total else "explicit_zero", total, completeness, evidence)

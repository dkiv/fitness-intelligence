"""Owner/account/day weight inputs for analysis, including historical reconciliation holds."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, true
from sqlalchemy.orm import Session

from fitness_intelligence.db.history_models import GarminCoverage, GarminIssue
from fitness_intelligence.db.nutrition_models import BodyWeightObservation
from fitness_intelligence.domain.endurance import Source


@dataclass(frozen=True)
class WeightDay:
    acquisition: str
    reasons: tuple[str, ...]
    retained_ids: tuple[UUID, ...]
    measurements: tuple[tuple[datetime | None, Decimal], ...]


def select_weight_day(session: Session, source: Source, day: date) -> WeightDay:
    """Hold the whole day's analytical series if any of its measurements is disputed."""
    key = dict(
        user_id=source.owner_id,
        provider=source.provider,
        source_account_id=source.source_account_id,
        local_date=day,
    )
    history = key | {"category": "weight"}
    # One statement uses a single PostgreSQL snapshot even during a concurrent repair.
    status = select(GarminCoverage.status).filter_by(**history).scalar_subquery()
    reasons = (
        select(func.array_agg(GarminIssue.reason))
        .filter_by(**history, resolved_at=None)
        .scalar_subquery()
    )
    state = select(status.label("acquisition"), reasons.label("issues")).subquery()
    weights = (
        select(
            BodyWeightObservation.id,
            BodyWeightObservation.measured_at,
            BodyWeightObservation.mass_kg,
        )
        .filter_by(**key)
        .subquery()
    )
    result = session.execute(
        select(state, weights)
        .select_from(state.outerjoin(weights, true()))
        .order_by(weights.c.measured_at, weights.c.id)
    ).all()
    first = result[0]
    holds = tuple(sorted(set(first.issues or ())))
    return WeightDay(
        first.acquisition or "never_queried",
        holds,
        tuple(r.id for r in result if r.id is not None),
        () if holds else tuple((r.measured_at, r.mass_kg) for r in result if r.id is not None),
    )

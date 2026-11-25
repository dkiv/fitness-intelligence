"""Synthetic PostgreSQL checks for canonical evidence, attribution and safe downgrades."""

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fitness_intelligence.db.models import SourceAccount, User
from fitness_intelligence.db.nutrition_models import BodyWeightObservation, DailyIntakeObservation
from fitness_intelligence.nutrition.intake import select_daily_intake

DAY = date(2020, 1, 1)
RETRIEVED = datetime(2020, 1, 2, tzinfo=UTC)


def account(db: Session) -> SourceAccount:
    owner = User()
    db.add(owner)
    db.flush()
    result = SourceAccount(
        user_id=owner.id, provider="synthetic", status="active", provider_account_id="invented"
    )
    db.add(result)
    db.commit()
    return result


def intake(source: SourceAccount, field: str, kcal: int) -> DailyIntakeObservation:
    return DailyIntakeObservation(
        user_id=source.user_id,
        provider=source.provider,
        source_account_id=source.id,
        local_date=DAY,
        source_field=field,
        reported_kcal=Decimal(kcal),
        completeness="unknown",
        retrieved_at=RETRIEVED,
        mapping_version="synthetic-v1",
    )


def weight(source: SourceAccount) -> BodyWeightObservation:
    return BodyWeightObservation(
        user_id=source.user_id,
        provider=source.provider,
        source_account_id=source.id,
        local_date=DAY,
        source_field="example.mass",
        mass_kg=Decimal(90),
        source_unit="kg",
        source_value=Decimal(90),
        measured_at=RETRIEVED,
        time_resolution_us=1000,
        retrieved_at=RETRIEVED,
        mapping_version="synthetic-v1",
    )


def test_selection_one_value_per_owner_day(db: Session) -> None:
    src, other = account(db), account(db)
    db.add(intake(other, "total", 999))
    assert select_daily_intake(db, src.user_id, DAY).status == "missing"
    a, b = intake(src, "summary", 0), intake(src, "food", 0)
    db.add_all([a, b])
    sel = select_daily_intake(db, src.user_id, DAY)
    assert (sel.status, sel.reported_kcal, sel.completeness) == ("explicit_zero", 0, "unknown")
    assert set(sel.observation_ids) == {a.id, b.id}
    a.reported_kcal = 1200
    conflict = select_daily_intake(db, src.user_id, DAY)
    assert conflict.status == "conflict" and conflict.reported_kcal is None
    b.reported_kcal = 1200
    b.completeness = "partial"
    agreed = select_daily_intake(db, src.user_id, DAY)
    assert (agreed.reported_kcal, agreed.completeness) == (1200, "partial")


@pytest.mark.parametrize("factory", [lambda src: intake(src, "total", 5), weight])
def test_account_fk_and_populated_downgrade_guard(db: Session, factory) -> None:
    src, other = account(db), account(db)
    bad = factory(src)
    bad.user_id = other.user_id
    db.add(bad)
    with pytest.raises(IntegrityError):
        db.flush()
    db.rollback()
    good = factory(src)
    db.add(good)
    db.commit()
    ident = good.id
    db.rollback()  # Release the read transaction before the external Alembic connection locks.
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(RuntimeError, match="preserve intake and body weight"):
        command.downgrade(config, "b302")
    db.expire_all()
    assert db.get(type(good), ident) is not None
    assert db.scalar(text("SELECT version_num FROM alembic_version")) == "b330"
    db.delete(good)
    db.commit()
    command.downgrade(config, "b302")
    assert "daily_intake_observations" not in inspect(db.bind).get_table_names()
    assert "body_weight_observations" not in inspect(db.bind).get_table_names()
    command.upgrade(config, "head")
    command.check(config)

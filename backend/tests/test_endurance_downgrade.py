from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, Table, inspect, select, text
from sqlalchemy.orm import Session
from test_strength_models import make_reference, seed

from fitness_intelligence.db.endurance_models import (
    ActivitySplit,
    ActivityStep,
    EnduranceActivity,
)
from fitness_intelligence.db.models import SourceAccount, User

pytestmark = pytest.mark.postgres

B2_TABLES = {
    "endurance_activities",
    "activity_split_summaries",
    "activity_performed_steps",
    "daily_recovery_observations",
}


@pytest.fixture
def config(db: Session) -> Config:
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.downgrade(config, "b201")
    return config


def assert_schema(db: Session, revision: str) -> None:
    inspector = inspect(db.get_bind())
    expected = revision == "b201"
    assert db.scalar(text("SELECT version_num FROM alembic_version")) == revision
    tables = B2_TABLES.intersection(inspector.get_table_names())
    assert tables == (B2_TABLES if expected else set())
    unique = inspector.get_unique_constraints("external_references")
    assert any(key["name"] == "uq_reference_workout_identity" for key in unique) == expected
    if expected:
        indexes = inspector.get_indexes("daily_recovery_observations")
        assert any(index["name"] == "ix_daily_recovery_observations_user_id" for index in indexes)


def test_empty_b201_downgrade_and_reupgrade(db: Session, config: Config) -> None:
    command.downgrade(config, "e301")
    assert_schema(db, "e301")
    db.close()
    command.upgrade(config, "b201")
    assert_schema(db, "b201")


def assert_downgrade_rejected(db: Session, config: Config) -> None:
    db.commit()
    with pytest.raises(RuntimeError, match="preserve observations before downgrade"):
        command.downgrade(config, "e301")
    assert_schema(db, "b201")


@pytest.mark.parametrize(
    "with_children", [False, True], ids=["activity-only", "with-splits-and-steps"]
)
def test_b201_downgrade_preserves_activity(
    db: Session, config: Config, with_children: bool
) -> None:
    owner, _, workout, _, _ = seed(db)
    reference = make_reference(
        db,
        user_id=owner.id,
        provider="synthetic",
        entity_type="workout",
        external_id="synthetic-run",
        workout_id=workout.id,
        raw_payload={},
    )
    db.add(reference)
    db.flush()
    parent = dict(user_id=owner.id, workout_id=workout.id)
    activity = EnduranceActivity(
        **parent,
        reference_id=reference.id,
        sport="running",
        local_date=date(2024, 3, 10),
        distance_m=Decimal("900.125"),
    )
    db.add(activity)
    if with_children:
        db.flush()
        split = ActivitySplit(**parent, position=0, kind="RUN_ACTIVE", count=2)
        step = ActivityStep(
            **parent, workout_index=0, step_index=0, duration_value=30, duration_unit="s"
        )
        db.add_all([split, step])

    assert_downgrade_rejected(db, config)
    db.refresh(activity)
    assert activity.reference_id == reference.id
    assert activity.distance_m == Decimal("900.125")
    if with_children:
        db.refresh(split)
        db.refresh(step)
        assert split.count == 2
        assert step.duration_value == Decimal("30")


def test_b201_downgrade_preserves_daily_observation(db: Session, config: Config) -> None:
    owner = User()
    db.add(owner)
    db.flush()
    account = SourceAccount(
        user_id=owner.id, provider="synthetic", provider_account_id="test", status="active"
    )
    db.add(account)
    db.flush()
    # This test targets the historical schema, independently of later ORM columns.
    table = Table("daily_recovery_observations", MetaData(), autoload_with=db.connection())
    observation_id = uuid4()
    db.execute(
        table.insert().values(
            id=observation_id,
            user_id=owner.id,
            source_account_id=account.id,
            provider=account.provider,
            local_date=date(2024, 3, 10),
            metric="resting_hr",
            value=52,
            unit="bpm",
            method="reported",
        )
    )

    assert_downgrade_rejected(db, config)
    assert db.execute(
        select(table.c.source_account_id, table.c.value, table.c.unit).where(
            table.c.id == observation_id
        )
    ).one() == (account.id, 52, "bpm")

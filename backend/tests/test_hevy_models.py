from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session
from test_strength_models import seed

from fitness_intelligence.db.models import (
    AccountSyncState,
    ExternalReference,
    SourceAccount,
    WorkoutTombstone,
)

pytestmark = pytest.mark.postgres


def account(db: Session, user_id: object, identity: str = "account-1") -> SourceAccount:
    item = SourceAccount(
        user_id=user_id, provider="hevy", provider_account_id=identity, status="active"
    )
    db.add(item)
    db.commit()
    return item


def test_namespaces_immutability_and_ownership(db: Session) -> None:
    owner, other, workout, _, _ = seed(db)
    first = account(db, owner.id)
    second = account(db, owner.id, "account-2")
    for source in (first, second):
        db.add(
            ExternalReference(
                user_id=owner.id,
                provider="hevy",
                source_account_id=source.id,
                entity_type="workout",
                external_id="same-id",
                workout_id=workout.id,
                raw_payload={},
            )
        )
    db.commit()
    first.provider_account_id = "changed"
    with pytest.raises(DBAPIError):
        db.commit()
    db.rollback()
    db.add(
        WorkoutTombstone(
            user_id=other.id, provider="hevy", source_account_id=first.id, external_id="unseen"
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.add(
        ExternalReference(
            user_id=owner.id,
            provider="wrong",
            source_account_id=first.id,
            entity_type="workout",
            external_id="x",
            workout_id=workout.id,
            raw_payload={},
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    db.close()
    with pytest.raises(RuntimeError, match="collisions"):
        command.downgrade(config, "2827ecaa5ef5")
    assert "source_accounts" in inspect(db.bind).get_table_names()
    assert len(db.scalars(select(ExternalReference)).all()) == 2


def test_pending_tombstone_checkpoint_and_atomic_rollback(db: Session) -> None:
    owner, other, _, _, _ = seed(db)
    source = account(db, owner.id)
    tombstone = WorkoutTombstone(
        user_id=owner.id, provider="hevy", source_account_id=source.id, external_id="unseen"
    )
    state = AccountSyncState(user_id=owner.id, provider="hevy", source_account_id=source.id)
    db.add_all([tombstone, state])
    db.commit()
    assert tombstone.source_deleted_at is None and tombstone.observed_at.tzinfo is not None
    assert not state.initialized and state.checkpoint is None
    now = datetime.now(UTC)
    state.initialized, state.checkpoint = True, now
    tombstone.source_deleted_at = now
    db.commit()
    state.checkpoint = now - timedelta(seconds=1)
    with pytest.raises(DBAPIError):
        db.commit()
    db.rollback()
    assert state.checkpoint == now
    tombstone.external_id = "changed"
    db.add(AccountSyncState(user_id=other.id, provider="hevy", source_account_id=source.id))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    assert tombstone.external_id == "unseen"
    db.add(
        WorkoutTombstone(
            user_id=owner.id, provider="hevy", source_account_id=source.id, external_id="unseen"
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_legacy_backfill_preserves_reference_and_downgrade(db: Session) -> None:
    owner, _, workout, _, _ = seed(db)
    owner_id, workout_id, ref_id = owner.id, workout.id, uuid4()
    db.close()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.downgrade(config, "2827ecaa5ef5")
    with db.bind.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO external_references "
                "(id,user_id,provider,entity_type,external_id,workout_id,"
                "raw_payload,source_version) "
                "VALUES (:id,:user,'legacy-provider','workout','original-id',"
                ":workout,'{}','original')"
            ),
            dict(id=ref_id, user=owner_id, workout=workout_id),
        )
        before = dict(
            connection.execute(text("SELECT * FROM external_references")).mappings().one()
        )
    command.upgrade(config, "head")
    command.check(config)
    with db.bind.connect() as connection:
        after = dict(connection.execute(text("SELECT * FROM external_references")).mappings().one())
        source_id = after.pop("source_account_id")
        assert after == before
        source = (
            connection.execute(
                text("SELECT * FROM source_accounts WHERE id=:id"), dict(id=source_id)
            )
            .mappings()
            .one()
        )
        assert source["status"] == "legacy_unresolved" and source["provider_account_id"] is None
    command.downgrade(config, "2827ecaa5ef5")
    with db.bind.connect() as connection:
        assert (
            dict(connection.execute(text("SELECT * FROM external_references")).mappings().one())
            == before
        )
        assert (
            connection.execute(
                text("SELECT id FROM workouts WHERE id=:id"), dict(id=workout_id)
            ).scalar_one()
            == workout_id
        )
    command.upgrade(config, "head")


@pytest.mark.parametrize("mutation", ["owner", "provider", "duplicate", "unresolved_active"])
def test_account_constraints(db: Session, mutation: str) -> None:
    owner, other, _, _, _ = seed(db)
    source = account(db, owner.id)
    if mutation == "owner":
        source.user_id = other.id
    elif mutation == "provider":
        source.provider = "different"
    elif mutation == "duplicate":
        db.add(
            SourceAccount(
                user_id=owner.id, provider="hevy", provider_account_id="account-1", status="active"
            )
        )
    else:
        db.add(SourceAccount(user_id=owner.id, provider="hevy", status="active"))
    with pytest.raises(DBAPIError):
        db.commit()
    db.rollback()


def test_legacy_binding_conflict_rolls_back(db: Session) -> None:
    owner, _, _, _, _ = seed(db)
    account(db, owner.id)
    legacy = SourceAccount(user_id=owner.id, provider="hevy", status="legacy_unresolved")
    db.add(legacy)
    db.commit()
    legacy.provider_account_id, legacy.status = "account-1", "active"
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    assert legacy.provider_account_id is None and legacy.status == "legacy_unresolved"
    legacy.provider_account_id, legacy.status = "account-2", "active"
    db.commit()
    legacy.provider_account_id = None
    legacy.status = "legacy_unresolved"
    with pytest.raises(DBAPIError):
        db.commit()
    db.rollback()

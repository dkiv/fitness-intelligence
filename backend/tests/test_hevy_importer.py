from collections.abc import Iterator
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import event, select, text
from sqlalchemy.orm import Session
from test_hevy_mapping import snapshot

from fitness_intelligence.adapters.hevy.client import HevyError
from fitness_intelligence.adapters.hevy.importer import Importer, LocalBinding
from fitness_intelligence.adapters.hevy.schemas import DeletedEvent, HevyWorkout, UpdatedEvent
from fitness_intelligence.db.models import (
    AccountSyncState,
    ExternalReference,
    SourceAccount,
    User,
    Workout,
    WorkoutTombstone,
)

pytestmark = pytest.mark.postgres


class FakeClient:
    def __init__(self) -> None:
        self.data = snapshot()
        self.feed: list[UpdatedEvent | DeletedEvent] = []
        self.fail = False
        self.identity_value = "account"

    def identity(self) -> str:
        return self.identity_value

    def workouts(self) -> Iterator[HevyWorkout]:
        yield HevyWorkout.model_validate(self.data)

    def events(self, since: datetime) -> Iterator[UpdatedEvent | DeletedEvent]:
        yield from self.feed
        if self.fail:
            raise HevyError("synthetic interruption")

    def workout(self, identity: str) -> HevyWorkout:
        return HevyWorkout.model_validate(self.data)


def setup(db: Session) -> tuple[Importer, FakeClient]:
    user = User()
    db.add(user)
    db.flush()
    account = SourceAccount(
        user_id=user.id, provider="hevy", provider_account_id="account", status="active"
    )
    db.add(account)
    db.commit()
    client = FakeClient()
    binding = LocalBinding(user.id, account.id, "account")
    return Importer(db.bind, binding, client), client


def read(db: Session) -> Workout:
    db.expire_all()
    return db.scalars(select(Workout)).one()


def edit(client: FakeClient, day: int = 2) -> None:
    client.data["updated_at"] = f"2026-01-{day:02d}T12:00:00Z"
    client.feed = [UpdatedEvent(type="updated", workout=HevyWorkout.model_validate(client.data))]


def test_duplicate_edit_reorder_stale_and_parent_only(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    workout = read(db)
    identity, child = workout.id, workout.exercises[0].id
    importer.sync()
    assert read(db).exercises[0].id == child
    client.data["title"] = "Parent edit"
    edit(client)
    importer.sync()
    assert read(db).exercises[0].id == child
    extra = deepcopy(client.data["exercises"][0])
    extra["index"], extra["title"] = 0, "First"
    extra["sets"].append(dict(extra["sets"][0], index=0))
    client.data["exercises"].append(extra)
    edit(client, 3)
    importer.sync()
    workout = read(db)
    assert workout.id == identity and workout.exercises[0].name == "First"
    assert workout.exercises[1].id != child
    assert [s.position for s in workout.exercises[0].sets] == [0, 1]
    client.data = snapshot()
    edit(client, 2)
    importer.sync()
    assert len(read(db).exercises) == 2


def test_deletion_unseen_stale_and_restore(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    identity = read(db).id
    client.feed = [
        DeletedEvent(type="deleted", id=client.data["id"], deleted_at="2026-01-03T00:00:00Z"),
        DeletedEvent(type="deleted", id="unseen", deleted_at="2026-01-03T00:00:00Z"),
    ]
    importer.sync()
    assert read(db).deleted_at is not None
    assert len(db.scalars(select(WorkoutTombstone)).all()) == 2
    edit(client, 2)
    importer.sync()
    assert read(db).deleted_at is not None
    edit(client, 4)
    importer.sync()
    assert read(db).id == identity and read(db).deleted_at is None


@pytest.mark.parametrize("failure", ["interrupt", "pending", "conflict", "future"])
def test_failed_runs_keep_checkpoint(db: Session, failure: str) -> None:
    importer, client = setup(db)
    importer.sync()
    checkpoint = db.scalar(select(AccountSyncState.checkpoint))
    if failure == "interrupt":
        client.fail = True
        edit(client)
    elif failure == "pending":
        client.feed = [DeletedEvent(type="deleted", id="unknown")]
    elif failure == "conflict":
        client.data["title"] = "Same time conflict"
        client.feed = [
            UpdatedEvent(type="updated", workout=HevyWorkout.model_validate(client.data))
        ]
    else:
        client.data["updated_at"] = "2099-01-01T00:00:00Z"
        client.feed = [
            UpdatedEvent(type="updated", workout=HevyWorkout.model_validate(client.data))
        ]
    with pytest.raises(HevyError):
        importer.sync()
    db.expire_all()
    assert db.scalar(select(AccountSyncState.checkpoint)) == checkpoint
    if failure == "pending":
        assert db.scalar(select(WorkoutTombstone)).source_deleted_at is None


def test_initial_interruption_replay(db: Session) -> None:
    importer, client = setup(db)
    client.fail = True
    with pytest.raises(HevyError):
        importer.sync()
    assert db.scalar(select(AccountSyncState)) is None
    identity = read(db).id
    client.fail = False
    importer.sync()
    assert read(db).id == identity
    assert db.scalar(select(AccountSyncState)).initialized


def test_account_binding_isolation_and_lock(db: Session) -> None:
    importer, client = setup(db)
    client.identity_value = "wrong"
    with pytest.raises(HevyError, match="mismatch"):
        importer.sync()
    client.identity_value = "account"
    other = Importer(
        db.bind, LocalBinding(uuid4(), importer.binding.source_account_id, "account"), client
    )
    with pytest.raises(HevyError, match="binding"):
        other.sync()
    with importer._locked():
        with pytest.raises(HevyError, match="already running"):
            importer.sync()
    second, _ = setup(db)
    importer.sync()
    second.sync()
    assert len(db.scalars(select(Workout)).all()) == 2
    assert len(db.scalars(select(ExternalReference)).all()) == 2


def test_replacement_rollback(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    workout = read(db)
    child = workout.exercises[0].id
    client.data["exercises"][0]["title"] = "Changed child"
    edit(client)

    def fail_insert(
        connection: Any, cursor: Any, statement: str, parameters: Any, context: Any, many: bool
    ) -> None:
        if statement.startswith("INSERT INTO exercise_sets"):
            raise RuntimeError("synthetic insert failure")

    event.listen(db.bind, "before_cursor_execute", fail_insert)
    try:
        with pytest.raises(RuntimeError):
            importer.sync()
    finally:
        event.remove(db.bind, "before_cursor_execute", fail_insert)
    assert read(db).exercises[0].id == child
    assert read(db).exercises[0].name == "Synthetic press"


def test_foreign_child_reference_blocks_replacement(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    workout = read(db)
    db.add(
        ExternalReference(
            user_id=importer.binding.user_id,
            provider="hevy",
            source_account_id=importer.binding.source_account_id,
            entity_type="exercise",
            external_id="foreign",
            exercise_id=workout.exercises[0].id,
            raw_payload={},
        )
    )
    db.commit()
    client.data["exercises"] = []
    edit(client)
    with pytest.raises(HevyError, match="ownership"):
        importer.sync()
    assert read(db).exercises


def test_same_owner_account_namespaces(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    other = SourceAccount(
        user_id=importer.binding.user_id,
        provider="hevy",
        provider_account_id="second",
        status="active",
    )
    db.add(other)
    db.commit()
    client.identity_value = "second"
    second = Importer(db.bind, LocalBinding(other.user_id, other.id, "second"), client)
    second.sync()
    assert len(db.scalars(select(Workout)).all()) == 2
    assert len(db.scalars(select(AccountSyncState)).all()) == 2
    client.feed = [
        DeletedEvent(type="deleted", id=client.data["id"], deleted_at="2026-01-03T00:00:00Z")
    ]
    second.sync()
    db.expire_all()
    assert sum(w.deleted_at is not None for w in db.scalars(select(Workout))) == 1


def test_newest_first_events_and_deletion_tie(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    client.data["title"] = "New"
    edit(client, 3)
    client.feed.append(UpdatedEvent(type="updated", workout=HevyWorkout.model_validate(snapshot())))
    importer.sync()
    assert read(db).title == "New"
    client.feed = [
        DeletedEvent(type="deleted", id=client.data["id"], deleted_at=client.data["updated_at"]),
        client.feed[0],
    ]
    importer.sync()
    assert read(db).deleted_at is not None


def test_conflict_refetch_resolves_newer_detail(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    conflict = snapshot()
    conflict["title"] = "Conflicting stale snapshot"
    client.data["title"] = "Current confirmed snapshot"
    edit(client)
    client.feed = [UpdatedEvent(type="updated", workout=HevyWorkout.model_validate(conflict))]
    importer.sync()
    assert read(db).title == "Current confirmed snapshot"


def test_disconnected_and_checkpoint_regression(db: Session) -> None:
    importer, client = setup(db)
    source = db.get(SourceAccount, importer.binding.source_account_id)
    source.status = "disconnected"
    db.commit()
    with pytest.raises(HevyError, match="binding"):
        importer.sync()
    source.status = "active"
    db.add(
        AccountSyncState(
            user_id=source.user_id,
            provider="hevy",
            source_account_id=source.id,
            initialized=True,
            checkpoint=datetime(2099, 1, 1, tzinfo=UTC),
        )
    )
    db.commit()
    with pytest.raises(HevyError, match="regression"):
        importer.sync()


def test_nonconverging_baseline(db: Session) -> None:
    importer, client = setup(db)
    calls = []

    def changing() -> Iterator[HevyWorkout]:
        calls.append(1)
        data = dict(snapshot(), id=f"changing-{len(calls)}")
        yield HevyWorkout.model_validate(data)

    client.workouts = changing
    with pytest.raises(HevyError, match="converge"):
        importer.sync()
    assert len(calls) == 3
    assert db.scalar(select(AccountSyncState)) is None


def test_reconciliation_missing_detail_not_deletion(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    checkpoint = db.scalar(select(AccountSyncState.checkpoint))
    client.workouts = lambda: iter(())
    with pytest.raises(HevyError, match="missing workouts"):
        importer.sync(reconcile=True)
    assert read(db).deleted_at is None
    assert db.scalar(select(AccountSyncState.checkpoint)) == checkpoint


def test_pending_after_confirmed_deletion_preserves_evidence(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    dated = DeletedEvent(type="deleted", id=client.data["id"], deleted_at="2026-01-03T00:00:00Z")
    client.feed = [dated]
    importer.sync()
    checkpoint = db.scalar(select(AccountSyncState.checkpoint))
    client.feed = [DeletedEvent(type="deleted", id=client.data["id"])]
    with pytest.raises(HevyError, match="unresolved"):
        importer.sync()
    db.expire_all()
    tombstone = db.scalar(select(WorkoutTombstone))
    assert tombstone.pending and tombstone.source_deleted_at == datetime(2026, 1, 3, tzinfo=UTC)
    # Even if a subsequent feed omits the unresolved event, no checkpoint can advance.
    client.feed = []
    with pytest.raises(HevyError, match="unresolved"):
        importer.sync()
    assert db.scalar(select(AccountSyncState.checkpoint)) == checkpoint
    client.feed = [dated]
    with pytest.raises(HevyError, match="unresolved"):
        importer.sync()
    client.feed = [
        DeletedEvent(type="deleted", id=client.data["id"], deleted_at="2026-01-04T00:00:00Z")
    ]
    importer.sync()
    db.expire_all()
    assert not db.scalar(select(WorkoutTombstone)).pending


def test_pending_update_does_not_prevent_later_deletion_resolution(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    client.feed = [DeletedEvent(type="deleted", id=client.data["id"])]
    with pytest.raises(HevyError):
        importer.sync()
    checkpoint = db.scalar(select(AccountSyncState.checkpoint))
    edit(client, 3)
    client.feed.append(
        DeletedEvent(type="deleted", id=client.data["id"], deleted_at="2026-01-04T00:00:00Z")
    )
    with pytest.raises(HevyError, match="unresolved"):
        importer.sync()
    db.expire_all()
    assert not db.scalar(select(WorkoutTombstone)).pending
    assert db.scalar(select(AccountSyncState.checkpoint)) == checkpoint
    importer.sync()
    assert read(db).deleted_at == datetime(2026, 1, 4, tzinfo=UTC)


def test_unlock_failure_discards_locked_connection(db: Session) -> None:
    importer, _ = setup(db)

    def fail_unlock(
        connection: Any, cursor: Any, statement: str, parameters: Any, context: Any, many: bool
    ) -> None:
        if "pg_advisory_unlock" in statement:
            raise RuntimeError("synthetic unlock failure")

    event.listen(db.bind, "before_cursor_execute", fail_unlock)
    try:
        with pytest.raises(RuntimeError, match="unlock failure"):
            with importer._locked() as session:
                old_backend = session.scalar(text("SELECT pg_backend_pid()"))
    finally:
        event.remove(db.bind, "before_cursor_execute", fail_unlock)
    # A pool reset alone leaves a session lock behind; invalidation closes its backend.
    with importer._locked() as session:
        assert session.scalar(text("SELECT pg_backend_pid()")) != old_backend


def test_shared_workout_deletion_rolls_back_tombstone_and_checkpoint(db: Session) -> None:
    importer, client = setup(db)
    importer.sync()
    workout = read(db)
    checkpoint = db.scalar(select(AccountSyncState.checkpoint))
    db.add(
        ExternalReference(
            user_id=importer.binding.user_id,
            provider="hevy",
            source_account_id=importer.binding.source_account_id,
            entity_type="exercise",
            external_id="shared-child",
            exercise_id=workout.exercises[0].id,
            raw_payload={},
        )
    )
    db.commit()
    client.feed = [
        DeletedEvent(type="deleted", id=client.data["id"], deleted_at="2026-01-04T00:00:00Z")
    ]
    with pytest.raises(HevyError, match="ownership"):
        importer.sync()
    assert read(db).deleted_at is None
    assert db.scalar(select(WorkoutTombstone)) is None
    assert db.scalar(select(AccountSyncState.checkpoint)) == checkpoint

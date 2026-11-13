"""Account-serialized local importer with independently atomic snapshot transactions."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, fields
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID

from sqlalchemy import Engine, or_, select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from fitness_intelligence.db.models import (
    AccountSyncState,
    ExerciseSet,
    ExternalReference,
    SourceAccount,
    Workout,
    WorkoutExercise,
    WorkoutTombstone,
)
from fitness_intelligence.domain.strength import StrengthSet

from .client import HevyClient, HevyError
from .mapping import map_workout
from .schemas import DeletedEvent, HevyWorkout, UpdatedEvent, utc


@dataclass(frozen=True)
class LocalBinding:
    """Trusted OS-operator configuration, never input from an HTTP caller."""

    user_id: UUID
    source_account_id: UUID
    provider_account_id: str


class Importer:
    def __init__(self, engine: Engine, binding: LocalBinding, client: HevyClient) -> None:
        self.engine, self.binding, self.client = engine, binding, client
        self.now = datetime.now(UTC)
        self._deferred_update = False

    def _scope(
        self, model: type[AccountSyncState] | type[ExternalReference] | type[WorkoutTombstone]
    ) -> tuple[ColumnElement[bool], ...]:
        return (
            model.user_id == self.binding.user_id,
            model.provider == "hevy",
            model.source_account_id == self.binding.source_account_id,
        )

    @contextmanager
    def _locked(self) -> Iterator[Session]:
        # Dedicated connection: session advisory lock survives per-snapshot commits.
        # A crashed process releases it when PostgreSQL closes the connection.
        key = int.from_bytes(
            sha256(str(self.binding.source_account_id).encode()).digest()[:8], "big", signed=True
        )
        with self.engine.connect() as connection:
            if connection.dialect.name != "postgresql":
                raise HevyError("PostgreSQL required")
            try:
                locked = connection.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": key})
                connection.commit()
            except BaseException:
                # Acquisition may have succeeded before a commit/connection failure.
                connection.invalidate()
                raise
            if not locked:
                raise HevyError("account synchronization already running")
            try:
                with Session(connection, expire_on_commit=False) as session:
                    yield session
            finally:
                try:
                    connection.rollback()
                    connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})
                    connection.commit()
                except BaseException:
                    # Rollback/pool reset cannot release session advisory locks.
                    connection.invalidate()
                    raise

    def _account(self, session: Session) -> None:
        account = session.scalar(
            select(SourceAccount)
            .where(
                SourceAccount.id == self.binding.source_account_id,
                SourceAccount.user_id == self.binding.user_id,
                SourceAccount.provider == "hevy",
                SourceAccount.status == "active",
                SourceAccount.provider_account_id == self.binding.provider_account_id,
            )
            .execution_options(populate_existing=True)
        )
        if account is None:
            raise HevyError("untrusted or inactive account binding")

    def _reference(self, session: Session, identity: str) -> ExternalReference | None:
        return session.scalar(
            select(ExternalReference).where(
                *self._scope(ExternalReference),
                ExternalReference.entity_type == "workout",
                ExternalReference.external_id == identity,
            )
        )

    def _tombstone(self, session: Session, identity: str) -> WorkoutTombstone | None:
        return session.scalar(
            select(WorkoutTombstone).where(
                *self._scope(WorkoutTombstone),
                WorkoutTombstone.external_id == identity,
            )
        )

    def _exclusive(self, session: Session, workout: Workout, ref: ExternalReference) -> None:
        exercise_ids = select(WorkoutExercise.id).where(
            WorkoutExercise.user_id == self.binding.user_id,
            WorkoutExercise.workout_id == workout.id,
        )
        set_ids = select(ExerciseSet.id).where(
            ExerciseSet.user_id == self.binding.user_id, ExerciseSet.exercise_id.in_(exercise_ids)
        )
        foreign = session.scalar(
            select(ExternalReference.id)
            .where(
                ExternalReference.user_id == self.binding.user_id,
                ExternalReference.id != ref.id,
                or_(
                    ExternalReference.workout_id == workout.id,
                    ExternalReference.exercise_id.in_(exercise_ids),
                    ExternalReference.set_id.in_(set_ids),
                ),
            )
            .limit(1)
        )
        if foreign is not None:
            raise HevyError("shared workout ownership conflict")

    def _clock(self, instant: datetime) -> None:
        if instant > datetime.now(UTC) + timedelta(minutes=5):
            raise HevyError("future source timestamp")

    def _upsert(self, session: Session, source: HevyWorkout, *, confirmed: bool = False) -> None:
        mapped = map_workout(source)
        self._clock(mapped.source_updated_at)
        needs_detail = False
        with session.begin():
            self._account(session)
            tombstone = self._tombstone(session, source.id)
            ref = self._reference(session, source.id)
            if tombstone is not None:
                if tombstone.pending or tombstone.source_deleted_at is None:
                    # Continue the feed so later timestamped evidence can resolve intent.
                    # This run must still fail: this skipped update needs a fresh replay.
                    self._deferred_update = True
                    return
                if mapped.source_updated_at <= tombstone.source_deleted_at:
                    return
                needs_detail = not confirmed
            if ref is not None and ref.source_updated_at is not None:
                if mapped.source_updated_at < ref.source_updated_at:
                    return
                if mapped.source_updated_at == ref.source_updated_at:
                    if (ref.sync_metadata or {}).get("content_hash") == mapped.content_hash:
                        return
                    if confirmed:
                        raise HevyError("equal timestamp content conflict")
                    needs_detail = True
            if not needs_detail:
                if ref is None:
                    workout = Workout(user_id=self.binding.user_id)
                    session.add(workout)
                else:
                    workout = session.scalar(
                        select(Workout).where(
                            Workout.user_id == self.binding.user_id, Workout.id == ref.workout_id
                        )
                    )
                    if workout is None:
                        raise HevyError("missing canonical workout")
                    self._exclusive(session, workout, ref)
                canonical = mapped.workout
                for name in ("title", "notes", "started_at", "ended_at"):
                    setattr(workout, name, getattr(canonical, name))
                workout.deleted_at = None
                # Compare normalized children so metadata/parent-only edits preserve child UUIDs.
                children = [
                    dict(
                        position=e.position,
                        name=e.name,
                        notes=e.notes,
                        superset_group=e.superset_group,
                        sets=[
                            {
                                field.name: getattr(entry, field.name)
                                for field in fields(StrengthSet)
                            }
                            for entry in e.sets
                        ],
                    )
                    for e in workout.exercises
                ]
                desired = [asdict(e) for e in canonical.exercises]
                # asdict retains tuples; use lists for comparison with ORM collections.
                for item in desired:
                    item["sets"] = list(item["sets"])
                if children != desired:
                    for exercise in list(workout.exercises):
                        session.delete(exercise)
                    session.flush()
                    if ref is not None:
                        session.expire(workout, ["exercises"])
                    for item in canonical.exercises:
                        exercise = WorkoutExercise(
                            user_id=self.binding.user_id,
                            workout=workout,
                            **{k: v for k, v in asdict(item).items() if k != "sets"},
                        )
                        session.add(exercise)
                        for entry in item.sets:
                            session.add(
                                ExerciseSet(
                                    user_id=self.binding.user_id, exercise=exercise, **asdict(entry)
                                )
                            )
                session.flush()
                if ref is None:
                    ref = ExternalReference(
                        user_id=self.binding.user_id,
                        provider="hevy",
                        source_account_id=self.binding.source_account_id,
                        entity_type="workout",
                        external_id=source.id,
                        workout_id=workout.id,
                    )
                    session.add(ref)
                ref.raw_payload = mapped.raw_payload
                ref.source_created_at = mapped.source_created_at
                ref.source_updated_at = mapped.source_updated_at
                ref.source_deleted_at = None
                ref.last_synced_at = self.now
                ref.sync_metadata = {
                    "adapter": "hevy-importer-v1",
                    "hash_contract": "hevy-semantic-v2",
                    "content_hash": mapped.content_hash,
                    "warnings": list(mapped.warnings),
                }
        if needs_detail:
            detail = self.client.workout(source.id)
            if utc(detail.updated_at) < mapped.source_updated_at:
                raise HevyError("detail older than observed update")
            self._upsert(session, detail, confirmed=True)

    def _delete(self, session: Session, event: DeletedEvent) -> None:
        instant = None if event.deleted_at is None else utc(event.deleted_at)
        if instant is not None:
            self._clock(instant)
        with session.begin():
            self._account(session)
            tombstone = self._tombstone(session, event.id)
            ref = self._reference(session, event.id)
            if instant is not None and ref is not None and ref.source_updated_at is not None:
                if instant < ref.source_updated_at:
                    return
            if tombstone is None:
                tombstone = WorkoutTombstone(
                    user_id=self.binding.user_id,
                    provider="hevy",
                    source_account_id=self.binding.source_account_id,
                    external_id=event.id,
                )
                session.add(tombstone)
            if instant is None:
                tombstone.pending = True
            if instant is not None:
                if tombstone.source_deleted_at is None or instant > tombstone.source_deleted_at:
                    tombstone.pending = False
                if tombstone.source_deleted_at is None or instant > tombstone.source_deleted_at:
                    tombstone.source_deleted_at = instant
                if ref is not None:
                    workout = session.scalar(
                        select(Workout).where(
                            Workout.user_id == self.binding.user_id, Workout.id == ref.workout_id
                        )
                    )
                    if workout is None:
                        raise HevyError("missing canonical workout")
                    self._exclusive(session, workout, ref)
                    ref.source_deleted_at = tombstone.source_deleted_at
                    workout.deleted_at = tombstone.source_deleted_at
        if instant is None:
            raise HevyError("unresolved deletion")

    def sync(self, *, reconcile: bool = False) -> None:
        self.now = datetime.now(UTC)
        self._deferred_update = False
        if self.client.identity() != self.binding.provider_account_id:
            raise HevyError("provider account mismatch")
        with self._locked() as session:
            with session.begin():
                self._account(session)
                state = session.scalar(
                    select(AccountSyncState).where(*self._scope(AccountSyncState))
                )
                checkpoint = None if state is None else state.checkpoint
                if checkpoint is not None and checkpoint > self.now:
                    raise HevyError("checkpoint clock regression")
            since = (checkpoint or self.now) - timedelta(minutes=5)

            def events() -> None:
                for event in self.client.events(since):
                    if isinstance(event, UpdatedEvent):
                        self._upsert(session, event.workout)
                    else:
                        self._delete(session, event)

            if checkpoint is None or reconcile:
                previous: set[str] | None = None
                for _ in range(3):
                    identities = set()
                    for source in self.client.workouts():
                        identities.add(source.id)
                        self._upsert(session, source)
                    events()
                    if identities == previous:
                        break
                    previous = identities
                else:
                    raise HevyError("baseline did not converge")
                # Missing IDs are uncertainty, never deletion evidence.
                with session.begin():
                    known = set(
                        session.scalars(
                            select(ExternalReference.external_id).where(
                                *self._scope(ExternalReference),
                                ExternalReference.entity_type == "workout",
                                ExternalReference.source_deleted_at.is_(None),
                            )
                        )
                    )
                for identity in sorted(known - identities):
                    # A detail 404 remains uncertainty; it never fabricates a tombstone.
                    self._upsert(session, self.client.workout(identity), confirmed=True)
                if known - identities:
                    raise HevyError("reconciliation missing workouts unresolved")
            else:
                events()
            with session.begin():
                self._account(session)
                pending = session.scalar(
                    select(WorkoutTombstone.id)
                    .where(
                        *self._scope(WorkoutTombstone),
                        or_(
                            WorkoutTombstone.pending.is_(True),
                            WorkoutTombstone.source_deleted_at.is_(None),
                        ),
                    )
                    .limit(1)
                )
                if pending is not None or self._deferred_update:
                    raise HevyError("unresolved deletion")
                if state is None:
                    state = AccountSyncState(
                        user_id=self.binding.user_id,
                        provider="hevy",
                        source_account_id=self.binding.source_account_id,
                    )
                    session.add(state)
                state.initialized, state.checkpoint = True, self.now

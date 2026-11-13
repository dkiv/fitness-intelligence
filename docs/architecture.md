# Architecture

## Current implementation

A monorepo contains a Python backend, migrations, tests and shared documentation. FastAPI exposes
`GET /health` as process liveness; it intentionally does not query PostgreSQL. Pydantic Settings
loads DATABASE_URL only when database access is needed. SQLAlchemy uses synchronous psycopg
connections and request-scoped sessions. Routes using blocking database operations should be
synchronous. Alembic owns schema creation; application startup does not create tables.

The users table retains its UUID primary key and server-generated timestamp. There is no email,
password or authentication implementation. UUID generation happens in the ORM; direct SQL inserts
must supply an ID. The database now supports fitness records, but no fitness API exposes them.

Compose runs PostgreSQL, a one-shot migration service, and the development API. Ports bind to
localhost. Development data lives in a Docker volume. This configuration is not public hosting.

## Canonical strength schema (Milestone 1)

- `workouts`: user, title, notes, start/end instants, local creation/update timestamps and an
  optional canonical deletion marker.
- `workout_exercises`: user, workout, zero-based position, display name, notes and optional
  superset group. Names are snapshots; there is no premature global exercise taxonomy.
- `exercise_sets`: user, exercise, zero-based position, optional kind, reps, weight, distance,
  duration, RPE, completion instant, notes and original measurement metadata.
- `external_references`: user, provider namespace, entity type and stable external identifier,
  exactly one workout/exercise/set target, raw JSON payload, first import and last successful
  synchronization instants, source creation/update/deletion instants, optional source version
  and synchronization metadata. Payloads must never contain credentials or be logged.

Every fitness row has a non-null FK to `users`. Child and reference targets also use composite
`(user_id, parent_id)` foreign keys, preventing cross-user links even through direct SQL.
Unique `(user_id, id)` keys enable these constraints. User-leading indexes support scoped lookups;
unique parent/position keys support ordered traversal. ORM collections load by position.
Positions must be nonnegative and unique within their parent but may have gaps. Reordering will
require an importer to avoid transient unique-key collisions (for example, staged positions).

Weights use kilograms, distances metres, durations seconds and RPE the inclusive 0–10 scale.
Decimal columns avoid binary floating-point storage: four decimal places for quantities, two
for RPE. Counts and quantities are nonnegative; null means unknown, and zero is retained.
Set kind is an optional extensible string rather than a provider-specific enum. Source measurement
JSON can retain original values and units (for example `{"weight": 100, "weight_unit": "lb"}`),
while reference payloads preserve provider-specific details and original identity. No analytics
should depend on these payloads. No standalone body-measurement model is introduced in M1.

All timestamp columns use PostgreSQL `timestamptz`. Importers must supply aware UTC datetimes;
PostgreSQL stores instants rather than original timezone names. Original offsets/zone names can
remain in source payloads. End times cannot precede start times. `updated_at` is maintained by
SQLAlchemy updates, not a database trigger; direct SQL writers must set it explicitly.

The unique external key is `(user_id, provider, entity_type, external_id)`. A future importer must
use a stable provider namespace and upsert in one explicit transaction, updating the existing
canonical target, payload, source version and last-sync timestamp while retaining first-import
time. If a provider lacks child IDs, its adapter must construct stable parent-scoped identities;
position alone is not stable across reordering. One canonical entity can have references from
multiple providers; matching those entities is deliberately deferred. This schema assumes one
identity namespace per provider per user; supporting multiple accounts of the same provider
will require an explicit account namespace migration.

Deletion timestamps support source tombstones without discarding identity or raw evidence.
A source deletion does not automatically delete a canonical record shared by other providers.
Importers must define reconciliation, conflict and retention rules in M2. Hard deletion of
referenced records is blocked by foreign keys until references are explicitly removed; workout
ORM deletion removes its exercises and sets only when reference constraints permit it. There
are no automatic user deletion cascades. Raw JSON stores the latest snapshot, not an audit log.

Database ownership constraints are integrity protection, not authenticated read isolation.
No fitness routes or generic unscoped repository API are added. Before any such routes exist,
resolve identity from authentication, filter every query by that identity, and test cross-user
access denial. A caller-supplied UUID is never authorization. PostgreSQL tests now exercise
cross-user FK rejection; authenticated access tests belong with the future authentication layer.

Migration `2827ecaa5ef5` adds these four tables without altering `users`. Its downgrade removes
fitness data and restores M0 while preserving users. Tests verify both this boundary and full
base/head round trips against disposable PostgreSQL schemas.

## Planned boundaries

Provider adapters -> normalized, user-owned records -> analytics -> API -> dashboard.
Adapters handle provider credentials, pagination, mapping and provenance. Domain records define
canonical units, timestamps and identities. Analytics will use Polars on these internal records,
without importing provider clients. No unused adapter or analytics packages are created yet.
Next.js/TypeScript and the Kotlin Health Connect bridge arrive in later milestones.

Before health-data APIs exist: add authentication, mandatory user foreign keys, ownership filters,
cross-user access tests, per-user provider credentials, deletion/retention policies and appropriate
secret storage. Consider PostgreSQL row-level security as defense in depth when access patterns
are known. Never return provider secrets or put sensitive records in logs.

Reference patterns: [SQLAlchemy session lifecycle](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
and [Alembic environment configuration](https://alembic.sqlalchemy.org/en/latest/tutorial.html).

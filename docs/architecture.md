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

## Implemented Hevy mapping foundation (M2B.1)

M2B.1 supersedes the proposed fenced synchronization architecture above for the initial local,
single-user importer. No HTTP client, credential handling, endpoints, orchestration or scheduler
is implemented. The `adapters/hevy` package validates complete source snapshots and maps them
purely to provider-independent `domain/strength.py` inputs. Ownership is supplied separately by
a future trusted application boundary; source JSON never supplies authorization.

Migration `91ab` adds `source_accounts`, `account_sync_states` and `workout_tombstones`.
References require a source account and retain their existing target/ownership constraints;
uniqueness now includes the account namespace. Account IDs, owners and providers are immutable
in PostgreSQL; verified provider account identity cannot change. Active/disconnected accounts
require a nonempty verified identity. One explicit unresolved legacy account per user/provider
receives all old references without modifying their identifiers, targets, payloads or timestamps.
No legacy account is automatically verified or connected. A later binding operation must verify
identity and check conflicts transactionally; it is not implemented here. No secret locator or
credential columns are needed at this stage.

Minimal sync state stores initialization and a nullable successful **run-start** checkpoint.
The database enforces coherent initialized/checkpoint state and refuses checkpoint regression.
It cannot establish that pages completed: M2B.2 must advance this value only after all pages and
events succeed, in an explicit transaction. There are no page-offset resume cursors. Tombstones
are unique per account/workout ID and need no canonical target. A null source deletion time means
pending/unresolved; a non-null time means timestamped source evidence. Observation time never
substitutes for deletion time. Ownership/provider composite foreign keys protect all new rows.

Downgrade preserves canonical records and old reference fields. It refuses before any destructive
DDL when account namespaces would collide under M1 uniqueness. Operators must reconcile such
collisions explicitly. Successful downgrade discards account, checkpoint and tombstone metadata;
it does not reconstruct synchronization history. Stop importers before any downgrade.

Mapping requires explicit nullable fields and child arrays, preserves zero/null distinctions,
rejects malformed timestamps and nonintegral indexes/repetitions, validates nonnegative finite
measurements against storage bounds, and quantizes Decimal values with HALF_EVEN (4 quantity
places, 2 RPE places). Offset timestamps become UTC; original timestamp strings remain in the
allowlisted projection. Source indexes sort children and normalize positions, retaining original
indexes as provenance. Order mismatches and unknown fields/types yield bounded warning categories.
Unknown set types retain quantities/provenance with null canonical kind; dropset maps to drop.
Custom metrics retain numeric strings with unknown units. No completion time is invented.
Source text is kept canonically, excluded from retained projections, and included only in the
content digest. The digest is a deterministic snapshot change detector, never a revision or ID.
JSON parsing preserves decimals and limits snapshot bytes/depth; child counts are bounded.
No source model or validation error should be logged; the JSON entry point emits sanitized errors.

Distributed fencing leases, automated reconciliation, run archives and scheduled syncing are
explicitly deferred until concurrency/production operation requires them. Subsequent local sync
must serialize runs, preserve idempotency, use atomic workout/reference/child transactions, retain
first-import identity, resolve equal-time conflicts, honor tombstones and avoid advancing a
checkpoint after partial failure. These correctness requirements have not been implemented or
claimed by M2B.1. Provider account stability/feed semantics, trusted ownership, credential storage,
retention and erasure remain gates before personal imports. M2B.2 may start implementation against
synthetic transports; this foundation is not production synchronization.

### Hevy JSON and semantic hash contract

All source-model `model_validate_json()` calls and the `parse_workout`, `parse_workout_page`
and `parse_event_page` helpers share one UTF-8 decoder. Integer and fractional JSON numbers
are decoded directly to Decimal before validation. Responses must be objects; duplicate keys,
nonstandard numeric constants, invalid UTF-8, malformed JSON, responses over 4,000,000 bytes and
nesting beyond 32 levels (root at depth 0) are rejected. These bounds also inspect unknown fields.
Python-object validation remains available for already-decoded synthetic/domain inputs; callers
must not first decode source numbers through binary floats. No decoder can recover lost digits.

Accepted timestamps use calendar `YYYY-MM-DDTHH:MM:SS[.ffffff]` with `Z` or `+/-HH:MM` offset.
Fractions may contain 1 through 6 digits. Longer fractions, including trailing-zero fractions,
are rejected rather than truncated. Invalid dates, naive timestamps and UTC conversion overflow
are controlled validation errors. Original accepted strings remain in provenance; normalized
instants use UTC with exactly six fractional digits in the semantic hash.

`hevy-semantic-v1` is a SHA-256 digest of UTF-8 JSON serialized with sorted object keys, compact
separators and Python's default ASCII escaping. The preimage contains the allowlisted workout
projection, a `hash_contract` label, workout title/description and exercise titles/notes. Source
workout timestamps are replaced with normalized UTC strings; null end time stays null. Exercises
and sets are sorted by their source indexes. Original indexes, template/routine/workout IDs,
superset IDs and original set types remain significant. Incoming array order alone is not
significant when indexes agree; assigning different content to those indexes is significant.

Weight, distance and duration are rounded HALF_EVEN to 4 places, and RPE to 2 places before
hashing. Numeric hash strings use fixed-point notation without insignificant trailing fractional
zeros; positive/negative zero both become `"0"`. Custom metrics have no canonical storage unit
or rounding precision, so their exact Decimal value is hashed with the same spelling
normalization. Repetitions and indexes use validated integers. Null and zero remain distinct.
Changes below canonical measurement precision deliberately share a hash; custom-metric changes
remain significant at their full source precision. Unknown fields, warning categories and local
observation timestamps are excluded. Source created/updated instants remain significant.

The hash preimage is a separate copy: original numeric values/scale and timestamp offsets remain
in the allowlisted provenance and source measurement metadata. It is a whole-snapshot change
detector, not an ordering version, account identity or child-only digest. Downstream ingestion
must still compare source times and canonical child content separately. This replaces the initial
format-sensitive digest; any persisted older digest would need recomputation/version labeling
before comparison. No real imports or persisted hashes are introduced in M2B.1.

# Milestone 2A: Hevy API contract and synchronization design

Status: M2A reviewed and approved with the M2B.1 scope adjustments below. This document preserves
the original synchronization proposal as future design context, not a claim of implemented sync.
Reviewed 2026-11-13 against clean `main` at `5f4345dcc936ef7823e3c80dc4349c69bb410bdd`.
M2B.1 schema, pure mapping and synthetic tests are merged into main. Production imports
remain gated on credential handling, trusted ownership and the validation questions in section 11.

## Current implementation and approved scope adjustments

M2B.1 implements user-owned source accounts with immutable verified identity, account-scoped
references and legacy backfill, minimal initialization/run-start checkpoint state, account-scoped
tombstones, Pydantic read schemas and pure source-to-canonical mapping. Mapping and migration
behavior are tested with synthetic data; no API requests, authentication, endpoints, ingestion
orchestration, scheduler or real health data are included in M2B.1. M2B.2 adds the private local
HTTP client and transactional importer; see [operating instructions](hevy-importer.md).
Session advisory locks replace the original proposed distributed leases for local serialization.

The initial importer is local and single-user. Distributed fencing leases and elaborate automated
reconciliation are deferred until concurrency or scheduled production syncing requires them.
Sections 6, 9 and 10 retain original proposed production mechanisms and broader acceptance tests;
they are not requirements to add leases/jobs in M2B.1. Account namespaces, ownership constraints,
transactional integrity, idempotency, source validation and checkpoint correctness remain mandatory.
Future ingestion must serialize local runs and must not checkpoint partial or unresolved runs.

The implemented [architecture and hash contract](architecture.md#hevy-json-and-semantic-hash-contract)
is authoritative for mapping: shared bounded Decimal JSON parsing for detail/workout/event pages;
UTC-normalized timestamps with at most six fractional digits and controlled overflow rejection;
and versioned semantic hashing at canonical quantity precision, preserving original provenance
separately. Null versus zero, meaningful child ordering, source types and supported measurement
changes remain significant. No Python float decoding may precede source validation.

## 1. Evidence and confidence

Primary sources reviewed:

- [Official Hevy Swagger documentation](https://api.hevyapp.com/docs/).
- [Official Swagger initialization and embedded OpenAPI document](https://api.hevyapp.com/docs/swagger-ui-init.js),
  fetched directly without credentials. OpenAPI 3.0.0, API description version `0.0.1`.
  SHA-256 of the embedded `swaggerDoc`, serialized as UTF-8 JSON with sorted keys, compact
  separators and unescaped Unicode:
  `7d920c8a3d171499a0a87dd7e161dd2716eb211c55829fd8a4cb15b348fddbc4`.
- [Official API-key settings](https://hevy.com/settings?developer), linked by the API description.

The endpoint and field statements in section 2 describe the downloaded official specification,
not observed behavior of a live account. Its property examples were inspected, including null
measurements, `rpe: 9.5`, short template IDs, UUID-shaped workout IDs and deletion examples.
Section 3 assembles a **synthetic response illustration**, not a captured response. No personal
account tools were called and no real workout data or API keys were read or saved.

**Documented** below means stated by this specification. **Design** means our proposed policy.
**Unverified** means the specification does not establish it. Schema examples do not establish
identity stability, ordering consistency, completeness, retention or nullability guarantees.
Hevy explicitly reserves the ability to change or discontinue this API and currently restricts
it to Hevy Pro. The version string alone is not a reliable change detector.

Repository review covered `db/models.py`, both migrations (`0001`, `2827ecaa5ef5`), all four
current test modules and the architecture/roadmap/data-source documents. M1 already enforces
ownership, parent/position uniqueness, quantity bounds and exactly one external-reference target.
It has no connection namespace or synchronization checkpoint table. Existing PostgreSQL tests
cover integrity and migration round trips, not authenticated access or importer behavior.

## 2. Proposed integration contract

Base URL: `https://api.hevyapp.com`. Public REST API requests use an `api-key` header (documented
as a required UUID-formatted string). This is distinct from the connected Hevy chat tools;
those tools are not evidence for this REST contract. M2B reads only; never call provider writes.

| Operation | Documented contract | Adapter policy / limitation |
| --- | --- | --- |
| `GET /v1/workouts` | `page` starts at 1, default 1; `pageSize` default/max 10; response `{page, page_count, workouts}` | Request 10 explicitly; follow all pages; workout list order is unspecified |
| `GET /v1/workouts/{workoutId}` | Returns a Workout directly; 404 means workout not found | Use for conflicted/current state; a single 404 is not sufficient deletion evidence |
| `GET /v1/workouts/count` | `{workout_count}` | Diagnostic only; equal counts do not prove equal ID sets |
| `GET /v1/workouts/events` | Same pagination/defaults; `since` string default `1970-01-01T00:00:00Z`; events newest to oldest | Fixed lower bound for each traversal; no snapshot token or upper-bound parameter |
| Updated event | `{type: "updated", workout: Workout}` | Compare `workout.updated_at`, not reception or workout start time |
| Deleted event | `{type: "deleted", id, deleted_at}` | `deleted_at` is described but not required by schema; missing/unparseable timestamp is an unresolved tombstone |
| `GET /v1/user/info` | `{data: {id, username, name, url, weight_unit, distance_unit, is_pro}}` | Bind connection to `data.id`; exclude names/profile from persisted response |
| `GET /v1/exercise_templates/{exerciseTemplateId}` | Template definition with ID, title, type, muscles, equipment, custom flag, optional thumbnail URL | Optional account-scoped enrichment; not necessary to import workout snapshot |
| `POST /v1/workouts`, `PUT /v1/workouts/{workoutId}` | Create/update routes; PUT accepts workout body with exercise/set arrays, no child occurrence IDs | Existence of PUT supports workout-addressed edits; child identity continuity is not promised |

No workout DELETE route is present. Deletions performed elsewhere are represented by the event
feed. No separate child change/deletion feed, webhook, ETag, ordered revision number, event ID,
rate-limit quota, retention period, snapshot pagination guarantee or `since` inclusivity rule is
specified. Do not infer these guarantees. The event response requires `page`, `page_count`, `events`;
most Workout properties have no `required` declaration. Validate our minimum complete-snapshot
contract explicitly rather than treating absent arrays as empty.

Workout timestamps (`start_time`, `end_time`, `created_at`, `updated_at`) are described as ISO 8601
strings; examples use UTC `Z`. There is no workout timezone name or set completion timestamp.
Exercise/set `index` are numeric order indicators with example 0, not stable IDs. The inline
Workout schema permits nullable exercise notes, while standalone Exercise is less explicit;
accept null notes. Numeric reps/index declarations are broader than our integer semantics.

Set types described for reads: `normal`, `warmup`, `failure`, `dropset`. Read RPE is nullable
numeric without a specified range. Write RPE lists `6, 7, 7.5, 8, 8.5, 9, 9.5, 10`; this is
**not** a guarantee that reads only return those values. `custom_metric` is nullable numeric,
described as currently used for stair-machine steps/floors; the workout field alone does not
identify which unit. Weights, distance and duration fields explicitly carry kg, metres, seconds.

## 3. Synthetic response illustration

This combines documented property shapes with invented IDs, text and measurements. It is not a
fixture copied from a user, and it makes no claim about server-generated ID format requirements.

```json
{
  "page": 1,
  "page_count": 1,
  "workouts": [{
    "id": "00000000-0000-4000-8000-000000000001",
    "title": "Synthetic session",
    "routine_id": null,
    "description": null,
    "start_time": "2026-01-01T12:00:00Z",
    "end_time": "2026-01-01T12:30:00Z",
    "created_at": "2026-01-01T12:31:00Z",
    "updated_at": "2026-01-01T12:32:00Z",
    "exercises": [{
      "index": 0,
      "title": "Synthetic press",
      "notes": null,
      "exercise_template_id": "SYNTH001",
      "superset_id": null,
      "sets": [{
        "index": 0, "type": "normal", "weight_kg": 20.5, "reps": 8,
        "distance_meters": null, "duration_seconds": null,
        "rpe": 7.5, "custom_metric": null
      }]
    }]
  }]
}
```

An updated event wraps the workout in `{ "type": "updated", "workout": ... }`.
A synthetic deletion is `{ "type": "deleted", "id": "00000000-0000-4000-8000-000000000001",
"deleted_at": "2026-01-02T12:00:00Z" }` inside a paginated `events` array.

## 4. Identity and account boundaries

| Entity | Evidence | Chosen identity policy |
| --- | --- | --- |
| Workout | `id`, GET/PUT by workoutId, deletion event ID | Treat opaque source ID as stable within one account; stability across edits/restore/copy is unverified and needs a synthetic account probe |
| Exercise definition | `exercise_template_id`, template lookup | Definition ID only; may repeat within one workout; never identify an occurrence by it or title |
| Workout exercise occurrence | Only `index`, template/title/data | No documented stable occurrence ID; cannot determine continuity after arbitrary edits/reorder |
| Set occurrence | Only `index` and measurements | No documented stable ID; identical sets make matching by content ambiguous |

**Design:** create one Hevy external reference per workout. Preserve the canonical workout UUID
across accepted updates. Maintain its exercises/sets as a replaceable snapshot: unchanged accepted
content keeps existing rows; changed child content/order replaces the entire child tree atomically
with new UUIDs. Parent-only edits need not replace children. Do not create position-derived Hevy
exercise/set external references or claim stable child UUIDs across changed snapshots. A content
hash is a change detector, not a provider identity or chronological version.

This deliberately narrows architecture.md's earlier suggestion to construct stable child identities:
Hevy supplies insufficient information to do that reliably. Snapshot paths such as exercise index
and set index are provenance locators valid only in that workout snapshot. No fuzzy matching of
duplicate exercises/sets; no cross-account or cross-provider deduplication in M2B.

All imported workout trees are exclusively managed by one source connection in M2B. Do not let
other providers, manual edits or external child references attach to these trees yet. Before
replacement, verify no foreign references exist; otherwise abort with a conflict, retain the old
snapshot, and require a later merge/ownership design. Existing FK restrictions must remain enabled.

**Multiple accounts:** add a durable source-account namespace; never change `provider="hevy"`
to `hevy:<account>` or prefix an existing `external_id`. Recommended source account row has UUID,
non-null user FK, provider and immutable opaque `provider_account_id` from `/v1/user/info.data.id`.
Unique `(user_id, provider, provider_account_id)`; composite ownership/provider keys bind references
and sync state. API-key rotation/reconnect to the same verified account reuses this row. A new
provider account gets a new row and never inherits the previous account's checkpoint. A mismatch
between expected and returned account ID stops the run before any data changes.

Change reference uniqueness to `(user_id, provider, source_account_id, entity_type, external_id)`.
Require a non-null account namespace for every reference, including existing providers. Backfill
existing rows to an explicit per-user/provider **legacy unresolved namespace**, preserving IDs,
targets, original provider/external strings, timestamps and payloads. Such rows cannot sync until
explicitly bound to a verified account; never silently assign them to the first connected account.
Binding must check duplicate-key conflicts and be transactional/auditable without payload logging.
Downgrade must refuse if multiple namespaces would collide under M1 uniqueness; document the
operator reconciliation requirement rather than deleting records to make downgrade pass.

## 5. Source-to-canonical mapping and validation

All mapping is within a trusted user + verified source-account context. Never read user ownership
from source JSON or accept a caller-supplied UUID as authorization.

| Hevy source | Canonical target / retained provenance | Rule |
| --- | --- | --- |
| Workout `id` | Workout external reference `external_id` | Opaque nonempty string; no UUID coercion, case folding or concatenated account prefix |
| `title` | `Workout.title` | Required string; sensitive user text |
| `description` | `Workout.notes` | Nullable string; keep once canonically, omit from retained raw projection |
| `start_time`, `end_time` | `started_at`, `ended_at` | Aware instants to UTC; require start; allow explicit null end, reject missing end under the complete-snapshot contract; end >= start |
| `created_at`, `updated_at` | Reference `source_created_at`, `source_updated_at` | Required parseable aware values for accepted upserts; do not overwrite local creation time |
| `routine_id` | Allowlisted workout provenance only | Nullable opaque routine ID; no routine import |
| `exercises` | Ordered `WorkoutExercise` snapshot | Explicit array required, empty array valid; no partial merge |
| Exercise `index` | `position`; retain original index | Require unique nonnegative integral indexes per workout, sort ascending then normalize to contiguous 0-based positions; gaps allowed in source |
| Exercise `title` | `name` snapshot | Required string; retain custom titles only canonically |
| `exercise_template_id` | Allowlisted snapshot provenance | Definition identity, scoped by source account; do not turn into occurrence external ID |
| Exercise `notes` | `WorkoutExercise.notes` | Nullable; omit duplicated raw text |
| `superset_id` | `superset_group` | Null stays null, integer 0 becomes string `"0"`; workout-local grouping, no global identity |
| `sets` | Ordered `ExerciseSet` snapshot | Explicit array required; validate indexes independently within each exercise |
| Set `index` | `position`; retain original index | Unique nonnegative integral index within exercise; sort/normalize; array/index disagreement recorded as a contract warning, index wins |
| `type` | `kind` | `normal→normal`, `warmup→warmup`, `failure→failure`, `dropset→drop` (existing canonical convention); explicit null→null |
| Unknown set type | `kind=null`, original type retained | Import quantities with a warning; no assumptions in analytics about unknown set semantics; missing type is a malformed snapshot |
| `reps` | `repetitions` | Null or nonnegative integer; 8.0 acceptable as integral, fractional reps rejected |
| `weight_kg` | `weight_kg` | Null or nonnegative finite Decimal, kg already |
| `distance_meters` | `distance_m` | Null or nonnegative finite Decimal, metres already |
| `duration_seconds` | `duration_seconds` | Null or nonnegative finite Decimal, seconds already |
| `rpe` | `rpe` | Null or Decimal in canonical inclusive 0–10; do not enforce write enum on reads |
| `custom_metric` | `source_measurements` / allowlisted snapshot | Retain original numeric value; unit unknown unless separately verified; never map to reps/metres/duration |
| No source completion/notes fields on sets | `completed_at=null`, `notes=null` | Do not invent per-set timestamps from workout end |
| User display units | No conversion of workout fields | `weight_unit`/`distance_unit` are preferences, not workout measurement units |
| Deleted `id`, `deleted_at` | Tombstone ledger and reference `source_deleted_at` when present | Preserve identity, no fake workout for an unseen ID |

Measurement nulls are preserved and zeros are never interpreted as missing. Require each documented
measurement property to be present (nullable); a missing field is not permission to erase a stored
measurement. Reject booleans masquerading as numbers, NaN/infinity, overflow and invalid types.
Validate the whole workout before persistence; any invalid child rejects the whole snapshot.

Parse JSON numbers directly as Decimal. Quantize quantities once to 4 decimal places and RPE to
2 using ROUND_HALF_EVEN; validate range both before and after rounding against actual Numeric
precision. Retain original numeric values/units in `source_measurements` as decimal strings so JSON
storage does not reintroduce float error. Hevy REST needs no lb conversion. For future explicitly
unit-tagged inputs only: lb × 0.45359237 → kg; km × 1000 and mile × 1609.344 → metres;
minutes × 60 → seconds. Do not multiply by two for dumbbells or add/subtract body weight for
assisted/bodyweight exercise types without a separate documented load-semantics decision.

Normalize offset-aware timestamps to UTC; retain original source timestamp strings in the raw
projection for offset provenance. Reject timezone-naive strings instead of assuming local time.
No source IANA timezone is documented; local calendar analytics must mark timezone unknown until
an explicit user/account timezone policy exists. Never infer a zone from a UTC offset or current
machine timezone. Workout duration, if derived later, uses start/end instants, not local wall time.

## 6. Idempotent synchronization and transaction boundaries

### Serialization, versions and retries

One active run per `(user_id, source_account_id)`. Recommended M2B lease: persistent run token,
monotonic fencing generation and expiry in sync state, acquired by atomic database update.
Every write/checkpoint transaction locks the state row and verifies token, generation and unexpired
lease. Renewal uses the same checks. An expired worker cannot write after a replacement acquires
the lease. Keep HTTP outside DB transactions and never hold row locks while waiting on Hevy.
Lock the workout reference before mutation; account serialization handles first-insert races,
while unique constraints remain the final integrity protection. Reject disconnected accounts.

Compare UTC source `updated_at` against stored update/deletion evidence. Older updates are no-ops.
Equal timestamp + equal allowlisted content hash is a repeat; retain canonical UUIDs and
`first_imported_at`, optionally advance `last_synced_at` for a successful observation. A newer
source timestamp updates reference metadata even if semantic canonical content is unchanged.
Equal timestamp + different content is unresolved: refetch current detail, and if still ambiguous
record conflict and fail the run; never arbitrarily pick arrival order. No documented source
revision exists, so leave `source_version` null; store adapter version and content hashes in
`sync_metadata` with explicit labels. Hash deterministic allowlisted content (including canonical
text but excluding local timestamps); store hashes rather than duplicate free text.

Deletion wins ties conservatively; only a strictly newer, detail-confirmed live snapshot can clear
a tombstone. This is our conflict policy, not a documented restore guarantee. Missing deletion
time blocks ordering/checkpoint advancement for that event; preserve a pending deletion intent
and resolve via later feed evidence/manual investigation, without inventing a source timestamp.

Each accepted workout snapshot commits workout, child replacement, reference and observation
metadata in one explicit transaction. Validation failure, FK error or process interruption rolls
it all back. Whole-run atomicity is unnecessary: successfully committed workouts may remain when
a later page fails, because replay is idempotent. Do not advance the account checkpoint until every
page/event is processed or an explicitly resolved no-op. No silent quarantine-and-skip policy.

Retry timeouts, connection errors, HTTP 429 and transient 5xx with bounded exponential backoff,
jitter and a total attempt/deadline budget; honor valid Retry-After. Recheck lease after HTTP.
401/403 stop and require credential/access repair; other permanent errors stop without cursor
advance. Log only internal run IDs, bounded error categories, status and counts. Hevy asks callers
to avoid scheduling exactly on the hour; choose randomized scheduling if automation is added.

### Initial import

1. Resolve trusted owner, verify `/v1/user/info` account binding, acquire lease; record run-start
   UTC `T0` and adapter version. Keep initialization state separate from a successful checkpoint.
2. Traverse workouts from page 1 with fixed page size. Validate page shape, matching requested
   page, nonnegative page_count, finite progress/page budget; support an empty first response.
   Deduplicate by account + workout ID with version rules. Capture an ID-set digest and counts.
3. Traverse events from `T0 - overlap`, including all pages, and apply updates/tombstones. This
   catches edits/deletes during the baseline only to the extent the event feed supplies them.
4. Repeat full enumeration and catch-up when counts/page boundaries change; require two matching
   full ID-set traversals for a provisional converged baseline. Do not loop forever under churn:
   bounded attempts end as incomplete, keep committed records, leave initial import unfinished.
5. On successful baseline + catch-up, atomically mark initialized and checkpoint the run-start
   `T0` under the lease check. Never checkpoint wall-clock completion time or newest event time.

### Repeat and interrupted imports

Start the event traversal at last successful run-start checkpoint minus a configurable overlap
(proposed 5 minutes initially; not a proven provider latency bound). Hold `since` fixed across all
pages, deduplicate repeated events, use source times rather than newest-first processing order.
All pages must complete; then atomically checkpoint this run's start. On interruption/failure,
restart at page 1 with the previous checkpoint, not a saved page offset into a changing feed.
An expired lease requires a new run/fencing token even when resuming. Empty successful runs can
advance the checkpoint, subject to clock/contract checks. Refuse checkpoint regression; detect
large clock skew/future timestamps and stop for investigation rather than widening deletion logic.

Offset pagination can shift during writes and has no snapshot isolation. Overlap, repeated passes
and periodic full reconciliation reduce missed events; **they cannot prove a lossless change
stream**. Run a full reconciliation at least daily initially (randomized start), and after long
downtime, suspected feed gaps or API shape changes. Retention and maximum delivery delay are
unknown; no run may claim exactly-once delivery or mathematically complete source coverage.

### Deleted records and reconciliation

A timestamped deletion event upserts a durable account-scoped tombstone even if that workout was
never imported. This prevents a late older baseline/update from recreating it. If a reference
exists, mark its source deletion; mark the canonical workout deleted only when it is exclusively
Hevy-owned and no other live source reference exists. Children remain hidden through the deleted
parent; no hard delete and no orphaning of external references. Preserve first import and last
allowlisted snapshot until the separate retention policy permits purging sensitive content.

Changed live workout snapshots remove missing children through atomic replacement; there are no
child tombstones because the source offers no stable child identity. A tombstoned workout may
retain its current children for recovery but must be excluded from active analytics.

Never delete records merely because they are absent from a page, an interrupted scan, a changed
count, or one full ID traversal. Full reconciliation records missing candidates only after two
successful matching ID-set passes; confirm with workout detail. Even repeated 404s are provisional
without a documented distinction from access loss/consistency lag: mark source availability
uncertain, retain data, do not set a fabricated `source_deleted_at`. Explicit feed tombstones are
the M2B automatic deletion authority. Permanent feed loss may require user-approved reconciliation
policy later; report unresolved missing candidates instead of silently claiming full sync.

## 7. Safe position changes and snapshot replacement

Current immediate unique keys are `(user_id, workout_id, position)` and
`(user_id, exercise_id, position)`; negative temporary positions violate checks. ORM flush ordering
is not a collision-avoidance strategy.

M2B default: lock/validate source ownership; explicitly delete old sets then exercises, flush
those deletes, insert the validated replacement in final normalized positions, flush and commit
with the workout/reference. Rollback restores the entire previous tree. Do not rely on adding new
children to an ORM collection with pending delete-orphan operations; force the deletion boundary.
Reject replacement when any external child references or unsupported shared ownership exist.

For a future adapter with real stable child identities, use this two-phase alternative in one
transaction under the parent lock: compute `B = max(existing_max, final_max) + 1`; move every
existing sibling to distinct `B + ordinal` positions, flush; delete removed siblings in FK-safe
order; assign survivor final positions and insert new siblings, flush. Stage sets separately per
exercise. Check PostgreSQL integer capacity before staging; overflow aborts rather than wraps.
An example swap `[0,1]→[1,0]` stages at `[2,3]` first. The temporary and final ranges must be
disjoint; retain nonnegative checks and uniqueness. No deferrable-constraint migration is required
for either proposed approach. Test both exercise and set swaps on PostgreSQL if this alternative
is implemented; it is not required for Hevy's replacement strategy.

## 8. Privacy and retained source fields

`raw_payload` will mean a **sanitized allowlisted latest source projection**, not an unfiltered
HTTP body or audit archive. Keep workout ID, routine ID, original timestamp strings, exercise
indexes/template IDs/superset IDs, set indexes/types and numeric measurements/custom_metric.
This supplies workout-level provenance for children without artificial external IDs. Retain
canonical workout title, description and exercise title/notes only in their canonical columns;
these are sensitive free text, not harmless metadata. Snapshot hashes can include those values
for change detection without retaining a second copy. `source_measurements` retains only numeric
values, documented units and uncertain custom-metric semantics. Keep account ID only in the
account namespace; do not duplicate `/user/info` responses in workout payloads.

Exclude credentials, API keys, auth/cookie headers, HTTP request objects, connection URLs,
username/display name/profile URL, thumbnail URLs, social data, unrelated body measurements and
all unknown response fields by default. Do not fetch image URLs. Template enrichment may retain
only ID/type/equipment/muscle classifications if needed; custom names remain sensitive.
Unknown fields produce bounded schema-change warnings without logging values. Apply size/depth
limits before persistence. Do not log payloads, SQL bound values, hashes of credentials or provider
error bodies that may echo data. Sanitize traces and exception capture as well as application logs.

Keep only the latest allowlisted workout snapshot; no payload history or failed-response archive.
Tombstone/identity metadata must outlive replay windows; sensitive snapshot retention and user
export/erasure require an explicit policy before real imports. Disconnect disables jobs and revokes
or removes credentials, but is not implicit consent to delete canonical workouts. A user erasure
workflow must remove raw projections, canonical text/measurements and secret references together;
identity retention cannot silently override erasure requirements. Synthetic tests only in Git.

## 9. Original recommended M2B schema changes (see implemented scope above)

1. **Source accounts:** user-owned namespace described in section 4; immutable verified account ID,
   provider, status, timestamps, optional secret-manager locator (never plaintext credential).
   Legacy unresolved namespaces require a constrained state allowing no verified provider ID;
   use a partial unique index for verified identities and one unresolved row per user/provider.
   Preserve a namespace through key rotation; an operational credential is not its identity.
2. **External-reference namespace:** non-null source_account_id, composite
   `(user_id, provider, source_account_id)` FK to an account unique key, replace unique source key
   as specified above. Existing canonical target/ownership constraints stay intact.
3. **Account sync state:** one user-owned row per source account with composite ownership FK,
   initialized flag, successful run-start checkpoint, lease token/generation/expiry, last outcome
   and minimal count/error categories. A page offset is diagnostic only, not a resume cursor.
4. **Workout tombstone ledger:** user/account/provider-scoped opaque workout ID, nullable source
   deletion instant, observed-at, pending/confirmed status and latest conflict metadata; unique
   source identity, independent of canonical target so unseen deletes are representable. Enforce
   account/owner/provider matching. Confirmed means a valid source timestamp, not local inference.
5. **Optional bounded run summary:** only if needed for operations; non-null user/account ownership,
   start/end/status/counts, no raw payloads. Prefer sync-state metadata initially; do not add an
   unused job framework or permanent event archive.

No new exercise taxonomy, provider-specific canonical columns, child stable-ID columns or numeric
schema changes are currently required. No schema changes occurred in M2A. M2B.1 has applied the minimal subset described above. M2B must use reviewed
Alembic migrations with upgrade/backfill/downgrade paths and tests. A downgrade with account
collisions must stop before dropping constraints/tables. Downgrading while imports/jobs run is
unsupported; disable jobs first. Schema removal necessarily loses new sync/tombstone metadata,
which must be documented rather than represented as reversible operational history.

## 10. Detailed M2B implementation sequence and acceptance tests

1. Approve namespace, child replacement, deletion authority and data-retention decisions. Recheck
   official spec/hash; resolve API account-binding and synthetic-edit probes below. Implement
   secure credential injection and trusted local operator ownership for any private import tool.
   No health-data HTTP routes until authentication and isolation tests are complete.
2. Add reviewed account/reference/state/tombstone migrations and SQLAlchemy typed models, including
   legacy backfill and refusal-on-collision downgrade. Exercise upgrade from M1 and base/head
   round trips on disposable PostgreSQL, preserving users, old references and canonical targets.
3. Add Pydantic source schemas and pure adapter mapping to provider-independent normalized inputs.
   Build invented fixtures matching documented shapes, including updated/deleted envelopes, empty
   pages and malformed snapshots. Add Decimal/timestamp/order tests before introducing HTTP.
4. Add a read-only modular Hevy HTTP adapter with injected transport/credentials/clock, explicit
   timeouts, bounded retries, pagination/size guards and sanitized errors. Use HTTP mocks only in
   repository tests; no dependency on personal account access or real exports.
5. Add account-scoped orchestration, fencing, version checks and explicit per-workout transaction
   boundaries. Add initial import + event catch-up + reconciliation, tombstone ledger and atomic
   child replacement. Keep configuration, persistence, adapter and future domain logic separate;
   analytics must never consume Hevy raw payloads. Keep routes thin if routes are later authorized.
6. Provide a private operator entry point only after ownership/secrets/retention gates are met;
   document setup, initial/repeat invocation, failure recovery, disconnect and safe reconciliation.
   Do not expose account IDs or user IDs as authorization. No UI, provider writes or analytics in M2B.
7. Run required pytest/Ruff checks and disposable PostgreSQL integration tests. Completion requires
   the following scenarios; API mock tests alone cannot validate uniqueness/locking behavior.

| Test group | Required assertions |
| --- | --- |
| Repeat/retry | Reimport identical snapshots/pages and retry after commit-before-ack; no duplicate workouts/references, unchanged child UUIDs, first-import preserved; newer metadata-only update does not churn children |
| Pagination | Multiple/empty pages, duplicate IDs/events, shrinking/growing page counts, invalid page metadata, bounded nonconvergence, fixed since, newest-first events arriving out of source-time order |
| Initial import races | Insert/edit/delete during baseline, restart baseline after interruption, unseen deletion before old snapshot; no initialization/checkpoint on incomplete scan |
| Stale updates | Older updates ignored, equal timestamp/equal hash no-op, equal timestamp/different hash conflict, source timestamp precision ties, future clock skew, restore strictly newer than deletion |
| Concurrency | Two workers contend for same account, lease expires during HTTP, fenced old worker cannot commit/checkpoint, two accounts may run independently; unique-key race rollback/retry |
| Partial failures | Failure before/after delete flush, midway through child inserts, reference update, final checkpoint, timeout and process death; old tree intact on failed workout and cursor unchanged on failed run |
| Deletion | Repeated/unknown timestamped tombstones, missing deletion time, stale resurrection, deletion wins tie, shared reference prevents canonical deletion, transient 404 never deletes, deleted parent excluded from active reads |
| Reorder/removal | Exercise swap, set swap, insertion at front, duplicate templates, identical sets, gaps, mismatched array/index order; exact desired ordering/no unique violation; changed children get new UUIDs; no fabricated continuity |
| Foreign references | Replacement aborts before mutation if child belongs to another reference; no cascaded deletion of provenance or silent reassignment of shared canonical data |
| Mapping | Null vs zero vs missing, RPE 0/9.5/10 and invalid values, all supported/unknown types, custom metrics, fractional reps/index rejection, negative/overflow/nonfinite values, rounding boundaries, offset UTC/DST/naive timestamps |
| Multi-account/isolation | Same external ID under two accounts and two users stays distinct; reconnect/key rotation preserves namespace; wrong account/user rejected before reads/writes; composite FKs reject cross-owner rows |
| Security | Secrets absent from repr/logs/traces/errors/raw projections; unknown fields excluded; synthetic sensitive free text not duplicated; request size limits; disconnect halts fenced jobs |
| Migration | Legacy tuple meaning preserved; verified account binding conflict rollback; downgrade refusal for colliding accounts; clean reversible empty/single-account upgrade and downgrade; Alembic metadata check |

## 11. Unresolved questions, risks and readiness

- **Provider identity:** docs expose `/v1/user/info.data.id`, but permanence across key rotation,
  username changes and reconnect is not explicitly promised. Verify with a dedicated synthetic
  account before using real credentials. Use synthetic workouts for lifecycle tests. M2B.3A permits only the [bounded in-memory contract check](hevy-importer.md#verify-one-live-sample-m2b3a) on a trusted personal account.
- **Workout continuity:** verify edit/title change/reorder preserve workout ID; copy/restore may
  create new IDs. Child continuity is intentionally unsupported unless Hevy adds occurrence IDs.
- **Feed semantics:** ask Hevy or probe synthetic records for `since` inclusive/exclusive behavior,
  timestamp resolution, delayed events, retention, duplicate/coalesced events, creation events,
  delete/restore behavior, and completeness of embedded updated snapshots. No documented cursor
  can eliminate concurrent-pagination loss; daily reconciliation remains necessary and provisional.
- **Deletion certainty:** missing deletion timestamps and expired tombstones cannot be solved by
  inventing data. Confirm whether 404 ever means permissions or eventual consistency; until then,
  missing-record reconciliation reports uncertainty. Strict exact mirroring is not yet guaranteed.
- **Read shapes:** validate null/missing end times and measurement fields, zero-workout page_count,
  integer index scope, write/read RPE differences, allowed negative assisted loads, superset IDs,
  custom-metric units and new set types. Unsupported snapshots fail closed without partial writes.
- **Operational limits:** quotas, retry guidance and clock/latency bounds remain unspecified;
  provisional overlap/schedule/budgets require measurement on synthetic traffic and tuning.
- **Privacy/access:** choose secret storage, credential rotation, retention duration and erasure
  workflow before importing personal data. Authentication does not exist at this baseline;
  trusted local ownership is required even for an operator tool, and health routes remain gated.
- **Product tradeoff:** child UUIDs change after child snapshot edits. Any future annotations,
  cross-provider merge or analytics cache keyed by child identity needs a separate design.

M2B.1's migrations, pure mapping and synthetic test foundation are merged. M2B.2 implements the
local client/importer on main with synthetic transport and PostgreSQL validation. This does not establish
production synchronization correctness or readiness to import personal data:
account binding, synthetic API validation and privacy/access decisions remain explicit gates.

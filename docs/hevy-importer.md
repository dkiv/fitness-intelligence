# Local Hevy synchronization (M2B.2)

The importer reads Hevy and writes to local PostgreSQL. For M2B.3A use only the [verification procedure](#verify-one-live-sample-m2b3a). There are no health-data HTTP routes, provider writes,
scheduler, analytics or UI. PostgreSQL 17 and Python 3.12+ are required. The operator must already
control the local OS account and the database. A UUID supplied by a remote caller is never an
authorization mechanism. Do not expose this CLI through a server, shared shell or multi-user service.

## Setup and binding

Install with `cd backend && uv sync --frozen`; apply `uv run alembic upgrade head` with
`DATABASE_URL` injected into the environment. M2B.2 adds a pending flag to the tombstone ledger so an undated deletion can block progress
without erasing earlier dated deletion evidence. The migration includes a guarded downgrade; resolve pending deletions before reverting it. Never downgrade during synchronization. Use synthetic data until the live-import gates
below are addressed. Keep database access restricted and backups protected.

Obtain a Hevy Pro API key from the [official settings](https://hevy.com/settings?developer).
Inject `HEVY_API_KEY` and `DATABASE_URL` through a local secret manager or an interactive shell
without echo or shell-history literals. Do not put keys in arguments, Git, fixtures or logs.
The CLI does not persist credentials, including rotated keys. Environment credentials can be read
by processes with sufficient local privileges; this is a single trusted OS operator boundary.

Provision a canonical user and verified, active source account through a trusted local database
administration session. Reuse an existing user only after checking ownership outside this tool.
The following bootstrap example creates a **new local user** and account, verifies the credential
against `/v1/user/info`, and writes the private binding. It must be run from `backend/` with the
environment injected. It is an explicit administrative action, not a public registration flow.
Do not repeat it for key rotation; reuse the existing binding for the same provider account.

```python
# Run in `uv run python` in a trusted local terminal. No key literals.
import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fitness_intelligence.adapters.hevy.client import HevyClient
from fitness_intelligence.db.models import SourceAccount, User

client = HevyClient(os.environ["HEVY_API_KEY"])
try:
    identity = client.identity()
finally:
    client.close()
engine = create_engine(os.environ["DATABASE_URL"], echo=False, hide_parameters=True)
with Session(engine) as session, session.begin():
    user = User()
    session.add(user)
    session.flush()
    account = SourceAccount(user_id=user.id, provider="hevy",
                            provider_account_id=identity, status="active")
    session.add(account)
    session.flush()
    binding = dict(user_id=str(user.id), source_account_id=str(account.id),
                   provider_account_id=identity)
engine.dispose()
folder = Path.home() / ".config" / "fitness-intelligence"
folder.mkdir(mode=0o700, parents=True, exist_ok=True)
path = folder / "hevy.json"
with open(path, "x", opener=lambda p, flags: os.open(p, flags, 0o600)) as stream:
    json.dump(binding, stream)
```

If binding-file creation fails, the account is already committed; retrieve its IDs from the trusted
administration session instead of creating another user. For existing users/accounts, construct the
same three-field JSON after verifying ownership. Use a private directory and mode `0600`. The CLI
opens without following symlinks and checks file type, size, ownership (real OS UID) and
permissions on the opened descriptor. Binding identities must also match an active database account
and the identity returned for the current key. Legacy unresolved accounts are rejected; explicit
legacy reconciliation/binding remains an operator task. Never silently transfer legacy references.

## Verify one live sample (M2B.3A)

1. Use a private, access-controlled workstation with encrypted storage (including swap and the database volume). Close debuggers, disable core dumps (`ulimit -c 0` in the calling shell), shell tracing, profiling, request capture, SQL parameter logging and crash uploads. Keep binding files, database files, exports and backups outside Git and cloud-synced directories. Check that the binding directory is owned by the operator and has mode 0700, including when it already exists.
2. Confirm the local user and expected Hevy account through a trusted operator session. Check that the active Hevy source account belongs to that user. If the expected account cannot be established independently, stop. Bootstrap above provisions identity metadata only. Use a short-lived shell with the key injected from a local secret manager. On suspicion of exposure revoke/rotate at Hevy, verify the replacement against the existing binding and close the shell.
3. From `backend/`, use a PostgreSQL role with only connection, schema usage and SELECT access to `source_accounts` for the verification command. Inject its connection string as `DATABASE_URL`. The verifier checks the private binding against that table, compares the identity from `GET /v1/user/info`, then requests only page 1 of `GET /v1/workouts` with `pageSize=1`. It uses the importer’s bounded parser and pure mapping in memory. Transient errors can retry the same request. The client disables environment proxies and redirects. Verification rejects TLS key logging.
4. Run this exact command. Omitting `--verify-only` selects the transactional importer.

```sh
uv run --frozen python -m fitness_intelligence.adapters.hevy.cli --verify-only \
  --binding "$HOME/.config/fitness-intelligence/hevy.json"
```

Record only the fixed outcome and exit status. An empty page verifies the envelope only. Failure is inconclusive; check local configuration or reproduce with synthetic fixtures. Never save a live response for troubleshooting. Success covers one identity comparison and the observed list shape. Detail, events, lifecycle, pagination stability and deletion behavior require separate controlled synthetic-account tests.

### Storage and recovery gates before a personal import

- Record who controls the single-user database, its volume, the OS credentials and backup keys. Restrict PostgreSQL to local access. Compose loopback binding alone does not establish encryption or exclusive ownership.
- Rehearse a backup and restore with synthetic records first. Use PostgreSQL 17 tools, a private encrypted directory and `umask 077`. With private libpq service entries for the source and a **new empty disposable target**, run `pg_dump -Fc -d service=fi_source -f "$private_dir/fitness.dump"` then `pg_restore --exit-on-error --single-transaction --no-owner --no-acl -d service=fi_restore "$private_dir/fitness.dump"`. Verify the migration revision, synthetic owner/account, workout tree and checkpoint on the restored target. Restrict restored access before use. Test recovery of the binding and backup keys separately. A successful database restore alone does not authorize a personal import.
- Agree on a retention period for canonical workouts (including soft-deleted rows), references, tombstones, checkpoints, backups and exports. Record the owner, expiry and cleanup procedure. There is no automatic purge.
- Rehearse an owner-scoped export and erasure on synthetic records, verifying coverage of related records and exclusion of other owners. Disconnect the source and revoke its key first for erasure. Include binding files, exports, backup expiry and how erasure will be reapplied after restoration. No owner-facing export/erasure implementation exists. A whole-database dump is only suitable for private disaster recovery.
- Leave personal imports blocked until the owner approves these policies, verifies recovery and erasure, and resolves the provider-contract gates below. M2B.3A authorizes only the in-memory check.

## Run synchronization (synthetic data only)

From `backend/`, with the two secret environment variables injected:

```sh
uv run python -m fitness_intelligence.adapters.hevy.cli \
  --binding "$HOME/.config/fitness-intelligence/hevy.json"
# Full reconciliation: run at least daily and after long downtime or suspected feed gaps.
uv run python -m fitness_intelligence.adapters.hevy.cli \
  --binding "$HOME/.config/fitness-intelligence/hevy.json" --reconcile
```

The first run enumerates all workouts and catches up events from run-start minus five minutes.
It requires two successive equal workout ID sets (at most three enumerations), with complete event
traversals after each enumeration. Later runs request events from the previous successful run-start
minus five minutes. Every traversal restarts at page one, with a fixed `since` and page size 10.
Changing page counts, invalid pages or more than 10,000 pages fail the run. Empty page-count zero
and an empty first page with page-count one are accepted. A nonterminal empty page is rejected.
The five-minute overlap is provisional; it is not a verified provider delivery bound.

One dedicated PostgreSQL connection holds a session advisory lock for the account for the entire
run. Competing runs fail immediately; other accounts proceed independently. HTTP runs outside
write transactions. Each accepted workout, replacement child tree and reference commits together.
Run-start checkpoints commit only after all required traversals and pending-deletion checks succeed.
Committed snapshots survive later page failures and are safe to replay. No page offset is saved.
All importer writers must use this serialization path; direct concurrent database administration
or future alternative writers require coordination. A killed process releases its lock when its
connection closes; a hung network connection may delay release. There is no distributed lease.

Updates compare UTC source timestamps and the M2B.1 semantic hash, preserve workout UUIDs and
first-import time, ignore older snapshots, and retain child UUIDs for unchanged normalized trees.
Changed children are deleted in FK-safe order, flushed and replaced atomically with fresh UUIDs.
Child external references or another workout source reference block mutation, including deletion.
Equal-time/different-hash updates refetch detail and fail if ambiguity remains. A strictly newer,
detail-confirmed snapshot can restore a tombstoned workout. Deletion wins timestamp ties. Tombstone
history remains durable even after restoration; canonical workout/children are never hard-deleted.

Explicit deletion events create account-scoped tombstones, including unseen IDs. Missing deletion
timestamps persist pending intent and fail the run. Invalid timestamps reject the page before
application. Neither case advances the checkpoint. Reconciliation compares source IDs against live
references; missing IDs trigger detail reads but remain unresolved even if detail is available.
A 404 never implies deletion. Such a run retains data and leaves the previous checkpoint intact.
A repeated deletion at or before the last confirmed deletion time cannot clear pending intent.
Only strictly newer timestamped deletion evidence can automatically clear it (an unverified
provider policy); otherwise operator investigation is required. Updates encountered while pending
are deferred so later deletion evidence can be read, but the run still fails without checkpointing
until a fresh replay processes those updates. Unresolved states require later feed evidence or deliberate operator investigation; there is no
quarantine-and-skip or automatic destructive repair command.

## Failures and diagnostics

Transport has connect/pool timeouts of five seconds, read/write timeouts of twenty seconds,
four attempts maximum, exponential backoff with jitter, a ninety-second retry deadline and a
four-megabyte decompressed response limit. The deadline is checked between attempts and response
chunks; a currently blocked network operation can overrun it by its socket timeout. Only transport
errors, 429 and 5xx retry. Valid Retry-After seconds or HTTP dates are honored up to thirty seconds;
longer waits fail for a later operator retry. Redirects and other 4xx fail immediately. Every API
operation is GET against the fixed official HTTPS origin. Decimal JSON validation precedes mapping.

Lock acquisition/cleanup failures invalidate the dedicated connection rather than returning a
session advisory lock to the pool. A cleanup failure after checkpoint commit cannot undo that
commit; inspect checkpoint state and safely replay instead of assuming it did not advance.
The CLI exits nonzero with a generic sanitized message on failure and prints a fixed success
message otherwise. It emits no provider response bodies, profile fields, credentials, SQL parameters
or health payloads. Library `HevyError` categories distinguish operational failures for trusted
local debugging. Avoid enabling HTTP/SQL wire logging, collecting exception locals or printing
unsanitized database exceptions. The CLI intentionally suppresses tracebacks. Provider 401/403
requires credential/access repair; retries cannot fix ownership conflicts or malformed snapshots.
Source timestamps more than five minutes ahead of the local clock and checkpoint regression stop
synchronization. Fix the clock; do not rewrite timestamps to force progress.

## Contract evidence, limitations and live-import gates

Re-fetched the [official Swagger initializer](https://api.hevyapp.com/docs/swagger-ui-init.js) on
2026-11-13. Its canonical embedded specification SHA-256 remains
`7d920c8a3d171499a0a87dd7e161dd2716eb211c55829fd8a4cb15b348fddbc4`, matching M2A.
Read paths, identity shape, api-key header and pagination match the approved design. No credentialed
calls or real workout imports were made during implementation. Automated tests use synthetic data.

Still unverified: stable workout/account identity under account lifecycle changes; ordering and
snapshot consistency during offset pagination; event creation/retention/delivery and `since`
inclusivity; source timestamp resolution; restore semantics and 404 meaning; actual quotas and
Retry-After behavior; nullable/missing read fields, assisted loads and custom-metric units.
Overlap and repeated enumeration cannot guarantee lossless synchronization. Reconciliation is
operator-invoked and must be run regularly; no unattended scheduling or exact-mirror claim exists.

Before personal-data import, approve retention, export/erasure, backup and credential-rotation
policies; establish the trusted local owner and account binding; and validate uncertain behaviors
using synthetic workouts in a controlled provider account. Sensitive canonical text and numeric
measurements remain in the database even after source deletion. No retention purge is implemented.
Authentication is still required before exposing any health-data endpoint.

## Validation

Run the full repository commands from `backend/` with `TEST_DATABASE_URL` set to a disposable
PostgreSQL database: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`.
PostgreSQL fixtures create isolated schemas and apply all migrations. Existing migration tests
check upgrade/downgrade/re-upgrade and Alembic metadata drift. SQLite-only runs are insufficient.

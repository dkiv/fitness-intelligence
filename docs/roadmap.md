# Roadmap

- **M0: Project foundation (complete).** Repository, documentation, FastAPI health endpoint,
  PostgreSQL, user identity model, Alembic, tests and local Compose. No integrations, AI or UI.
- **M1: Canonical data model and ownership (complete).** Canonical strength schema, database-enforced
  ownership links, synthetic constraint and migration tests. Authentication and authorized data
  access remain required before exposing fitness endpoints.
- **M2: Hevy ingestion.**
  - **M2A: API contract and synchronization design (reviewed and approved with adjustments).** Official documentation reviewed;
    [integration design](hevy-sync-design.md) records mapping, identity limits, account namespaces,
    synchronization and M2B acceptance criteria. M2A itself introduced no schema changes.
  - **M2B.1: Schema and pure mapping (merged).** Source-account
    namespaces, legacy migration, minimal checkpoint/tombstone storage, strict source schemas,
    pure mapping and synthetic PostgreSQL/regression tests. No live API requests or ingestion.
  - **M2B.2: HTTP client and transactional importer (implemented on feature branch).** Read-only
    transport, account-serialized historical/incremental import, atomic snapshots, tombstones,
    checkpoint safety and a private local CLI. See [operating instructions](hevy-importer.md). Distributed fencing and elaborate automated
    reconciliation are deferred until concurrency or scheduled production syncing requires them.
    Idempotency and checkpoint correctness remain mandatory. Personal imports remain gated on
    trusted ownership, secrets and retention decisions.
- **M3: Garmin ingestion.** Validate Garmin Personal API access; implement a separate adapter
  for running, sleep, HRV and resting heart rate with user-scoped, idempotent imports.
- **M4: Health Connect integration.** Kotlin bridge with permissions and sync for RENPHO-origin
  weight and MyFitnessPal-origin calorie intake; validate upstream record availability first.
- **M5: Analytics and dashboard.** Provider-independent Polars longitudinal calculations,
  followed by a Next.js/TypeScript dashboard with documented missing-data behavior.
- **M6: Personalized intelligence.** Validate personalized performance recommendations and
  address privacy, retention/deletion, operational safeguards and public-release requirements
  before launch.

The remainder of M2 and M3 through M6 are planned, not implemented. Strava remains out of scope.

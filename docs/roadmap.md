# Roadmap

- **M0: Project foundation (current).** Repository, documentation, FastAPI health endpoint,
  PostgreSQL, user identity model, Alembic, tests and local Compose. No integrations, AI or UI.
- **M1: Canonical data model and ownership.** Authentication design, enforced user isolation,
  canonical measurement/workout schema, synthetic fixtures and access tests.
- **M2: Hevy ingestion.** Validate API access; implement a modular adapter, per-user connections,
  idempotent workout imports and provenance.
- **M3: Garmin ingestion.** Validate Garmin Personal API access; implement a separate adapter
  for running, sleep, HRV and resting heart rate with user-scoped, idempotent imports.
- **M4: Health Connect integration.** Kotlin bridge with permissions and sync for RENPHO-origin
  weight and MyFitnessPal-origin calorie intake; validate upstream record availability first.
- **M5: Analytics and dashboard.** Provider-independent Polars longitudinal calculations,
  followed by a Next.js/TypeScript dashboard with documented missing-data behavior.
- **M6: Personalized intelligence.** Validate personalized performance recommendations and
  address privacy, retention/deletion, operational safeguards and public-release requirements
  before launch.

M1 through M6 are planned, not implemented. Strava remains out of scope.

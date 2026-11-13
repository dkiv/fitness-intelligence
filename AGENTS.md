# Coding conventions

- Scope changes to the current milestone. No external integrations, AI, or UI in Milestone 0.
- Python 3.12+, explicit type hints, SQLAlchemy 2 typed models, Pydantic API schemas.
- Keep routes thin; isolate configuration, persistence, future domain logic and adapters.
- Future analytics use normalized domain inputs and Polars, never provider-specific payloads.
- Every future user-owned record must carry a non-null user foreign key. Scope every query
  by authenticated user identity; do not trust a caller-supplied user ID as authorization.
- UUIDs are identifiers, not access control. Authentication and isolation tests are required
  before exposing health data or provider credentials.
- Use Alembic for all schema changes. Review generated migrations and include downgrade paths.
- Use a session per request; commit explicitly at the application transaction boundary.
- UTC-aware timestamps; document units and source provenance for future measurements.
- Never commit credentials, tokens, real health data, database dumps, or identifying fixtures.
  Use synthetic test data. Do not log health payloads, connection URLs or tokens.
- Run `cd backend && uv run pytest && uv run ruff check . && uv run ruff format --check .`.
  Run PostgreSQL tests against a disposable database when changing models or migrations.
- Keep setup commands and product documentation current. Add dependencies only when used.
- Future frontend: Next.js with strict TypeScript; Android bridge: Kotlin. Neither exists yet.

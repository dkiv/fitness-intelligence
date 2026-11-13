# Fitness Intelligence

Longitudinal analytics across strength, endurance, recovery, nutrition and body weight.
Users keep their existing tracking apps. **Milestones 0 and 1** are implemented: API foundation, user-owned canonical strength models,
migrations and tests. No integrations, authentication, AI or web UI.

## Repository

- `backend/src/fitness_intelligence/`: API, settings and persistence
- `backend/migrations/`: versioned schema
- `backend/tests/`: synthetic API and database tests
- `docs/`: [vision](docs/product-vision.md), [architecture](docs/architecture.md),
  [roadmap](docs/roadmap.md), [data sources](docs/data-sources.md)
- `AGENTS.md`: contribution conventions

## Docker development

Prerequisite: Docker with Compose v2 and a running daemon. From the repository root:

```sh
cp .env.example .env
# Edit .env: replace the example password in BOTH password and URL.
# Use a URL-safe password (for example: openssl rand -hex 24).
docker compose up --build -d
curl --fail http://localhost:8000/health
# Expected: {"status":"ok"}
docker compose logs migrate api
```

Compose waits for PostgreSQL, runs `alembic upgrade head`, then starts the API.
API docs: http://localhost:8000/docs. Source edits reload automatically.
After model/migration changes, rebuild and recreate the migration service:

```sh
docker compose up --build --force-recreate -d migrate api
```

Stop with `docker compose down`; the named database volume persists. Changing initial Postgres
credentials does not change an existing volume's database credentials. Never use production data.
The local password in `.env` is a development secret and must not be committed.

## Local Python development

Prerequisites: Python 3.12+ and [uv](https://docs.astral.sh/uv/), plus PostgreSQL 17
(or the Compose database). Run from repository root after configuring `.env` as above:

```sh
docker compose up -d db
cd backend
uv sync --frozen
# Explicitly use the root env file; no shell sourcing required.
uv run --env-file ../.env alembic upgrade head
uv run --env-file ../.env uvicorn fitness_intelligence.main:app --reload
```

In another terminal, `curl --fail http://localhost:8000/health`.
If using existing local PostgreSQL, create a database/user and set DATABASE_URL accordingly.
Run all backend commands from `backend/`; dependencies are locked in `uv.lock`.

## Tests and checks

```sh
cd backend
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The default suite uses in-memory SQLite for a portable model smoke test and skips the PostgreSQL
integration tests. SQLite alone does not validate PostgreSQL behavior. Run the full suite with
Compose (from repository root, after `docker compose up --build -d`):

```sh
docker compose exec api sh -c 'TEST_DATABASE_URL="$DATABASE_URL" uv run --no-sync pytest'
```

Or, from `backend/`, set TEST_DATABASE_URL to a disposable PostgreSQL database:

```sh
TEST_DATABASE_URL='postgresql+psycopg://USER:PASSWORD@localhost:5432/TEST_DB' uv run pytest
```

PostgreSQL tests use unique temporary schemas, exercise ownership and measurement constraints,
ordering, external identities, upgrades, metadata drift checks, downgrade and re-upgrade,
then remove those schemas. Downgrading M1 preserves existing users. The test account needs
schema creation privileges. Never point tests at production. No real health data is used.

## Migrations

From `backend/`, with a configured root `.env`:

```sh
uv run --env-file ../.env alembic current
uv run --env-file ../.env alembic revision --autogenerate -m "describe change"
# Review the generated migration before applying it.
uv run --env-file ../.env alembic upgrade head
uv run --env-file ../.env alembic check
```

`/health` reports process liveness only. Database availability is checked separately by
Compose and migration/tests. User IDs currently provide a schema foundation; authentication
and enforced isolation must precede any health-data endpoints. See the roadmap for next steps.

# Architecture

## Current implementation

A monorepo contains a Python backend, migrations, tests and shared documentation. FastAPI exposes
`GET /health` as process liveness; it intentionally does not query PostgreSQL. Pydantic Settings
loads DATABASE_URL only when database access is needed. SQLAlchemy uses synchronous psycopg
connections and request-scoped sessions. Routes using blocking database operations should be
synchronous. Alembic owns schema creation; application startup does not create tables.

The users table contains a UUID primary key and a server-generated timestamp. No email, password,
authentication or health data is stored. This is an ownership foundation, not implemented tenant
security. UUID generation happens in the ORM; direct SQL inserts must supply an ID.

Compose runs PostgreSQL, a one-shot migration service, and the development API. Ports bind to
localhost. Development data lives in a Docker volume. This configuration is not public hosting.

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

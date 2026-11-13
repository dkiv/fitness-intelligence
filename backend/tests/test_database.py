import os
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fitness_intelligence.db.models import Base, User


def test_user_identity_and_primary_key() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        first, second = User(), User()
        session.add_all([first, second])
        session.commit()
        assert isinstance(first.id, UUID)
        assert first.id != second.id
        assert first.created_at is not None
        identity = first.id
    with Session(engine) as session:
        session.add(User(id=identity))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    engine.dispose()


@pytest.mark.postgres
def test_postgres_migration_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to a disposable PostgreSQL database")
    # Use a unique schema so this test never drops existing application tables.
    from uuid import uuid4

    schema = "test_" + uuid4().hex
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
    from sqlalchemy.engine import make_url

    test_url = make_url(url).update_query_dict({"options": f"-csearch_path={schema}"})
    monkeypatch.setenv("DATABASE_URL", test_url.render_as_string(hide_password=False))
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    isolated = create_engine(test_url)
    try:
        command.upgrade(config, "head")
        command.check(config)
        with Session(isolated) as session:
            user = User()
            session.add(user)
            session.commit()
            assert session.scalar(select(User.id)) == user.id
            assert user.created_at.tzinfo is not None
        command.downgrade(config, "base")
        assert "users" not in inspect(isolated).get_table_names()
        command.upgrade(config, "head")
    finally:
        isolated.dispose()
        with engine.begin() as connection:
            connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        engine.dispose()

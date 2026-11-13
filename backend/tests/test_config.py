import pytest
from pydantic import ValidationError

from fitness_intelligence.config import Settings


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_database_url_is_not_exposed_in_settings() -> None:
    settings = Settings(database_url="postgresql+psycopg://test:synthetic-secret@localhost/test")
    assert "synthetic-secret" not in repr(settings)
    assert settings.sqlalchemy_url().startswith("postgresql+psycopg://")


def test_rejects_unsupported_database_driver() -> None:
    with pytest.raises(ValueError):
        Settings(database_url="sqlite:///test.db").sqlalchemy_url()

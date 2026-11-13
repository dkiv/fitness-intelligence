from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from fitness_intelligence.config import Settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(Settings().sqlalchemy_url(), pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """One session per request. The caller explicitly owns commit/rollback."""
    with Session(get_engine()) as session:
        yield session

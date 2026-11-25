"""Shared private operator file and PostgreSQL account serialization."""

import json
import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import Engine, text
from sqlalchemy.orm import Session


class LocalAccountError(Exception):
    pass


def private_config(path: Path) -> dict[str, Any]:
    # Open without following symlinks, then check the opened file to avoid TOCTOU races.
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor) as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_size > 4096
        ):
            raise LocalAccountError("binding must be an operator-owned mode 0600 regular file")
        data = json.loads(stream.read(4097))
        if not isinstance(data, dict):
            raise LocalAccountError("invalid binding")
        return data


@contextmanager
def locked_account(engine: Engine, source_account_id: UUID) -> Iterator[Session]:
    # Dedicated connection: session advisory lock survives per-snapshot commits.
    # A crashed process releases it when PostgreSQL closes the connection.
    key = int.from_bytes(sha256(str(source_account_id).encode()).digest()[:8], "big", signed=True)
    with engine.connect() as connection:
        if connection.dialect.name != "postgresql":
            raise LocalAccountError("PostgreSQL required")
        try:
            locked = connection.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": key})
            connection.commit()
        except BaseException:
            # Acquisition may have succeeded before a commit/connection failure.
            connection.invalidate()
            raise
        if not locked:
            raise LocalAccountError("account synchronization already running")
        try:
            with Session(connection, expire_on_commit=False) as session:
                yield session
        finally:
            try:
                connection.rollback()
                connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})
                connection.commit()
            except BaseException:
                # Rollback/pool reset cannot release session advisory locks.
                connection.invalidate()
                raise

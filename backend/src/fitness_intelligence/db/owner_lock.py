"""Owner row shared by planning decisions and source mutations. Caller owns the transaction."""

import os
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import User


def trusted_owner() -> UUID:
    binding = os.environ.get("FITNESS_PLANNING_OWNER_ID")
    if not binding:
        raise PermissionError("trusted local planning owner binding required")
    return UUID(binding)


def lock_owner(db: Session, owner: UUID) -> None:
    conn = db.connection()
    if conn.dialect.name == "postgresql" and conn.connection.driver_connection.autocommit:
        raise ValueError("owner lock requires an active database transaction")
    with db.no_autoflush:
        db.execute(select(User.id).where(User.id == owner).with_for_update()).one()

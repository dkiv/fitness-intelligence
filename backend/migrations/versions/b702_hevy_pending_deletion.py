"""Preserve unresolved deletion intent alongside earlier confirmed evidence.

Revision ID: b702_hevy_pending
Revises: 91ab
"""

import sqlalchemy as sa
from alembic import op

revision = "b702_hevy_pending"
down_revision = "91ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workout_tombstones",
        sa.Column("pending", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    # Removing unresolved intent could permit unsafe checkpoint advancement.
    connection = op.get_bind()
    if connection.scalar(sa.text("SELECT EXISTS (SELECT 1 FROM workout_tombstones WHERE pending)")):
        raise RuntimeError("Resolve pending Hevy deletions before downgrade")
    op.drop_column("workout_tombstones", "pending")

"""Record retrieval and source provenance on bounded recovery observations."""

import sqlalchemy as sa
from alembic import op

revision = "b301"
down_revision = "b201"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "daily_recovery_observations", sa.Column("retrieved_at", sa.DateTime(timezone=True))
    )
    for name in ("mapping_version", "source_field"):
        op.add_column("daily_recovery_observations", sa.Column(name, sa.String()))


def downgrade() -> None:
    op.execute("LOCK TABLE daily_recovery_observations IN ACCESS EXCLUSIVE MODE")
    if op.get_bind().scalar(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM daily_recovery_observations "
            "WHERE retrieved_at IS NOT NULL "
            "OR mapping_version IS NOT NULL OR source_field IS NOT NULL)"
        )
    ):
        raise RuntimeError("preserve recovery provenance before downgrade")
    for name in ("source_field", "mapping_version", "retrieved_at"):
        op.drop_column("daily_recovery_observations", name)

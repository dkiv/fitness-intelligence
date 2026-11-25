"""Record Garmin enrollment evidence alongside the immutable source identity."""

import sqlalchemy as sa
from alembic import op

revision = "b302"
down_revision = "b301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "garmin_enrollments",
        sa.Column("source_account_id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("evidence_type", sa.String(), nullable=False),
        sa.Column("approved_pin", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("provider = 'garmin'", name="garmin_provider"),
        sa.CheckConstraint(
            "(evidence_type = 'independent' AND approved_pin IS NULL) OR "
            "(evidence_type = 'locally_witnessed' AND approved_pin IS NOT NULL "
            "AND length(approved_pin) = 64)",
            name="valid_evidence",
        ),
    )


def downgrade() -> None:
    op.execute("LOCK TABLE garmin_enrollments IN ACCESS EXCLUSIVE MODE")
    if op.get_bind().scalar(sa.text("SELECT EXISTS (SELECT 1 FROM garmin_enrollments)")):
        raise RuntimeError("preserve enrollment evidence before downgrade")
    op.drop_table("garmin_enrollments")

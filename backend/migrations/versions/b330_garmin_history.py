"""garmin historical acquisition and reconciliation"""

import sqlalchemy as sa
from alembic import op

revision = "b330"
down_revision = "b320"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "garmin_history_coverage",
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("pass_key", sa.String(), nullable=False),
        sa.Column("policy", sa.String(), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_success", sa.DateTime(timezone=True), nullable=True),
        sa.Column("eligible_count", sa.Integer(), nullable=True),
        sa.Column("receipts", sa.JSON(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("source_account_id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.CheckConstraint(
            "provider = 'garmin'", name=op.f("ck_garmin_history_coverage_garmin_source")
        ),
        sa.CheckConstraint(
            "status IN ('observed','empty','failed','partial')",
            name=op.f("ck_garmin_history_coverage_status"),
        ),
        sa.CheckConstraint(
            "eligible_count >= 0", name=op.f("ck_garmin_history_coverage_positive_count")
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
            name=op.f("fk_garmin_history_coverage_user_id_source_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_garmin_history_coverage_user_id_users")
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            "provider",
            "source_account_id",
            "category",
            "local_date",
            name=op.f("pk_garmin_history_coverage"),
        ),
    )
    op.create_table(
        "garmin_history_issues",
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("evidence_digest", sa.String(), nullable=False),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("source_account_id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.CheckConstraint(
            "provider = 'garmin'", name=op.f("ck_garmin_history_issues_garmin_source")
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
            name=op.f("fk_garmin_history_issues_user_id_source_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_garmin_history_issues_user_id_users")
        ),
        sa.PrimaryKeyConstraint(
            "subject",
            "reason",
            "user_id",
            "provider",
            "source_account_id",
            "category",
            "local_date",
            name=op.f("pk_garmin_history_issues"),
        ),
    )
    op.add_column(
        "body_weight_observations", sa.Column("verification_scope", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.execute(
        "LOCK TABLE garmin_history_coverage, garmin_history_issues, "
        "body_weight_observations IN ACCESS EXCLUSIVE MODE"
    )
    if op.get_bind().scalar(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM garmin_history_coverage) "
            "OR EXISTS (SELECT 1 FROM garmin_history_issues) "
            "OR EXISTS (SELECT 1 FROM body_weight_observations "
            "WHERE verification_scope IS NOT NULL)"
        )
    ):
        raise RuntimeError("preserve historical coverage and reconciliation before downgrade")
    op.drop_column("body_weight_observations", "verification_scope")
    op.drop_table("garmin_history_issues")
    op.drop_table("garmin_history_coverage")

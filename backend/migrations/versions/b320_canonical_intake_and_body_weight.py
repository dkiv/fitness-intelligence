"""canonical intake and body weight"""

import sqlalchemy as sa
from alembic import op

revision = "b320"
down_revision = "b302"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "body_weight_observations",
        sa.Column("mass_kg", sa.Numeric(precision=22, scale=9), nullable=False),
        sa.Column("source_value", sa.Numeric(precision=22, scale=9), nullable=False),
        sa.Column("documented_source_unit", sa.String(), nullable=True),
        sa.Column("source_unit", sa.String(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_resolution_us", sa.Integer(), nullable=True),
        sa.Column("upstream_id", sa.String(), nullable=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("source_account_id", sa.Uuid(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("source_field", sa.String(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mapping_version", sa.String(), nullable=False),
        sa.Column("upstream_writer", sa.String(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "(measured_at IS NULL) = (time_resolution_us IS NULL) AND time_resolution_us > 0",
            name=op.f("ck_body_weight_observations_time_precision"),
        ),
        sa.CheckConstraint(
            "mass_kg > 0 AND mass_kg < 10000000000000 "
            "AND source_value > 0 AND source_value < 10000000000000",
            name=op.f("ck_body_weight_observations_valid_mass"),
        ),
        sa.CheckConstraint(
            "upstream_id IS NOT NULL OR measured_at IS NOT NULL",
            name=op.f("ck_body_weight_observations_weight_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
            name=op.f("fk_body_weight_observations_user_id_source_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_body_weight_observations_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_body_weight_observations")),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            "source_account_id",
            "upstream_id",
            name="uq_weight_source_record",
        ),
    )
    op.create_index(
        op.f("ix_body_weight_observations_user_id"),
        "body_weight_observations",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "uq_weight_unidentified_instant",
        "body_weight_observations",
        ["user_id", "provider", "source_account_id", "measured_at"],
        unique=True,
        postgresql_where=sa.text("upstream_id IS NULL"),
    )
    op.create_table(
        "daily_intake_observations",
        sa.Column("reported_kcal", sa.Numeric(precision=22, scale=9), nullable=False),
        sa.Column("completeness", sa.String(), nullable=False),
        sa.Column("source_data_present", sa.Boolean(), nullable=True),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("source_account_id", sa.Uuid(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("source_field", sa.String(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mapping_version", sa.String(), nullable=False),
        sa.Column("upstream_writer", sa.String(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "completeness IN ('unknown','partial','athlete_confirmed')",
            name=op.f("ck_daily_intake_observations_completeness"),
        ),
        sa.CheckConstraint(
            "reported_kcal >= 0 AND reported_kcal < 10000000000000",
            name=op.f("ck_daily_intake_observations_valid_kcal"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
            name=op.f("fk_daily_intake_observations_user_id_source_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_daily_intake_observations_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_intake_observations")),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            "source_account_id",
            "local_date",
            "source_field",
            name="uq_intake_source_day_field",
        ),
    )
    op.create_index(
        op.f("ix_daily_intake_observations_user_id"),
        "daily_intake_observations",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.execute(
        "LOCK TABLE daily_intake_observations, body_weight_observations IN ACCESS EXCLUSIVE MODE"
    )
    if op.get_bind().scalar(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM daily_intake_observations) "
            "OR EXISTS (SELECT 1 FROM body_weight_observations)"
        )
    ):
        raise RuntimeError("preserve intake and body weight observations before downgrade")
    op.drop_table("daily_intake_observations")
    op.drop_table("body_weight_observations")

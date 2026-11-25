"""canonical_endurance_recovery"""

import sqlalchemy as sa
from alembic import op

revision = "b201"
down_revision = "e301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_reference_workout_identity", "external_references", ["user_id", "workout_id", "id"]
    )
    op.create_table(
        "daily_recovery_observations",
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("source_account_id", sa.Uuid(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("metric", sa.String(), nullable=False),
        sa.Column("value", sa.Numeric(precision=22, scale=9), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "(metric IN ('overnight_hrv','seven_day_hrv') AND unit IN "
            "('ms','source_unit_unverified') AND method = 'reported_average') OR (metric = "
            "'resting_hr' AND unit = 'bpm' AND method = 'reported') OR (metric IN "
            "('sleep_duration','light_sleep','deep_sleep','rem_sleep','awake_during_sleep') AND "
            "unit = 's' AND method = 'reported') OR (metric IN "
            "('total_expenditure','active_expenditure','basal_expenditure') AND unit = 'kcal' "
            "AND method IN ('wearable_estimate','measured'))",
            name=op.f("ck_daily_recovery_observations_metric_unit_method"),
        ),
        sa.CheckConstraint(
            "(value IS NULL OR (value >= 0 AND value < 10000000000000))",
            name=op.f("ck_daily_recovery_observations_valid_quantities"),
        ),
        sa.CheckConstraint(
            "window_end >= window_start", name=op.f("ck_daily_recovery_observations_window_order")
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
            name=op.f("fk_daily_recovery_observations_user_id_source_accounts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_daily_recovery_observations_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_recovery_observations")),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            "source_account_id",
            "local_date",
            "metric",
            name="uq_recovery_account_day_metric",
        ),
    )
    op.create_index(
        op.f("ix_daily_recovery_observations_user_id"),
        "daily_recovery_observations",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "endurance_activities",
        sa.Column("workout_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("reference_id", sa.Uuid(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("sport", sa.String(), nullable=False),
        sa.Column("subtype", sa.String(), nullable=True),
        sa.Column("duration_s", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("elapsed_s", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("moving_s", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("distance_m", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("average_speed_mps", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("average_hr_bpm", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("max_hr_bpm", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("elevation_gain_m", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("elevation_loss_m", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.CheckConstraint(
            "(duration_s IS NULL OR (duration_s >= 0 AND duration_s < 10000000000000)) AND "
            "(elapsed_s IS NULL OR (elapsed_s >= 0 AND elapsed_s < 10000000000000)) AND "
            "(moving_s IS NULL OR (moving_s >= 0 AND moving_s < 10000000000000)) AND (distance_m "
            "IS NULL OR (distance_m >= 0 AND distance_m < 10000000000000)) AND "
            "(average_speed_mps IS NULL OR (average_speed_mps >= 0 AND average_speed_mps < "
            "10000000000000)) AND (average_hr_bpm IS NULL OR (average_hr_bpm >= 0 AND "
            "average_hr_bpm < 10000000000000)) AND (max_hr_bpm IS NULL OR (max_hr_bpm >= 0 AND "
            "max_hr_bpm < 10000000000000)) AND (elevation_gain_m IS NULL OR (elevation_gain_m >= "
            "0 AND elevation_gain_m < 10000000000000)) AND (elevation_loss_m IS NULL OR "
            "(elevation_loss_m >= 0 AND elevation_loss_m < 10000000000000))",
            name=op.f("ck_endurance_activities_valid_quantities"),
        ),
        sa.CheckConstraint(
            "length(sport) > 0", name=op.f("ck_endurance_activities_nonempty_sport")
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "workout_id", "reference_id"],
            [
                "external_references.user_id",
                "external_references.workout_id",
                "external_references.id",
            ],
            name="fk_endurance_workout_reference",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_endurance_activities_user_id_users")
        ),
        sa.PrimaryKeyConstraint("workout_id", name=op.f("pk_endurance_activities")),
        sa.UniqueConstraint("user_id", "workout_id", name=op.f("uq_endurance_activities_user_id")),
    )
    op.create_table(
        "activity_performed_steps",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("workout_id", sa.Uuid(), nullable=False),
        sa.Column("workout_index", sa.Integer(), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("intensity", sa.String(), nullable=True),
        sa.Column("duration_type", sa.String(), nullable=True),
        sa.Column("duration_value", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("duration_unit", sa.String(), nullable=True),
        sa.Column("target_type", sa.String(), nullable=True),
        sa.Column("target_zone", sa.Integer(), nullable=True),
        sa.Column("target_low", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("target_high", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("target_unit", sa.String(), nullable=True),
        sa.Column("repeat_count", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "(duration_value IS NULL OR (duration_value >= 0 AND duration_value < "
            "10000000000000)) AND (target_low IS NULL OR (target_low >= 0 AND target_low < "
            "10000000000000)) AND (target_high IS NULL OR (target_high >= 0 AND target_high < "
            "10000000000000))",
            name=op.f("ck_activity_performed_steps_valid_quantities"),
        ),
        sa.CheckConstraint(
            "(duration_value IS NULL) = (duration_unit IS NULL)",
            name=op.f("ck_activity_performed_steps_duration_units"),
        ),
        sa.CheckConstraint(
            "(target_low IS NULL) = (target_high IS NULL) AND (target_low IS NULL) = "
            "(target_unit IS NULL) AND target_low <= target_high AND (target_zone IS NULL OR "
            "target_low IS NULL)",
            name=op.f("ck_activity_performed_steps_range_units"),
        ),
        sa.CheckConstraint(
            "target_zone > 0 AND repeat_count >= 0", name=op.f("ck_activity_performed_steps_counts")
        ),
        sa.CheckConstraint(
            "workout_index >= 0 AND step_index >= 0",
            name=op.f("ck_activity_performed_steps_positions"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "workout_id"],
            ["endurance_activities.user_id", "endurance_activities.workout_id"],
            name=op.f("fk_activity_performed_steps_user_id_endurance_activities"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_activity_performed_steps_user_id_users")
        ),
        sa.PrimaryKeyConstraint(
            "workout_id", "workout_index", "step_index", name=op.f("pk_activity_performed_steps")
        ),
    )
    op.create_table(
        "activity_split_summaries",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("workout_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.Column("distance_m", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("duration_s", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.Column("average_speed_mps", sa.Numeric(precision=22, scale=9), nullable=True),
        sa.CheckConstraint(
            "(distance_m IS NULL OR (distance_m >= 0 AND distance_m < 10000000000000)) AND "
            "(duration_s IS NULL OR (duration_s >= 0 AND duration_s < 10000000000000)) AND "
            "(average_speed_mps IS NULL OR (average_speed_mps >= 0 AND average_speed_mps < "
            "10000000000000))",
            name=op.f("ck_activity_split_summaries_valid_quantities"),
        ),
        sa.CheckConstraint(
            "position >= 0 AND (count IS NULL OR count >= 0)",
            name=op.f("ck_activity_split_summaries_valid_position_count"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "workout_id"],
            ["endurance_activities.user_id", "endurance_activities.workout_id"],
            name=op.f("fk_activity_split_summaries_user_id_endurance_activities"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_activity_split_summaries_user_id_users")
        ),
        sa.PrimaryKeyConstraint("workout_id", "position", name=op.f("pk_activity_split_summaries")),
    )


def downgrade() -> None:
    op.drop_table("activity_split_summaries")
    op.drop_table("activity_performed_steps")
    op.drop_table("endurance_activities")
    op.drop_index(
        op.f("ix_daily_recovery_observations_user_id"), table_name="daily_recovery_observations"
    )
    op.drop_table("daily_recovery_observations")
    op.drop_constraint("uq_reference_workout_identity", "external_references", type_="unique")

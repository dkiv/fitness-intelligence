"""canonical strength models"""

import sqlalchemy as sa
from alembic import op

revision = "2827ecaa5ef5"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workouts",
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at", name=op.f("ck_workouts_time_order")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_workouts_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workouts")),
        sa.UniqueConstraint("user_id", "id", name=op.f("uq_workouts_user_id")),
    )
    op.create_index(op.f("ix_workouts_user_id"), "workouts", ["user_id"], unique=False)
    op.create_index("ix_workouts_user_started", "workouts", ["user_id", "started_at"], unique=False)
    op.create_table(
        "workout_exercises",
        sa.Column("workout_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("superset_group", sa.String(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("position >= 0", name=op.f("ck_workout_exercises_position_nonnegative")),
        sa.ForeignKeyConstraint(
            ["user_id", "workout_id"],
            ["workouts.user_id", "workouts.id"],
            name=op.f("fk_workout_exercises_user_id_workouts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_workout_exercises_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workout_exercises")),
        sa.UniqueConstraint("user_id", "id", name=op.f("uq_workout_exercises_user_id")),
        sa.UniqueConstraint(
            "user_id", "workout_id", "position", name="uq_workout_exercises_position"
        ),
    )
    op.create_index(
        op.f("ix_workout_exercises_user_id"), "workout_exercises", ["user_id"], unique=False
    )
    op.create_table(
        "exercise_sets",
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(), nullable=True),
        sa.Column("repetitions", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("distance_m", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("duration_seconds", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("rpe", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_measurements", sa.JSON(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("distance_m >= 0", name=op.f("ck_exercise_sets_distance_nonnegative")),
        sa.CheckConstraint(
            "duration_seconds >= 0", name=op.f("ck_exercise_sets_duration_nonnegative")
        ),
        sa.CheckConstraint("position >= 0", name=op.f("ck_exercise_sets_position_nonnegative")),
        sa.CheckConstraint(
            "repetitions >= 0", name=op.f("ck_exercise_sets_repetitions_nonnegative")
        ),
        sa.CheckConstraint("rpe >= 0 AND rpe <= 10", name=op.f("ck_exercise_sets_rpe_range")),
        sa.CheckConstraint("weight_kg >= 0", name=op.f("ck_exercise_sets_weight_nonnegative")),
        sa.ForeignKeyConstraint(
            ["user_id", "exercise_id"],
            ["workout_exercises.user_id", "workout_exercises.id"],
            name=op.f("fk_exercise_sets_user_id_workout_exercises"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_exercise_sets_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercise_sets")),
        sa.UniqueConstraint("user_id", "exercise_id", "position", name="uq_exercise_sets_position"),
        sa.UniqueConstraint("user_id", "id", name=op.f("uq_exercise_sets_user_id")),
    )
    op.create_index(op.f("ix_exercise_sets_user_id"), "exercise_sets", ["user_id"], unique=False)
    op.create_table(
        "external_references",
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("workout_id", sa.Uuid(), nullable=True),
        sa.Column("exercise_id", sa.Uuid(), nullable=True),
        sa.Column("set_id", sa.Uuid(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column(
            "first_imported_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_synced_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("source_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_version", sa.String(), nullable=True),
        sa.Column("sync_metadata", sa.JSON(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "(entity_type = 'workout' AND workout_id IS NOT NULL "
            "AND exercise_id IS NULL AND set_id IS NULL) OR "
            "(entity_type = 'exercise' AND exercise_id IS NOT NULL "
            "AND workout_id IS NULL AND set_id IS NULL) OR "
            "(entity_type = 'set' AND set_id IS NOT NULL "
            "AND workout_id IS NULL AND exercise_id IS NULL)",
            name=op.f("ck_external_references_target_matches_type"),
        ),
        sa.CheckConstraint(
            "length(provider) > 0 AND length(external_id) > 0",
            name=op.f("ck_external_references_identity_nonempty"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "exercise_id"],
            ["workout_exercises.user_id", "workout_exercises.id"],
            name=op.f("fk_external_references_user_id_workout_exercises"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "set_id"],
            ["exercise_sets.user_id", "exercise_sets.id"],
            name=op.f("fk_external_references_user_id_exercise_sets"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "workout_id"],
            ["workouts.user_id", "workouts.id"],
            name=op.f("fk_external_references_user_id_workouts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_external_references_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_external_references")),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            "entity_type",
            "external_id",
            name=op.f("uq_external_references_user_id"),
        ),
    )
    op.create_index(
        "ix_external_references_user_exercise",
        "external_references",
        ["user_id", "exercise_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_external_references_user_id"), "external_references", ["user_id"], unique=False
    )
    op.create_index(
        "ix_external_references_user_set",
        "external_references",
        ["user_id", "set_id"],
        unique=False,
    )
    op.create_index(
        "ix_external_references_user_workout",
        "external_references",
        ["user_id", "workout_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_external_references_user_workout", table_name="external_references")
    op.drop_index("ix_external_references_user_set", table_name="external_references")
    op.drop_index(op.f("ix_external_references_user_id"), table_name="external_references")
    op.drop_index("ix_external_references_user_exercise", table_name="external_references")
    op.drop_table("external_references")
    op.drop_index(op.f("ix_exercise_sets_user_id"), table_name="exercise_sets")
    op.drop_table("exercise_sets")
    op.drop_index(op.f("ix_workout_exercises_user_id"), table_name="workout_exercises")
    op.drop_table("workout_exercises")
    op.drop_index("ix_workouts_user_started", table_name="workouts")
    op.drop_index(op.f("ix_workouts_user_id"), table_name="workouts")
    op.drop_table("workouts")

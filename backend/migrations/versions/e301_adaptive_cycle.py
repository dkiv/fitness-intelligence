"""adaptive_cycle"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "e301"
down_revision = "e201"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "session_outcomes",
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("revision_id", sa.Uuid(), nullable=False),
        sa.Column("choice", sa.String(), server_default="approve", nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(), nullable=False),
        sa.Column("command_id", sa.Uuid(), nullable=False),
        sa.Column("supersedes_id", sa.Uuid(), nullable=True),
        sa.Column("workout_id", sa.Uuid(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "actual",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("choice = 'approve'", name=op.f("ck_session_outcomes_approved")),
        sa.CheckConstraint(
            "slot IN ('first-press','second-press','short-run','long-run')",
            name=op.f("ck_session_outcomes_slot"),
        ),
        sa.CheckConstraint(
            "id <> supersedes_id", name=op.f("ck_session_outcomes_distinct_correction")
        ),
        sa.CheckConstraint("occurred_at <= recorded_at", name=op.f("ck_session_outcomes_elapsed")),
        sa.CheckConstraint("week IN (1, 2)", name=op.f("ck_session_outcomes_week")),
        sa.ForeignKeyConstraint(
            ["user_id", "plan_id", "revision_id", "choice"],
            [
                "plan_decisions.user_id",
                "plan_decisions.plan_id",
                "plan_decisions.revision_id",
                "plan_decisions.choice",
            ],
            name="fk_outcome_approval",
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "plan_id", "week", "slot", "supersedes_id"],
            [
                "session_outcomes.user_id",
                "session_outcomes.plan_id",
                "session_outcomes.week",
                "session_outcomes.slot",
                "session_outcomes.id",
            ],
            name="fk_outcome_supersedes",
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "workout_id"],
            ["workouts.user_id", "workouts.id"],
            name=op.f("fk_session_outcomes_user_id_workouts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_session_outcomes_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_session_outcomes")),
        sa.UniqueConstraint("supersedes_id", name="uq_outcome_successor"),
        sa.UniqueConstraint("user_id", "command_id", name="uq_outcome_command"),
        sa.UniqueConstraint("user_id", "plan_id", "week", "slot", "id", name="uq_outcome_slot_id"),
    )
    op.create_index(
        op.f("ix_session_outcomes_user_id"), "session_outcomes", ["user_id"], unique=False
    )
    op.create_index(
        "uq_outcome_root",
        "session_outcomes",
        ["user_id", "plan_id", "week", "slot"],
        unique=True,
        postgresql_where=sa.text("supersedes_id IS NULL"),
        sqlite_where=sa.text("supersedes_id IS NULL"),
    )
    op.add_column(
        "plan_revisions",
        sa.Column(
            "rationale",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
    )

    op.execute("""CREATE TRIGGER immutable BEFORE UPDATE OR DELETE ON session_outcomes
        FOR EACH ROW EXECUTE FUNCTION e2_immutable()""")
    op.execute("""CREATE TRIGGER preserve_history BEFORE TRUNCATE ON session_outcomes
        FOR EACH STATEMENT EXECUTE FUNCTION e2_immutable()""")
    # Walk approved bases backwards. Lineage breaks ties when two receipts share an instant.
    op.execute("""CREATE FUNCTION e3_effective_revision(
        athlete uuid, cycle uuid, instant timestamptz)
        RETURNS uuid LANGUAGE sql STABLE AS $$
        WITH RECURSIVE lineage(id, base_id, decided_at) AS (
            SELECT r.id, r.base_id, d.decided_at FROM training_plans p
            JOIN plan_revisions r ON r.user_id = athlete AND r.plan_id = cycle AND r.id = p.head_id
            JOIN plan_decisions d ON d.user_id = athlete AND d.plan_id = cycle
                AND d.revision_id = r.id AND d.choice = 'approve'
            WHERE p.id = cycle AND p.user_id = athlete
            UNION ALL
            SELECT r.id, r.base_id, d.decided_at FROM lineage l
            JOIN plan_revisions r ON r.user_id = athlete AND r.plan_id = cycle AND r.id = l.base_id
            JOIN plan_decisions d ON d.user_id = athlete AND d.plan_id = cycle
                AND d.revision_id = r.id AND d.choice = 'approve'
            WHERE l.decided_at > instant
        )
        SELECT id FROM lineage WHERE decided_at <= instant
        $$""")
    op.execute("""CREATE FUNCTION e3_outcome_attribution() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            PERFORM id FROM users WHERE id = NEW.user_id FOR UPDATE;
            IF NEW.revision_id IS DISTINCT FROM
                e3_effective_revision(NEW.user_id, NEW.plan_id, NEW.occurred_at)
                OR NOT EXISTS (SELECT 1 FROM plan_revisions
                    WHERE user_id = NEW.user_id AND plan_id = NEW.plan_id AND id = NEW.revision_id
                    AND (snapshot #>> '{data,week,inputs,number}')::integer >= NEW.week) THEN
                RAISE EXCEPTION 'prescription was not in force' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$""")
    op.execute("""CREATE TRIGGER attribution BEFORE INSERT ON session_outcomes
        FOR EACH ROW EXECUTE FUNCTION e3_outcome_attribution()""")


def downgrade() -> None:
    op.execute("LOCK TABLE plan_revisions, session_outcomes IN ACCESS EXCLUSIVE MODE")
    if op.get_bind().scalar(
        sa.text("""SELECT EXISTS (SELECT 1 FROM session_outcomes)
        OR EXISTS (SELECT 1 FROM plan_revisions WHERE rationale IS NOT NULL)""")
    ):
        raise RuntimeError("E3 contains adaptive cycle data; preserve history before downgrade")
    op.drop_column("plan_revisions", "rationale")
    op.drop_index(
        "uq_outcome_root",
        table_name="session_outcomes",
        postgresql_where=sa.text("supersedes_id IS NULL"),
        sqlite_where=sa.text("supersedes_id IS NULL"),
    )
    op.drop_index(op.f("ix_session_outcomes_user_id"), table_name="session_outcomes")
    op.drop_table("session_outcomes")
    op.execute("DROP FUNCTION e3_outcome_attribution()")
    op.execute("DROP FUNCTION e3_effective_revision(uuid, uuid, timestamptz)")

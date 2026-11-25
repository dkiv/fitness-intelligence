"""canonical plan approval"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "e201"
down_revision = "b702_hevy_pending"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "athlete_contexts",
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column(
            "snapshot",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("sequence > 0", name=op.f("ck_athlete_contexts_positive_sequence")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_athlete_contexts_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_athlete_contexts")),
        sa.UniqueConstraint("user_id", "id", name=op.f("uq_athlete_contexts_user_id")),
        sa.UniqueConstraint("user_id", "sequence", name="uq_context_sequence"),
    )
    op.create_index(
        op.f("ix_athlete_contexts_user_id"), "athlete_contexts", ["user_id"], unique=False
    )
    op.create_table(
        "training_plans",
        sa.Column(
            "block",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("head_id", sa.Uuid(), nullable=True),
        sa.Column("head_choice", sa.String(), server_default="approve", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("head_choice = 'approve'", name=op.f("ck_training_plans_approved_only")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_training_plans_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_training_plans")),
        sa.UniqueConstraint("user_id", "id", name=op.f("uq_training_plans_user_id")),
    )
    op.create_index(op.f("ix_training_plans_user_id"), "training_plans", ["user_id"], unique=False)
    op.create_table(
        "plan_revisions",
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("context_id", sa.Uuid(), nullable=False),
        sa.Column("base_id", sa.Uuid(), nullable=True),
        sa.Column(
            "snapshot",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("id <> base_id", name=op.f("ck_plan_revisions_distinct_base")),
        sa.ForeignKeyConstraint(
            ["user_id", "context_id"],
            ["athlete_contexts.user_id", "athlete_contexts.id"],
            name=op.f("fk_plan_revisions_user_id_athlete_contexts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "plan_id", "base_id"],
            ["plan_revisions.user_id", "plan_revisions.plan_id", "plan_revisions.id"],
            name="fk_revision_base",
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "plan_id"],
            ["training_plans.user_id", "training_plans.id"],
            name=op.f("fk_plan_revisions_user_id_training_plans"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_plan_revisions_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_plan_revisions")),
        sa.UniqueConstraint("user_id", "id", name=op.f("uq_plan_revisions_user_id")),
        sa.UniqueConstraint("user_id", "plan_id", "id", name="uq_plan_revision_lineage"),
    )
    op.create_index(op.f("ix_plan_revisions_user_id"), "plan_revisions", ["user_id"], unique=False)
    op.create_table(
        "plan_decisions",
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("revision_id", sa.Uuid(), nullable=False),
        sa.Column("command_id", sa.Uuid(), nullable=False),
        sa.Column("choice", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "choice IN ('approve','decline')", name=op.f("ck_plan_decisions_valid_choice")
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "plan_id", "revision_id"],
            ["plan_revisions.user_id", "plan_revisions.plan_id", "plan_revisions.id"],
            name=op.f("fk_plan_decisions_user_id_plan_revisions"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_plan_decisions_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_plan_decisions")),
        sa.UniqueConstraint("revision_id", name=op.f("uq_plan_decisions_revision_id")),
        sa.UniqueConstraint("user_id", "command_id", name="uq_plan_decision_command"),
        sa.UniqueConstraint("user_id", "id", name=op.f("uq_plan_decisions_user_id")),
        sa.UniqueConstraint(
            "user_id", "plan_id", "revision_id", "choice", name="uq_plan_decision_head"
        ),
    )
    op.create_index(op.f("ix_plan_decisions_user_id"), "plan_decisions", ["user_id"], unique=False)

    op.create_foreign_key(
        "fk_plan_approved_head",
        "training_plans",
        "plan_decisions",
        ["user_id", "id", "head_id", "head_choice"],
        ["user_id", "plan_id", "revision_id", "choice"],
    )
    op.execute("""
        CREATE FUNCTION e2_immutable() RETURNS trigger LANGUAGE plpgsql AS $e2$
        BEGIN
            RAISE EXCEPTION 'sealed planning record' USING ERRCODE = '23514';
        END $e2$""")
    for table in ("athlete_contexts", "plan_revisions", "plan_decisions"):
        op.execute(f"""CREATE TRIGGER immutable BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION e2_immutable()""")

    for table in ("athlete_contexts", "training_plans", "plan_revisions", "plan_decisions"):
        op.execute(f"""CREATE TRIGGER preserve_history BEFORE TRUNCATE ON {table}
            FOR EACH STATEMENT EXECUTE FUNCTION e2_immutable()""")

    op.execute("""
        CREATE FUNCTION e2_context_sequence() RETURNS trigger LANGUAGE plpgsql AS $e2$
        BEGIN
            PERFORM id FROM users WHERE id = NEW.user_id FOR UPDATE;
            IF NEW.sequence <> (SELECT coalesce(max(sequence), 0) + 1
                                FROM athlete_contexts WHERE user_id = NEW.user_id) THEN
                RAISE EXCEPTION 'stale context sequence' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $e2$""")
    op.execute("""CREATE TRIGGER context_sequence BEFORE INSERT ON athlete_contexts
        FOR EACH ROW EXECUTE FUNCTION e2_context_sequence()""")

    op.execute("""
        CREATE FUNCTION e2_revision_base() RETURNS trigger LANGUAGE plpgsql AS $e2$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM training_plans
                WHERE user_id = NEW.user_id AND id = NEW.plan_id
                AND head_id IS NOT DISTINCT FROM NEW.base_id FOR UPDATE) THEN
                RAISE EXCEPTION 'invalid proposal base' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $e2$""")
    op.execute("""CREATE TRIGGER revision_base BEFORE INSERT ON plan_revisions
        FOR EACH ROW EXECUTE FUNCTION e2_revision_base()""")

    op.execute("""
        CREATE FUNCTION e2_head_transition() RETURNS trigger LANGUAGE plpgsql AS $e2$
        BEGIN
            IF TG_OP = 'INSERT' AND NEW.head_id IS NULL THEN
                RETURN NEW;
            ELSIF TG_OP = 'UPDATE' THEN
                IF (NEW.id, NEW.user_id, NEW.block, NEW.head_choice) IS NOT DISTINCT FROM
                   (OLD.id, OLD.user_id, OLD.block, OLD.head_choice)
                   AND EXISTS (SELECT 1 FROM plan_revisions WHERE user_id = NEW.user_id
                       AND plan_id = NEW.id AND id = NEW.head_id
                       AND base_id IS NOT DISTINCT FROM OLD.head_id) THEN
                    RETURN NEW;
                END IF;
            END IF;
            RAISE EXCEPTION 'invalid plan transition' USING ERRCODE = '23514';
        END $e2$""")
    op.execute("""CREATE TRIGGER head_transition BEFORE INSERT OR UPDATE OR DELETE ON training_plans
        FOR EACH ROW EXECUTE FUNCTION e2_head_transition()""")

    # The approval receipt itself switches the head. Even direct SQL cannot commit half a decision.
    op.execute("""
        CREATE FUNCTION e2_apply_decision() RETURNS trigger LANGUAGE plpgsql AS $e2$
        DECLARE
            candidate plan_revisions%ROWTYPE;
            current_head uuid;
            current_context uuid;
        BEGIN
            PERFORM id FROM users WHERE id = NEW.user_id FOR UPDATE;
            SELECT head_id INTO STRICT current_head FROM training_plans
                WHERE user_id = NEW.user_id AND id = NEW.plan_id FOR UPDATE;
            SELECT * INTO STRICT candidate FROM plan_revisions
                WHERE user_id = NEW.user_id AND plan_id = NEW.plan_id AND id = NEW.revision_id;
            IF current_head IS DISTINCT FROM candidate.base_id THEN
                RAISE EXCEPTION 'stale decision base' USING ERRCODE = '23514';
            END IF;
            IF NEW.choice = 'approve' THEN
                SELECT id INTO current_context FROM athlete_contexts WHERE user_id = NEW.user_id
                    ORDER BY sequence DESC LIMIT 1;
                IF current_context IS DISTINCT FROM candidate.context_id THEN
                    RAISE EXCEPTION 'stale approval context' USING ERRCODE = '23514';
                END IF;
                UPDATE training_plans SET head_id = candidate.id
                    WHERE user_id = NEW.user_id AND id = NEW.plan_id;
            END IF;
            RETURN NEW;
        END $e2$""")
    op.execute("""CREATE TRIGGER apply_decision AFTER INSERT ON plan_decisions
        FOR EACH ROW EXECUTE FUNCTION e2_apply_decision()""")


def downgrade() -> None:
    # Hold writers out between the preflight and DROP. Context and cycle are the two roots.
    op.execute("LOCK TABLE athlete_contexts, training_plans IN ACCESS EXCLUSIVE MODE")
    if op.get_bind().scalar(
        sa.text("""
        SELECT EXISTS (SELECT 1 FROM athlete_contexts) OR EXISTS (SELECT 1 FROM training_plans)
    """)
    ):
        raise RuntimeError("E2 contains planning data; preserve history before downgrade")
    op.drop_constraint("fk_plan_approved_head", "training_plans", type_="foreignkey")
    op.drop_index(op.f("ix_plan_decisions_user_id"), table_name="plan_decisions")
    op.drop_table("plan_decisions")
    op.drop_index(op.f("ix_plan_revisions_user_id"), table_name="plan_revisions")
    op.drop_table("plan_revisions")
    op.drop_index(op.f("ix_training_plans_user_id"), table_name="training_plans")
    op.drop_table("training_plans")
    op.drop_index(op.f("ix_athlete_contexts_user_id"), table_name="athlete_contexts")
    op.drop_table("athlete_contexts")
    for function in (
        "apply_decision",
        "head_transition",
        "revision_base",
        "context_sequence",
        "immutable",
    ):
        op.execute(f"DROP FUNCTION e2_{function}()")

"""Index the member-level lineage of sealed synthetic confirmation receipts."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "e422"
down_revision = "e421"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "confirmation_receipts",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("command", sa.Uuid(), nullable=False),
        sa.Column("actor", sa.Uuid(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("intent_digest", sa.String(), nullable=False),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "actor = user_id AND user_id = 'c13399d0-4e41-50ef-b9e4-25fff100dadd'",
            name=op.f("ck_confirmation_receipts_synthetic_actor"),
        ),
        sa.CheckConstraint(
            "payload->'schema_version' IS NOT DISTINCT FROM '1'::jsonb",
            name=op.f("ck_confirmation_receipts_version"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_confirmation_receipts_user_id_users")
        ),
        sa.PrimaryKeyConstraint("user_id", "command", name=op.f("pk_confirmation_receipts")),
    )
    op.create_table(
        "confirmation_members",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("account", sa.Uuid(), nullable=False),
        sa.Column("workout", sa.Uuid(), nullable=False),
        sa.Column("member", sa.Uuid(), nullable=False),
        sa.Column("command", sa.Uuid(), nullable=False),
        sa.Column("supersedes", sa.Uuid(), nullable=True),
        sa.Column("outcome", sa.Uuid(), nullable=True),
        sa.CheckConstraint(
            "command <> supersedes", name=op.f("ck_confirmation_members_distinct_predecessor")
        ),
        sa.ForeignKeyConstraint(
            ["outcome"],
            ["session_outcomes.id"],
            name=op.f("fk_confirmation_members_outcome_session_outcomes"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "account", "workout", "member", "supersedes"],
            [
                "confirmation_members.user_id",
                "confirmation_members.account",
                "confirmation_members.workout",
                "confirmation_members.member",
                "confirmation_members.command",
            ],
            name="fk_confirmation_member_predecessor",
        ),
        sa.ForeignKeyConstraint(
            ["user_id", "command"],
            ["confirmation_receipts.user_id", "confirmation_receipts.command"],
            name=op.f("fk_confirmation_members_user_id_confirmation_receipts"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_confirmation_members_user_id_users")
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            "account",
            "workout",
            "member",
            "command",
            name=op.f("pk_confirmation_members"),
        ),
    )
    op.create_index(
        "uq_confirmation_root",
        "confirmation_members",
        ["user_id", "member"],
        unique=True,
        postgresql_where=sa.text("supersedes IS NULL"),
        sqlite_where=sa.text("supersedes IS NULL"),
    )
    op.create_index(
        "uq_confirmation_successor",
        "confirmation_members",
        ["user_id", "member", "supersedes"],
        unique=True,
    )

    # Insert all edges atomically with the receipt. The unique root and successor
    # indexes serialize even competing direct inserts for the same member.
    op.execute("""CREATE FUNCTION e422_index_receipt() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE
            d jsonb := NEW.payload->'display';
            facts jsonb := d->'members';
            answers jsonb := NEW.payload->'answers';
            m jsonb;
            a jsonb;
        BEGIN
            IF d->>'owner' IS DISTINCT FROM NEW.user_id::text OR
               d->'schema_version' IS DISTINCT FROM '1'::jsonb OR
               jsonb_typeof(facts) IS DISTINCT FROM 'array' OR
               jsonb_typeof(answers) IS DISTINCT FROM 'array' OR
               jsonb_array_length(facts) = 0 OR
               jsonb_array_length(facts) <> jsonb_array_length(answers) THEN
                RAISE EXCEPTION 'invalid display scope' USING ERRCODE='23514';
            END IF;
            FOR i IN 0..jsonb_array_length(facts)-1 LOOP
                m := facts->i;
                a := answers->i;
                IF m->>'owner' IS DISTINCT FROM NEW.user_id::text OR
                   m->>'account' IS DISTINCT FROM d->>'account' OR
                   coalesce(m->>'member',m->>'workout') IS DISTINCT FROM a->>'member' OR
                   (m->>'occurred_at')::timestamptz > NEW.recorded_at OR
                   (a->>'disposition' = 'withdraw' AND a->>'supersedes' IS NULL) THEN
                    RAISE EXCEPTION 'invalid confirmation member' USING ERRCODE='23514';
                END IF;
                INSERT INTO confirmation_members(user_id,account,workout,member,command,
                                                 supersedes,outcome)
                    VALUES(NEW.user_id,(m->>'account')::uuid,(m->>'workout')::uuid,
                           (a->>'member')::uuid,NEW.command,(a->>'supersedes')::uuid,
                           (a->>'outcome')::uuid);
            END LOOP;
            RETURN NEW;
        END $$""")
    op.execute("""CREATE TRIGGER confirmation_index AFTER INSERT ON confirmation_receipts
        FOR EACH ROW EXECUTE FUNCTION e422_index_receipt()""")
    op.execute("""CREATE FUNCTION e422_guard_member() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM confirmation_receipts r
                CROSS JOIN LATERAL jsonb_array_elements(r.payload->'answers') a
                CROSS JOIN LATERAL jsonb_array_elements(r.payload#>'{display,members}') m
                WHERE (r.user_id,r.command) = (NEW.user_id,NEW.command)
                  AND a->>'member' = NEW.member::text
                  AND coalesce(m->>'member',m->>'workout') = NEW.member::text
                  AND (m->>'account',m->>'workout') = (NEW.account::text,NEW.workout::text)
                  AND (a->>'supersedes')::uuid IS NOT DISTINCT FROM NEW.supersedes
                  AND (a->>'outcome')::uuid IS NOT DISTINCT FROM NEW.outcome
                  AND (NEW.supersedes IS NULL OR EXISTS (SELECT 1 FROM confirmation_receipts p
                      JOIN confirmation_members parent
                        ON (parent.user_id,parent.command) = (p.user_id,p.command)
                      WHERE (p.user_id,p.command) = (NEW.user_id,NEW.supersedes)
                        AND parent.member = NEW.member
                        AND p.recorded_at <= r.recorded_at))
                  AND (NEW.outcome IS NULL OR EXISTS (SELECT 1 FROM session_outcomes o
                      WHERE (o.user_id,o.id) = (NEW.user_id,NEW.outcome)
                        AND o.outcome_version=2 AND o.occurred_at=(m->>'occurred_at')::timestamptz
                        AND o.recorded_at <= r.recorded_at
                        AND o.actual->>'status' IN ('completed','partial')
                        AND ((m->>'provider'='synthetic-hevy' AND o.actual->>'sport'='strength') OR
                             (m->>'provider'='synthetic-garmin' AND o.actual->>'sport'='running'
                              AND o.actual->>'role'=m->>'role'))
                        AND NOT EXISTS (SELECT 1 FROM session_outcomes successor
                            WHERE successor.user_id=o.user_id
                              AND successor.supersedes_id=o.id)))) THEN
                RAISE EXCEPTION 'invalid receipt or member lineage' USING ERRCODE='23514';
            END IF;
            RETURN NEW;
        END $$""")
    op.execute("""CREATE TRIGGER member_scope BEFORE INSERT ON confirmation_members
        FOR EACH ROW EXECUTE FUNCTION e422_guard_member()""")
    for table in ("confirmation_receipts", "confirmation_members"):
        op.execute(f"""CREATE TRIGGER immutable BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION e2_immutable()""")
        op.execute(f"""CREATE TRIGGER no_truncate BEFORE TRUNCATE ON {table}
            FOR EACH STATEMENT EXECUTE FUNCTION e2_immutable()""")


def downgrade() -> None:
    op.execute("LOCK TABLE confirmation_receipts, confirmation_members IN ACCESS EXCLUSIVE MODE")
    if op.get_bind().scalar(sa.text("SELECT EXISTS (SELECT 1 FROM confirmation_receipts)")):
        raise RuntimeError("preserve scoped confirmation history before downgrade")

    op.drop_index("uq_confirmation_successor", table_name="confirmation_members")
    op.drop_index(
        "uq_confirmation_root",
        table_name="confirmation_members",
        postgresql_where=sa.text("supersedes IS NULL"),
        sqlite_where=sa.text("supersedes IS NULL"),
    )
    op.drop_table("confirmation_members")
    op.drop_table("confirmation_receipts")
    op.execute("DROP FUNCTION e422_index_receipt()")
    op.execute("DROP FUNCTION e422_guard_member()")

"""Attribute manual synthetic generalized execution to its in-force and originating approvals."""

import sqlalchemy as sa
from alembic import op

revision = "e421"
down_revision = "b330"
branch_labels = None
depends_on = None

LEGACY_SLOTS = "slot IN ('first-press','second-press','short-run','long-run')"
SCOPE = (
    "(outcome_version = 1 AND origin_revision_id IS NULL AND week IN (1, 2) AND "
    + LEGACY_SLOTS
    + ") OR (outcome_version = 2 AND origin_revision_id IS NOT NULL AND week > 0 "
    "AND workout_id IS NULL)"
)


def upgrade() -> None:
    op.add_column(
        "session_outcomes",
        sa.Column("outcome_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column("session_outcomes", sa.Column("origin_revision_id", sa.Uuid()))
    op.create_foreign_key(
        "fk_outcome_origin_approval",
        "session_outcomes",
        "plan_decisions",
        ["user_id", "plan_id", "origin_revision_id", "choice"],
        ["user_id", "plan_id", "revision_id", "choice"],
    )
    for name in ("week", "slot"):
        op.drop_constraint(op.f(f"ck_session_outcomes_{name}"), "session_outcomes", type_="check")
    op.create_check_constraint(
        op.f("ck_session_outcomes_versioned_scope"), "session_outcomes", SCOPE
    )
    # The canonical occurrence UUID string occupies the existing slot key. Root / successor
    # uniqueness, same-slot parent FK and immutable/truncate triggers continue to apply.
    op.execute("DROP TRIGGER attribution ON session_outcomes")
    op.execute("""CREATE TRIGGER attribution BEFORE INSERT ON session_outcomes FOR EACH ROW
        WHEN (NEW.outcome_version = 1) EXECUTE FUNCTION e3_outcome_attribution()""")
    op.execute("""CREATE FUNCTION e421_outcome_attribution() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE
            scheduled jsonb;
            first_day date;
            local_zone text;
            reported_status text := NEW.actual->>'status';
        BEGIN
            PERFORM id FROM users WHERE id = NEW.user_id FOR UPDATE;
            PERFORM id FROM training_plans WHERE user_id = NEW.user_id AND id = NEW.plan_id
                FOR UPDATE;
            IF NEW.user_id <> 'c13399d0-4e41-50ef-b9e4-25fff100dadd'::uuid OR
                NEW.revision_id IS DISTINCT FROM
                    e3_effective_revision(NEW.user_id, NEW.plan_id, NEW.occurred_at) THEN
                RAISE EXCEPTION 'invalid generalized effective head' USING ERRCODE = '23514';
            END IF;

            SELECT s, (p.block#>>'{data,start}')::date + 7 * (NEW.week - 1),
                   c.snapshot#>>'{data,zone}' INTO scheduled, first_day, local_zone
            FROM training_plans p
            JOIN plan_revisions h ON (h.user_id,h.plan_id,h.id) =
                                     (p.user_id,p.id,NEW.revision_id)
            JOIN plan_revisions o ON (o.user_id,o.plan_id,o.id) =
                                     (p.user_id,p.id,NEW.origin_revision_id)
            JOIN plan_decisions d ON (d.user_id,d.plan_id,d.revision_id,d.choice) =
                                     (o.user_id,o.plan_id,o.id,'approve')
            JOIN athlete_contexts c ON (c.user_id,c.id) = (o.user_id,o.context_id)
            CROSS JOIN LATERAL jsonb_array_elements(o.snapshot#>'{data,days}') day
            CROSS JOIN LATERAL jsonb_array_elements(day->'sessions') s
            WHERE p.id = NEW.plan_id AND p.user_id = NEW.user_id AND d.decided_at <= NEW.occurred_at
              AND p.block->>'schema_version' = '2'
              AND h.snapshot->>'schema_version' = '2' AND o.snapshot->>'schema_version' = '2'
              AND h.snapshot#>>'{data,mode}' = 'synthetic-research-preview'
              AND o.snapshot#>>'{data,mode}' = 'synthetic-research-preview'
              AND h.snapshot#>>'{data,cycle}' = p.id::text
              AND o.snapshot#>>'{data,cycle}' = p.id::text
              AND h.snapshot#>>'{data,block_key}' = p.block#>>'{data,key}'
              AND o.snapshot#>>'{data,block_key}' = p.block#>>'{data,key}'
              AND h.snapshot#>>'{data,block_revision}' = o.snapshot#>>'{data,block_revision}'
              AND h.snapshot#>>'{data,request,kind}' = 'familiar-week'
              AND o.snapshot#>>'{data,request,kind}' = 'familiar-week'
              AND o.snapshot#>>'{data,request,number}' = NEW.week::text
              AND NEW.week <= jsonb_array_length(p.block#>'{data,phases}')
              AND (h.id = o.id OR (
                   (h.snapshot#>>'{data,request,number}')::int > NEW.week AND
                   h.snapshot#>'{data,prior_weeks}' @>
                       jsonb_build_array(jsonb_build_object('number',NEW.week,'revision',o.id))))
              AND s->>'occurrence' = NEW.slot;

            IF scheduled IS NULL OR local_zone IS NULL OR first_day IS NULL OR
               NOT ((NEW.occurred_at AT TIME ZONE local_zone)::date
                    BETWEEN first_day AND first_day+6)
               OR NEW.actual->'schema_version' IS DISTINCT FROM '2'::jsonb
               OR NEW.actual->>'provenance' IS DISTINCT FROM 'synthetic-athlete-report'
               OR NEW.actual->>'sport' IS DISTINCT FROM scheduled#>>'{prescription,sport}'
               OR (NEW.actual->>'sport' = 'running' AND NEW.actual->>'role' IS DISTINCT FROM
                       scheduled#>>'{prescription,role}')
               OR reported_status IS NULL
               OR reported_status NOT IN ('completed','partial','missed','unknown')
               OR (reported_status IN ('missed','unknown') AND
                   NEW.occurred_at IS DISTINCT FROM (scheduled->>'start_utc')::timestamptz)
            THEN
                RAISE EXCEPTION 'invalid occurrence, origin or attribution instant'
                    USING ERRCODE = '23514';
            END IF;
            IF NEW.supersedes_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM session_outcomes parent WHERE parent.user_id = NEW.user_id
                  AND parent.id = NEW.supersedes_id AND parent.plan_id = NEW.plan_id
                  AND parent.slot = NEW.slot AND parent.week = NEW.week
                  AND parent.origin_revision_id = NEW.origin_revision_id
                  AND parent.recorded_at <= NEW.recorded_at
                  AND NOT EXISTS (SELECT 1 FROM session_outcomes successor
                      WHERE successor.user_id = parent.user_id
                        AND successor.supersedes_id = parent.id)
            ) THEN
                RAISE EXCEPTION 'invalid correction lineage' USING ERRCODE = '23514';
            END IF;
            IF reported_status IN ('completed','partial') AND EXISTS (
                SELECT 1 FROM session_outcomes a WHERE a.user_id = NEW.user_id
                  AND a.occurred_at = NEW.occurred_at AND a.id IS DISTINCT FROM NEW.supersedes_id
                  AND a.actual->>'status' IN ('completed','partial')
                  AND NOT EXISTS (SELECT 1 FROM session_outcomes successor
                       WHERE successor.user_id = a.user_id AND successor.supersedes_id = a.id)
            ) THEN
                RAISE EXCEPTION 'execution already attributed' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$""")
    op.execute("""CREATE TRIGGER generalized_attribution BEFORE INSERT ON session_outcomes
        FOR EACH ROW WHEN (NEW.outcome_version = 2) EXECUTE FUNCTION e421_outcome_attribution()""")


def downgrade() -> None:
    op.execute("LOCK TABLE session_outcomes IN ACCESS EXCLUSIVE MODE")
    if op.get_bind().scalar(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM session_outcomes "
            "WHERE outcome_version <> 1 OR origin_revision_id IS NOT NULL)"
        )
    ):
        raise RuntimeError("generalized execution exists; preserve history before downgrade")
    op.execute("DROP TRIGGER generalized_attribution ON session_outcomes")
    op.execute("DROP FUNCTION e421_outcome_attribution()")
    op.execute("DROP TRIGGER attribution ON session_outcomes")
    op.execute("""CREATE TRIGGER attribution BEFORE INSERT ON session_outcomes
        FOR EACH ROW EXECUTE FUNCTION e3_outcome_attribution()""")
    op.drop_constraint(
        op.f("ck_session_outcomes_versioned_scope"), "session_outcomes", type_="check"
    )
    op.create_check_constraint(
        op.f("ck_session_outcomes_week"), "session_outcomes", "week IN (1, 2)"
    )
    op.create_check_constraint(op.f("ck_session_outcomes_slot"), "session_outcomes", LEGACY_SLOTS)
    op.drop_constraint("fk_outcome_origin_approval", "session_outcomes", type_="foreignkey")
    op.drop_column("session_outcomes", "origin_revision_id")
    op.drop_column("session_outcomes", "outcome_version")

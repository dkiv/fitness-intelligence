"""Account namespaces and minimal ingestion state.

Revision ID: 91ab
Revises: 2827ecaa5ef5
"""

from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    MetaData,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
        }
    )


sa.Table("users", Base.metadata, sa.Column("id", sa.Uuid(), primary_key=True))


class OwnedRecord:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)


class SourceAccount(OwnedRecord, Base):
    __tablename__ = "source_accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "id"),
        CheckConstraint("length(provider) > 0", name="provider_nonempty"),
        CheckConstraint(
            "(status = 'legacy_unresolved' AND provider_account_id IS NULL) OR "
            "(status IN ('active', 'disconnected') AND "
            "provider_account_id IS NOT NULL AND length(provider_account_id) > 0)",
            name="identity_state",
        ),
        Index(
            "uq_source_accounts_verified",
            "user_id",
            "provider",
            "provider_account_id",
            unique=True,
            postgresql_where=text("provider_account_id IS NOT NULL"),
            sqlite_where=text("provider_account_id IS NOT NULL"),
        ),
        Index(
            "uq_source_accounts_legacy",
            "user_id",
            "provider",
            unique=True,
            postgresql_where=text("provider_account_id IS NULL"),
            sqlite_where=text("provider_account_id IS NULL"),
        ),
    )
    provider: Mapped[str]
    provider_account_id: Mapped[str | None]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AccountSyncState(OwnedRecord, Base):
    __tablename__ = "account_sync_states"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "source_account_id"),
        ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
        ),
        CheckConstraint(
            "(initialized AND checkpoint IS NOT NULL) OR (NOT initialized AND checkpoint IS NULL)",
            name="checkpoint_state",
        ),
    )
    provider: Mapped[str]
    source_account_id: Mapped[UUID]
    initialized: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    checkpoint: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WorkoutTombstone(OwnedRecord, Base):
    __tablename__ = "workout_tombstones"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "source_account_id", "external_id"),
        ForeignKeyConstraint(
            ["user_id", "provider", "source_account_id"],
            ["source_accounts.user_id", "source_accounts.provider", "source_accounts.id"],
        ),
        CheckConstraint("length(external_id) > 0", name="identity_nonempty"),
    )
    provider: Mapped[str]
    source_account_id: Mapped[UUID]
    external_id: Mapped[str]
    source_deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


revision = "91ab"
down_revision = "2827ecaa5ef5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # Revision-local declarations freeze the schema independently of application models.
    for model in (SourceAccount, AccountSyncState, WorkoutTombstone):
        model.__table__.create(bind)
    op.add_column("external_references", sa.Column("source_account_id", sa.Uuid(), nullable=True))
    pairs = bind.execute(
        sa.text("SELECT DISTINCT user_id, provider FROM external_references")
    ).all()
    for user_id, provider in pairs:
        account_id = uuid4()
        bind.execute(
            sa.text(
                "INSERT INTO source_accounts "
                "(id,user_id,provider,status) VALUES (:id,:user,:provider,'legacy_unresolved')"
            ),
            dict(id=account_id, user=user_id, provider=provider),
        )
        bind.execute(
            sa.text(
                "UPDATE external_references SET source_account_id=:id "
                "WHERE user_id=:user AND provider=:provider"
            ),
            dict(id=account_id, user=user_id, provider=provider),
        )
    op.alter_column("external_references", "source_account_id", nullable=False)
    op.drop_constraint("uq_external_references_user_id", "external_references", type_="unique")
    op.create_unique_constraint(
        "uq_external_references_user_id",
        "external_references",
        ["user_id", "provider", "source_account_id", "entity_type", "external_id"],
    )
    op.create_foreign_key(
        "fk_external_references_user_id_source_accounts",
        "external_references",
        "source_accounts",
        ["user_id", "provider", "source_account_id"],
        ["user_id", "provider", "id"],
    )
    op.execute("""CREATE FUNCTION guard_source_account_identity() RETURNS trigger AS $$
    BEGIN
      IF NEW.id IS DISTINCT FROM OLD.id OR NEW.user_id IS DISTINCT FROM OLD.user_id
         OR NEW.provider IS DISTINCT FROM OLD.provider
         OR (OLD.provider_account_id IS NOT NULL AND
             NEW.provider_account_id IS DISTINCT FROM OLD.provider_account_id) THEN
        RAISE EXCEPTION 'source account identity is immutable';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql""")
    op.execute("""CREATE TRIGGER source_account_identity BEFORE UPDATE ON source_accounts
                  FOR EACH ROW EXECUTE FUNCTION guard_source_account_identity()""")
    op.execute("""CREATE FUNCTION guard_sync_checkpoint() RETURNS trigger AS $$
    BEGIN
      IF OLD.checkpoint IS NOT NULL AND
         (NEW.checkpoint IS NULL OR NEW.checkpoint < OLD.checkpoint) THEN
        RAISE EXCEPTION 'checkpoint cannot regress';
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql""")
    op.execute("""CREATE TRIGGER sync_checkpoint BEFORE UPDATE ON account_sync_states
                  FOR EACH ROW EXECUTE FUNCTION guard_sync_checkpoint()""")


def downgrade() -> None:
    collision = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT 1 FROM external_references GROUP BY "
                "user_id, provider, entity_type, external_id HAVING count(*) > 1 LIMIT 1"
            )
        )
        .first()
    )
    if collision:
        raise RuntimeError("Reconcile account namespace collisions before downgrade")
    op.drop_constraint(
        "fk_external_references_user_id_source_accounts", "external_references", type_="foreignkey"
    )
    op.drop_constraint("uq_external_references_user_id", "external_references", type_="unique")
    op.create_unique_constraint(
        "uq_external_references_user_id",
        "external_references",
        ["user_id", "provider", "entity_type", "external_id"],
    )
    op.drop_column("external_references", "source_account_id")
    op.execute("DROP FUNCTION guard_sync_checkpoint() CASCADE")
    op.execute("DROP FUNCTION guard_source_account_identity() CASCADE")
    for table in ("workout_tombstones", "account_sync_states", "source_accounts"):
        op.drop_table(table)

"""Project owner-bound D1D, E421 and E422 evidence for standalone reads and planning decisions."""

from collections import Counter, defaultdict
from datetime import UTC, datetime, time, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Engine, or_, select, text, tuple_
from sqlalchemy.orm import Session

from ..adapters.hevy.analytics import HevyHistoryProfile
from ..analytics.strength import Period, StrengthFact
from ..domain.endurance import Source
from ..planning import confirmation as c
from ..planning import evidence as e
from ..planning import familiar as f
from ..planning.evidence_reconciliation import identity, reconcile
from . import confirmations, execution, familiar_snapshot
from .history_models import GarminCoverage
from .longitudinal import read_snapshot, read_training_days, training_ledger_scope
from .models import ExternalReference, SourceAccount, Workout, WorkoutTombstone
from .owner_lock import trusted_owner
from .plan_models import PlanRevision, SessionOutcome
from .plan_snapshot import canonical


def _manuals(
    db: Session, owner: UUID, start: datetime, stop: datetime, linked: set[UUID]
) -> tuple[e.Manual, ...]:
    latest = (
        execution._latest(owner)
        .where(
            SessionOutcome.outcome_version == 2,
            or_(
                (SessionOutcome.occurred_at >= start) & (SessionOutcome.occurred_at < stop),
                SessionOutcome.id.in_(linked),
            ),
        )
        .with_only_columns(SessionOutcome.plan_id, SessionOutcome.week, SessionOutcome.slot)
    )
    scope = tuple_(SessionOutcome.plan_id, SessionOutcome.week, SessionOutcome.slot)
    rows = db.scalars(
        select(SessionOutcome).where(
            SessionOutcome.user_id == owner, SessionOutcome.outcome_version == 2, scope.in_(latest)
        )
    )
    chains = defaultdict(dict)
    origins = set()
    for row in rows:
        origins.add(row.origin_revision_id)
        chains[row.plan_id, row.week, row.slot, row.origin_revision_id][row.supersedes_id] = row
    prescriptions = {}
    blocks = {}
    for revision in db.scalars(
        select(PlanRevision).where(PlanRevision.user_id == owner, PlanRevision.id.in_(origins))
    ):
        candidate = familiar_snapshot.read_candidate(revision.snapshot)
        blocks[revision.id] = candidate.block_key, candidate.block_revision
        for day in candidate.days:
            for occurrence in day.sessions:
                prescriptions[revision.id, str(occurrence.occurrence)] = occurrence
    result = []
    for (cycle, week, slot, origin), chain in chains.items():
        tip = chain[None]
        history = []
        while tip:
            history.append(execution.familiar_assertion(tip))
            tip = chain.get(tip.id)
        result.append(
            e.Manual(
                block_key=blocks[origin][0],
                block_revision=blocks[origin][1],
                cycle=cycle,
                week=week,
                origin=origin,
                prescribed=prescriptions[origin, slot],
                history=tuple(history),
            )
        )
    return tuple(result)


def _supports(
    db: Session,
    owner: UUID,
    account: UUID,
    members: tuple[e.NativeMember, ...],
    start: datetime,
    stop: datetime,
) -> tuple[c.Support, ...]:
    current_ids = {i for m in members if (i := identity(m)) is not None}
    # Older displays can outlive a replaced child. Select them by their own recorded
    # workout start, even when the current projection can no longer find that UUID.
    rows = db.scalars(
        text("""SELECT DISTINCT cm.member FROM confirmation_members cm
        JOIN confirmation_receipts r ON (r.user_id,r.command)=(cm.user_id,cm.command)
        WHERE cm.user_id=:owner AND cm.account=:account AND
          (cm.member=ANY(CAST(:current AS uuid[])) OR EXISTS (
            SELECT 1 FROM jsonb_array_elements(r.payload#>'{display,members}') m
            WHERE coalesce(m->>'member',m->>'workout')=cm.member::text
              AND (m->>'occurred_at')::timestamptz >= :start
              AND (m->>'occurred_at')::timestamptz < :stop))
        ORDER BY cm.member"""),
        dict(owner=owner, account=account, current=list(current_ids), start=start, stop=stop),
    )
    return confirmations.review_members(
        db, owner, account, tuple(rows), tuple(m.display for m in members if m.display is not None)
    )


def _current_members(
    db: Session, owner: UUID, accounts: set[UUID], members: list[e.NativeMember]
) -> tuple[e.NativeMember, ...]:
    ref = ExternalReference
    tomb = WorkoutTombstone
    # A pending, undated deletion can coexist with a still-active canonical workout.
    references = {
        ident: (created, imported, tombstone)
        for ident, created, imported, tombstone in db.execute(
            select(ref.id, Workout.created_at, ref.first_imported_at, tomb)
            .join(Workout, (Workout.id == ref.workout_id) & (Workout.user_id == owner))
            .outerjoin(
                tomb,
                (tomb.user_id == owner)
                & (tomb.provider == ref.provider)
                & (tomb.source_account_id == ref.source_account_id)
                & (tomb.external_id == ref.external_id)
                & tomb.pending,
            )
            .where(
                ref.user_id == owner,
                ref.source_account_id.in_(accounts),
                ref.id.in_({m.fact.reference_id for m in members}),
            )
        )
    }

    def ordinal(m: e.NativeMember) -> tuple | None:
        d = m.display
        return (
            (d.account, d.workout, d.exercise, d.group, d.ordinal)
            if isinstance(d, c.StrengthFact)
            else None
        )

    occupied = Counter(ordinal(m) for m in members if isinstance(m.display, c.StrengthFact))
    result = []
    for member in members:
        created, imported, tombstone = references[member.fact.reference_id]
        # These clocks describe the parent rows. Neither dates a particular child revision.
        values = dict(workout_created_at=created, reference_first_imported_at=imported)
        if tombstone:
            values.update(
                display=None,
                limitation="pending source deletion",
                pending_deletion=e.PendingDeletion(
                    id=tombstone.id,
                    source_deleted_at=tombstone.source_deleted_at,
                    observed_at=tombstone.observed_at,
                ),
            )
        elif occupied[ordinal(member)] > 1:
            values.update(display=None, limitation="mapped source ordinals overlap")
        result.append(member.model_copy(update=values))
    return tuple(result)


class EvidenceScopeUnavailable(ValueError):
    """An account selection is no longer valid for this owner and policy."""


def query_planning_evidence(engine: Engine, scope: e.Scope) -> e.Projection:
    """Read current synthetic evidence. No historical as-of or approval-time guarantee."""
    owner = trusted_owner()
    familiar_snapshot.require_preview_owner(owner)
    with read_snapshot(engine) as db:
        return _read_projection(db, owner, scope)


def _read_projection(db: Session, owner: UUID, scope: e.Scope) -> e.Projection:
    familiar_snapshot.require_preview_owner(owner)
    scope = e.Scope.model_validate(scope)
    period = Period(scope.start, scope.stop, ZoneInfo(scope.zone))
    start, stop = (
        datetime.combine(d, time.min, period.zone).astimezone(UTC)
        for d in (scope.start, scope.stop)
    )
    contexts = {(ctx.account, ctx.member): ctx for ctx in scope.contexts}
    expected = [
        (scope.strength_account, "hevy"),
        (scope.endurance_account, "garmin"),
        (scope.recovery_account, "garmin"),
    ]
    accounts = {
        r.id: r
        for r in db.scalars(
            select(SourceAccount).where(
                SourceAccount.user_id == owner,
                SourceAccount.id.in_([i for i, _ in expected if i]),
            )
        )
    }
    for i, provider in expected:
        if i and (
            i not in accounts
            or accounts[i].provider != provider
            or accounts[i].status == "legacy_unresolved"
        ):
            raise EvidenceScopeUnavailable("invalid source account for planning evidence")
    profile = (
        HevyHistoryProfile(
            scope.strength_account,
            frozenset(scope.external_load_templates),
            frozenset(scope.lower_body_templates),
            frozenset(scope.non_lower_body_templates),
        )
        if scope.strength_account
        else None
    )
    zones = {
        i: ZoneInfo(z)
        for i, z in (
            (scope.endurance_account, scope.endurance_zone),
            (scope.recovery_account, scope.recovery_zone),
        )
        if i and z
    }

    def garmin(i: UUID | None) -> Source | None:
        return Source(owner, "garmin", i) if i else None

    training = read_training_days(
        db,
        owner,
        period,
        zones,
        profile,
        garmin(scope.endurance_account),
        garmin(scope.recovery_account),
        {i: a.status for i, a in accounts.items()},
    )
    days = []
    members = []
    for day in training:
        strength = day.strength
        activity = day.endurance.days[0] if day.endurance else None
        running = (
            next((s for s in day.endurance.sports if s.sport == "running"), None)
            if activity
            else None
        )
        days.append(
            e.Day(
                day=day.day,
                open_issues=day.open_issues,
                strength_acquisition=strength.acquisition if strength else None,
                strength_account_status=strength.account_status if strength else None,
                activities=activity.activities if activity else None,
                instructions=activity.instructions if activity else None,
                discrepancies=activity.discrepancies if activity else (),
                scan_started_at=activity.scan_started_at if activity else None,
                full_day_zero_exclusion=activity.full_day_empty_exclusion(None)
                if activity
                else None,
                running_count=running.sessions.value if running else None,
                running_count_status=running.sessions.status if running else None,
                recovery=day.recovery,
            )
        )
        for fact in (
            *(strength.facts if strength else ()),
            *(activity.facts if activity else ()),
        ):
            member = fact.row.set_id if isinstance(fact, StrengthFact) else fact.workout_id
            members.append(
                e.bridge(
                    fact,
                    contexts.get((fact.source.source_account_id, member)),
                    activity_discrepancies=activity.discrepancies
                    if activity and not isinstance(fact, StrengthFact)
                    else (),
                )
            )

    members = _current_members(db, owner, set(accounts), members)
    limitations = {
        (m.fact.source.source_account_id, identity(m)): m.limitation
        for m in members
        if m.limitation
    }
    supports = {}
    for account in dict.fromkeys((scope.strength_account, scope.endurance_account)):
        if account:
            selected = tuple(m for m in members if m.fact.source.source_account_id == account)
            for support in _supports(db, owner, account, selected, start, stop):
                supports[account, support.member] = support
    manual = _manuals(
        db,
        owner,
        start,
        stop,
        {s.effective_link.outcome for s in supports.values() if s.effective_link},
    )
    return e.Projection(
        owner=owner,
        scope=scope,
        days=tuple(days),
        confirmations=tuple(
            e.Confirmation(
                account=s.history[-1].source.account,
                member=s.member,
                state=s.state,
                reason=(limitations.get((s.history[-1].source.account, s.member)) or s.reason)
                if s.state == "stale"
                else s.reason,
                confirmed=tuple(sorted(s.confirmed.items())),
                unconfirmed=s.unconfirmed,
                history=s.history,
                ambiguous_set_link=s.ambiguous_set_link,
                effective_link=s.effective_link,
            )
            for s in sorted(
                supports.values(), key=lambda s: (s.history[-1].source.account, s.member)
            )
        ),
        performances=reconcile(tuple(members), supports, manual, period.zone),
    )


# Increment on a material change to selection or field/qualification semantics.
DECISION_POLICY = "current-accepted-training-v1"


def _representative_scope(db: Session, owner: UUID, context: f.Context) -> e.Scope:
    selected = {}
    for provider, account in db.execute(
        select(SourceAccount.provider, SourceAccount.id).where(
            SourceAccount.user_id == owner,
            SourceAccount.provider.in_(("hevy", "garmin")),
            SourceAccount.status != "legacy_unresolved",
        )
    ):
        if provider in selected:
            raise EvidenceScopeUnavailable(
                "multiple bound accounts for provider; supply an explicit evidence scope"
            )
        selected[provider] = account
    return e.Scope(
        start=context.history_start,
        stop=context.history_start + timedelta(days=7),
        zone=context.zone,
        strength_account=selected.get("hevy"),
        endurance_account=selected.get("garmin"),
        recovery_account=selected.get("garmin"),
    )


def freeze_inputs(
    db: Session, owner: UUID, context: f.Context, scope: e.Scope | None, cutoff: datetime
) -> e.DecisionInputs:
    """Called under the owner lock. All reads use the command's physical transaction."""
    familiar_snapshot.require_preview_owner(owner)
    if trusted_owner() != owner:
        raise PermissionError("planning evidence owner differs from the trusted binding")
    if db.scalar(text("SHOW transaction_isolation")) != "read committed":
        raise ValueError("planning evidence decisions require a read-committed transaction")
    db.flush()
    # Avoid cached ORM entities from before lock acquisition. Closing this read Session
    # leaves the enclosing transaction, its writes and its locks with the command.
    with Session(db.connection(), join_transaction_mode="rollback_only", autoflush=False) as reader:
        reader.execute(text("SET LOCAL TIME ZONE 'UTC'"))
        selection = "explicit" if scope is not None else "representative-week"
        scope = scope if scope is not None else _representative_scope(reader, owner, context)
        projection = _read_projection(reader, owner, scope)
        accounts = tuple(
            e.SelectedAccount(
                id=row.id,
                provider=row.provider,
                provider_account_id=row.provider_account_id,
                status=row.status,
            )
            for row in reader.scalars(
                select(SourceAccount)
                .where(
                    SourceAccount.user_id == owner,
                    SourceAccount.id.in_(
                        [scope.strength_account, scope.endurance_account, scope.recovery_account]
                    ),
                )
                .order_by(SourceAccount.id)
            )
        )
        ledger = GarminCoverage
        receipts = tuple(
            e.CoverageReceipt(
                account=row.source_account_id,
                day=row.local_date,
                category=row.category,
                receipts_json=canonical(row.receipts),
            )
            for row in reader.scalars(
                select(ledger)
                .where(
                    *training_ledger_scope(
                        ledger,
                        owner,
                        scope.start,
                        scope.stop,
                        scope.endurance_account,
                        scope.recovery_account,
                    )
                )
                .order_by(ledger.source_account_id, ledger.local_date, ledger.category)
            )
        )
        return e.DecisionInputs(
            policy=DECISION_POLICY,
            selection=selection,
            cutoff=cutoff,
            projection=projection,
            accounts=accounts,
            coverage_receipts=receipts,
        )

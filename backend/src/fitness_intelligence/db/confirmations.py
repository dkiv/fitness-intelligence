"""Owner-scoped synthetic confirmation commands, bound by PlanCommands."""

from collections import Counter, defaultdict
from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, aliased

from ..planning import confirmation as c
from ..planning import familiar as f
from . import execution
from .confirmation_models import ConfirmationMember as Member
from .confirmation_models import ConfirmationReceipt as Stored
from .plan_models import SessionOutcome
from .plan_snapshot import InvalidSnapshot, canonical


def decode(row: Stored) -> c.Receipt:
    intent = c.Intent.model_validate_json(canonical(row.payload))
    if (
        canonical(intent.model_dump(mode="json")) != canonical(row.payload)
        or c.digest(intent) != row.intent_digest
        or intent.display.owner != row.user_id
    ):
        raise InvalidSnapshot("invalid sealed confirmation intent")
    return c.Receipt(
        command=row.command,
        actor=row.actor,
        recorded_at=row.recorded_at,
        intent_digest=row.intent_digest,
        intent=intent,
    )


def receipt(db: Session, owner: UUID, command: UUID) -> c.Receipt:
    row = db.scalars(select(Stored).where(Stored.user_id == owner, Stored.command == command)).one()
    return decode(row)


def _tips(owner: UUID) -> Select[tuple[Member]]:
    successor = aliased(Member)
    return select(Member).where(
        Member.user_id == owner,
        ~select(successor.command)
        .where(
            successor.user_id == owner,
            successor.member == Member.member,
            successor.supersedes == Member.command,
        )
        .exists(),
    )


# A current execution assertion pins exactly one approved occurrence. Its prescription
# has unique movement/variation pairs, group keys per exercise and ordinals per group.
type PrescribedSet = tuple[UUID, str, str, str, int]


def _prescribed_set(outcome: UUID, source: c.StrengthFact) -> PrescribedSet:
    return outcome, source.movement, source.variation, source.group, source.ordinal


def _linked_sets(
    db: Session, owner: UUID, outcomes: set[UUID], replacing: set[UUID]
) -> Counter[PrescribedSet]:
    counts: Counter[PrescribedSet] = Counter()
    if not outcomes:
        return counts
    rows = db.execute(
        _tips(owner)
        .join(Stored, (Stored.user_id == Member.user_id) & (Stored.command == Member.command))
        .where(Member.outcome.in_(outcomes), Member.member.not_in(replacing))
        .with_only_columns(Stored, Member.member)
    )
    # Decode each receipt once. Only its still-effective member edges occupy ordinals.
    members_by_receipt: dict[Stored, set[UUID]] = defaultdict(set)
    for receipt_row, member in rows:
        members_by_receipt[receipt_row].add(member)
    for receipt_row, members in members_by_receipt.items():
        intent = decode(receipt_row).intent
        for fact, answer in zip(intent.display.members, intent.answers, strict=True):
            if fact.member in members and isinstance(fact, c.StrengthFact) and answer.outcome:
                counts[_prescribed_set(answer.outcome, fact)] += 1
    return counts


def _link(db: Session, owner: UUID, fact: c.Fact, outcome: UUID) -> tuple[UUID, str]:
    row = db.scalar(
        execution._latest(owner).where(
            SessionOutcome.id == outcome, SessionOutcome.outcome_version == 2
        )
    )
    if (
        row is None
        or row.occurred_at != fact.occurred_at
        or row.actual["status"] not in ("completed", "partial")
    ):
        raise ValueError("link requires the current performed assertion at the exact workout start")
    # E421 already verified the two approvals and occurrence at this instant.
    origin, week, _ = execution._familiar_week(db, owner, row.plan_id, row.revision_id, row.week)
    if origin != row.origin_revision_id:
        raise ValueError("linked execution origin changed")
    prescription = next(
        s.prescription for d in week.days for s in d.sessions if str(s.occurrence) == row.slot
    )
    if isinstance(fact, c.StrengthFact):
        if not isinstance(prescription, f.Strength) or not any(
            (e.movement, e.variation, e.equipment, e.load_convention, g.key, g.kind, s.ordinal)
            == (
                fact.movement,
                fact.variation,
                fact.equipment,
                fact.load_convention,
                fact.group,
                fact.kind,
                fact.ordinal,
            )
            for e in prescription.exercises
            for g in e.groups
            for s in g.sets
        ):
            raise ValueError("source set does not match the linked exercise and ordinal")
    else:
        if not isinstance(prescription, f.Running) or fact.role != prescription.role:
            raise ValueError("source outing does not match the linked role")
        if any(
            step.index > len(prescription.steps)
            or step.purpose != prescription.steps[step.index - 1].purpose
            for step in fact.achieved_steps
        ):
            raise ValueError("source step differs from the linked prescription")

    return row.plan_id, row.slot


def _attribution(db: Session, owner: UUID, outcome: UUID) -> c.Attribution:
    row = db.scalars(
        select(SessionOutcome).where(
            SessionOutcome.user_id == owner,
            SessionOutcome.id == outcome,
            SessionOutcome.outcome_version == 2,
        )
    ).one()
    current = (
        db.scalar(
            select(SessionOutcome.id).where(
                SessionOutcome.user_id == owner, SessionOutcome.supersedes_id == outcome
            )
        )
        is None
    )
    return c.Attribution(
        outcome=outcome,
        cycle=row.plan_id,
        week=row.week,
        occurrence=UUID(row.slot),
        origin_revision=row.origin_revision_id,
        effective_head=row.revision_id,
        occurred_at=row.occurred_at,
        current=current,
    )


def record(
    db: Session,
    owner: UUID,
    command: UUID,
    intent: c.Intent,
    current: tuple[c.Fact, ...],
    now: datetime,
) -> c.Receipt:
    intent = c.Intent.model_validate(intent)
    if intent.display.owner != owner:
        raise ValueError("wrong displayed owner")
    hashed = c.digest(intent)
    existing = db.get(Stored, (owner, command))
    if existing:
        result = decode(existing)
        if result.intent_digest != hashed:
            raise ValueError("confirmation command already used for different intent")
        return result
    facts = c.index_facts(owner, intent.display.account, current)
    ids = {m.member for m in intent.display.members}
    if facts.keys() - ids:
        raise ValueError("unexpected member in current display")
    tips = {m.member: m for m in db.scalars(_tips(owner).where(Member.member.in_(ids)))}
    # One performance per logical occurrence, including proposed links within this batch.
    linked = db.execute(
        _tips(owner)
        .join(
            SessionOutcome,
            (SessionOutcome.id == Member.outcome) & (SessionOutcome.user_id == Member.user_id),
        )
        .where(
            Member.member.not_in(ids),
            SessionOutcome.id.in_(
                execution._latest(owner).with_only_columns(SessionOutcome.id).correlate(None)
            ),
        )
        .with_only_columns(Member.workout, SessionOutcome.plan_id, SessionOutcome.slot)
    ).all()
    by_workout = {w: (p, s) for w, p, s in linked}
    by_occurrence = {(p, s): w for w, p, s in linked}
    strength_outcomes = {
        answer.outcome
        for fact, answer in zip(intent.display.members, intent.answers, strict=True)
        if isinstance(fact, c.StrengthFact) and answer.outcome is not None
    }
    occupied = _linked_sets(db, owner, strength_outcomes, replacing=ids)
    for fact, answer in zip(intent.display.members, intent.answers, strict=True):
        tip = tips.get(fact.member)
        if (tip.command if tip else None) != answer.supersedes:
            raise ValueError("must supersede the current assertion for this member")
        if tip and (tip.account, tip.workout) != (fact.account, fact.workout):
            raise ValueError("member lineage changed source identity")
        if fact.occurred_at > now:
            raise ValueError("cannot confirm future observations")
        if answer.disposition == "withdraw":
            prior = receipt(db, owner, answer.supersedes)
            original = next(m for m in prior.intent.display.members if m.member == fact.member)
            if c.digest(original) != c.digest(fact):
                raise ValueError("withdrawal requires its predecessor's original display")
        elif fact.member not in facts or c.digest(facts[fact.member]) != c.digest(fact):
            raise ValueError("display changed before confirmation")
        if answer.outcome:
            key = _link(db, owner, fact, answer.outcome)
            if (
                by_workout.setdefault(fact.workout, key) != key
                or by_occurrence.setdefault(key, fact.workout) != fact.workout
            ):
                raise ValueError("workout or planned occurrence already linked elsewhere")
            if isinstance(fact, c.StrengthFact):
                ordinal = _prescribed_set(answer.outcome, fact)
                if occupied[ordinal]:
                    raise ValueError("prescribed set ordinal already linked to another source set")
                occupied[ordinal] += 1
    row = Stored(
        user_id=owner,
        actor=owner,
        command=command,
        recorded_at=now,
        payload=intent.model_dump(mode="json"),
        intent_digest=hashed,
    )
    db.add(row)
    db.flush()  # PostgreSQL inserts and constrains all member edges atomically.
    return decode(row)


def review(
    db: Session, owner: UUID, command: UUID, current: tuple[c.Fact, ...]
) -> tuple[c.Support, ...]:
    scope = receipt(db, owner, command).intent.display
    return review_members(db, owner, scope.account, tuple(m.member for m in scope.members), current)


def review_members(
    db: Session, owner: UUID, account: UUID, members: tuple[UUID, ...], current: tuple[c.Fact, ...]
) -> tuple[c.Support, ...]:
    facts = c.index_facts(owner, account, current)
    rows = db.scalars(
        select(Stored)
        .join(Member, (Member.user_id == Stored.user_id) & (Member.command == Stored.command))
        .where(Stored.user_id == owner, Member.account == account, Member.member.in_(members))
    ).unique()
    chains: dict[UUID, dict[UUID | None, c.Assertion]] = {m: {} for m in members}
    for row in rows:
        saved = decode(row)
        for source, answer in zip(saved.intent.display.members, saved.intent.answers, strict=True):
            if source.member in members:
                chains[source.member][answer.supersedes] = c.Assertion(
                    command=saved.command,
                    recorded_at=saved.recorded_at,
                    source=source,
                    source_digest=c.digest(source),
                    answer=answer,
                    link=_attribution(db, owner, answer.outcome) if answer.outcome else None,
                )
    # Earlier receipts can predate the uniqueness check. Include other batches even
    # when the caller reviews only one of the two members sharing an ordinal.
    outcomes = {
        a.link.outcome
        for chain in chains.values()
        for a in chain.values()
        if isinstance(a.source, c.StrengthFact) and a.link and a.link.current
    }
    occupied = _linked_sets(db, owner, outcomes, replacing=set())
    result = []
    for member in members:
        chain = chains[member]
        history = [chain[None]]
        while history[-1].command in chain:
            history.append(chain[history[-1].command])
        tip = history[-1]
        source = tip.source
        answer = tip.answer
        state = {
            "confirm": "confirmed",
            "exclude": "excluded",
            "uncertain": "uncertain",
            "withdraw": "withdrawn",
        }[answer.disposition]
        actual = facts.get(source.member)
        reason = None
        if state == "confirmed":
            if actual is None:
                reason = "canonical member absent or replaced"
            elif actual.deleted or not actual.reference_active:
                reason = "workout deleted or source reference inactive"
            elif c.digest(actual) != tip.source_digest:
                reason = "source content, identity or mapping changed"
            if reason:
                state = "stale"
        confirmed = {k: source.eligible[k] for k in answer.fields} if state == "confirmed" else {}
        result.append(
            c.Support(
                member=source.member,
                history=tuple(history),
                state=state,
                reason=reason,
                ambiguous_set_link=bool(
                    isinstance(source, c.StrengthFact)
                    and tip.link
                    and tip.link.current
                    and occupied[_prescribed_set(tip.link.outcome, source)] > 1
                ),
                confirmed=confirmed,
                unconfirmed=tuple(sorted(source.eligible.keys() - confirmed.keys())),
                independent_report=answer.reported,
            )
        )
    return tuple(result)

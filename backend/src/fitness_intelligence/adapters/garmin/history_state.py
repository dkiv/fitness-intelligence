"""Day-grained progress shared by the bounded range commands."""

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from fitness_intelligence.adapters.local_account import private_config
from fitness_intelligence.db.history_models import GarminCoverage, GarminIssue
from fitness_intelligence.domain.endurance import Source

from .client import GarminError


class Category(StrEnum):
    ACTIVITIES = "activities"
    STEPS = "running_steps"
    EXPENDITURE = "expenditure"
    RESTING = "resting_hr"
    SLEEP = "sleep"
    HRV = "hrv"
    INTAKE = "intake"
    WEIGHT = "weight"


def digest(value: object) -> str:
    return sha256(
        json.dumps(value, default=str, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class WeightSegment:
    source: Source
    first: date
    last: date
    minimum: Decimal
    maximum: Decimal
    fingerprint: str

    @classmethod
    def load(cls, path: Path, source: Source) -> "WeightSegment":
        """Operator-attested references and alert envelope, restricted to one account."""
        cfg = private_config(path)
        try:
            if (
                cfg["approved"] is not True
                or cfg["unit"] != "g"
                or UUID(cfg["user_id"]) != source.owner_id
                or UUID(cfg["source_account_id"]) != source.source_account_id
            ):
                raise ValueError
            first, last = (date.fromisoformat(cfg[k]) for k in ("start", "end"))
            refs = cfg["references"]
            days = {date.fromisoformat(r["date"]) for r in refs}
            masses = [Decimal(r["verified_grams"]) for r in refs]
            if (
                len(days) < 2
                or not min(days) <= first <= last <= max(days)
                or not all(v.is_finite() and v > 0 for v in masses)
            ):
                raise ValueError
            # Broad anomaly screen relative to independently verified wire values.
            # These bounds never select the unit of an entry.
            return cls(source, first, last, min(masses) / 2, max(masses) * 2, digest(cfg))
        except (KeyError, TypeError, ArithmeticError, ValueError):
            raise GarminError("invalid private weight verification segment") from None


@dataclass(frozen=True)
class Scope:
    mode: str
    start: date
    end: date
    categories: tuple[Category, ...]
    pass_id: UUID
    overlap: int = 7
    weight: WeightSegment | None = None

    def validate(self) -> None:
        if (
            self.mode not in ("backfill", "incremental", "repair")
            or self.start > self.end
            or (self.end - self.start).days >= 3660
            or not 1 <= self.overlap <= 366
            or not self.categories
            or len(set(self.categories)) != len(self.categories)
        ):
            raise GarminError("invalid historical scope")
        if Category.STEPS in self.categories and Category.ACTIVITIES not in self.categories:
            raise GarminError("running steps require activity enumeration")
        if Category.WEIGHT in self.categories and not (
            self.weight and self.weight.first <= self.start <= self.end <= self.weight.last
        ):
            raise GarminError("range outside verified weight segment")

    def policy(self, category: Category) -> str:
        return (
            self.weight.fingerprint if self.weight and category == Category.WEIGHT else "history-v1"
        )

    def done(self, row: GarminCoverage | None, category: Category, day: date) -> bool:
        if (
            row is None
            or row.status not in ("empty", "observed")
            or row.policy != self.policy(category)
        ):
            return False
        if self.mode == "backfill":
            return True
        if self.mode == "incremental" and (self.end - day).days >= self.overlap:
            return True
        return row.pass_key == str(self.pass_id)


def days(start: date, end: date) -> Iterable[date]:
    for offset in range((end - start).days + 1):
        yield start + timedelta(days=offset)


def account_key(source: Source) -> dict:
    return dict(
        provider=source.provider,
        user_id=source.owner_id,
        source_account_id=source.source_account_id,
    )


def day_key(source: Source, category: Category, day: date) -> dict:
    return account_key(source) | dict(category=category.value, local_date=day)


def coverage(
    session: Session,
    source: Source,
    scope: Scope,
    category: Category,
    day: date,
    status: str,
    count: int | None = None,
    receipts: dict[str, dict] | None = None,
) -> None:
    key = day_key(source, category, day)
    row = session.get(GarminCoverage, key)
    if row is None:
        row = GarminCoverage(**key, receipts={})
        session.add(row)
    if row.pass_key != str(scope.pass_id) or row.policy != scope.policy(category):
        row.receipts = {}
    row.status, row.attempted_at = status, datetime.now(UTC)
    row.pass_key, row.policy = str(scope.pass_id), scope.policy(category)
    if status in ("observed", "empty"):
        row.last_success = row.attempted_at
        row.eligible_count = count
        row.receipts = {}
    elif receipts is not None:
        row.receipts = dict(receipts)


def issue(
    session: Session,
    source: Source,
    category: Category,
    day: date,
    subject: str,
    reason: str,
    evidence: object,
    when: datetime,
) -> None:
    key = day_key(source, category, day) | dict(subject=subject, reason=reason)
    row = session.get(GarminIssue, key)
    if row is None:
        row = GarminIssue(**key, first_seen=when)
        session.add(row)
    row.evidence_digest = digest(evidence)
    row.last_seen, row.resolved_at = when, None


def close_issues(
    session: Session,
    source: Source,
    category: Category,
    day: date,
    subject: str,
    reasons: tuple[str, ...],
    when: datetime,
) -> None:
    query = (
        select(GarminIssue)
        .filter_by(**day_key(source, category, day), subject=subject, resolved_at=None)
        .where(GarminIssue.reason.in_(reasons))
    )
    for row in session.scalars(query):
        row.resolved_at = when


def day_status(session: Session, source: Source, category: Category, day: date) -> dict:
    """Internal analytics lookup. Open day-level issues qualify all retained rows for the day."""
    key = day_key(source, category, day)
    row = session.get(GarminCoverage, key)
    active = list(session.scalars(select(GarminIssue.reason).filter_by(**key, resolved_at=None)))
    return dict(
        acquisition=row.status if row else "never_queried",
        last_success=row.last_success if row else None,
        last_eligible_count=row.eligible_count if row else None,
        reconciliation="unresolved" if active else "no_open_issue",
        reasons=sorted(set(active)),
    )

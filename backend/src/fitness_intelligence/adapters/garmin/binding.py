"""Trusted single-owner evidence, and the five-read B2 comparison."""

import json
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from fitness_intelligence.adapters.local_account import private_config
from fitness_intelligence.db.endurance_models import GarminEnrollment
from fitness_intelligence.db.models import SourceAccount, User
from fitness_intelligence.domain.endurance import Source

from .client import Endpoint, GarminClient, GarminError
from .mapping import LIST_STAMP, GarminBinding, MappingError, Row, integer, obj, rows, stamp


class Feed(StrEnum):
    DAILY = "daily"
    SLEEP = "sleep"
    HRV = "hrv"


PROFILE_FIELDS = {
    Feed.DAILY: "userProfileId",
    Feed.SLEEP: "userProfilePK",
    Feed.HRV: "userProfilePk",
}


class EvidenceType(StrEnum):
    INDEPENDENT = "independent"
    WITNESSED = "locally_witnessed"


@dataclass(frozen=True, repr=False)
class Evidence:
    source: Source
    activity_id: int
    day: date
    feeds: tuple[Feed, ...]
    kind: EvidenceType
    profile_id: int | None = None
    durability_confirmed: bool = False
    approved_pin: str | None = None

    @classmethod
    def load(cls, path: Path) -> "Evidence":
        config = private_config(path)
        kind = EvidenceType(config.get("evidence_type", "independent"))
        profile = config.get("profile_id")
        durable = config.get("durability_confirmed") is True
        if kind == EvidenceType.INDEPENDENT:
            if config.get("independent_profile_confirmed") is not True:
                raise GarminError("independent profile evidence required")
            integer(profile, minimum=1, bits=64)
        elif (
            config.get("key_issued_in_authenticated_session") is not True
            or config.get("owned_activity_confirmed") is not True
            or profile is not None
            or durable
            or config.get("independent_profile_confirmed")
        ):
            raise GarminError("invalid locally witnessed evidence")
        feeds = config["feeds"]
        if not isinstance(feeds, list) or len(feeds) != len(set(feeds)):
            raise GarminError("invalid feed selection")
        return cls(
            Source(UUID(config["user_id"]), "garmin", UUID(config["source_account_id"])),
            integer(config["known_activity_id"], minimum=1, bits=64),
            date.fromisoformat(config["known_day"]),
            tuple(Feed(feed) for feed in feeds),
            kind,
            profile,
            durable,
            config.get("approved_pin"),
        )

    def receipt(self, binding: GarminBinding) -> str:
        # A private comparison value for this exact candidate and ceremony. It grants no access.
        parts = [
            "garmin-local-pin-v1",
            str(self.source.owner_id),
            str(self.source.source_account_id),
            self.kind,
            self.activity_id,
            self.day.isoformat(),
            sorted(self.feeds),
            binding.profile_id,
        ]
        return sha256(json.dumps(parts, separators=(",", ":")).encode()).hexdigest()

    def resolve(
        self,
        session: Session,
        *,
        allow_new: bool,
        observed: GarminBinding | None = None,
        for_write: bool = False,
    ) -> GarminBinding | None:
        """Resolve both account keys and the original enrollment policy under the local owner."""
        source = self.source
        if session.scalar(select(User.id).where(User.id == source.owner_id)) is None:
            raise GarminError("local owner unresolved")
        profile = observed.profile_id if observed else self.profile_id
        keys = [SourceAccount.id == source.source_account_id]
        if profile is not None:
            keys.append(
                (SourceAccount.provider == "garmin")
                & (SourceAccount.provider_account_id == str(profile))
            )
        query = (
            select(SourceAccount)
            .where(SourceAccount.user_id == source.owner_id, or_(*keys))
            .execution_options(populate_existing=True)
        )
        if for_write:
            query = query.with_for_update()
        account = session.scalars(query).one_or_none()
        if account is None:
            if allow_new:
                return None
            raise GarminError("active enrollment required")
        binding = GarminBinding.from_account(owner_id=source.owner_id, account=account)
        if binding.source != source or (profile is not None and profile != binding.profile_id):
            raise GarminError("local account mismatch")
        policy = session.scalar(
            select(GarminEnrollment)
            .filter_by(user_id=source.owner_id, source_account_id=source.source_account_id)
            .execution_options(populate_existing=True)
        )
        # Before b302 the only permitted path required independently confirmed identity.
        kind = policy.evidence_type if policy else EvidenceType.INDEPENDENT
        if kind != self.kind or (
            self.kind == EvidenceType.WITNESSED and policy.approved_pin != self.receipt(binding)
        ):
            raise GarminError("enrollment evidence mismatch")
        return binding

    def enroll(
        self, session: Session, observed: GarminBinding, existing: GarminBinding | None
    ) -> None:
        source = self.source
        receipt = None
        if self.kind == EvidenceType.WITNESSED:
            receipt = self.receipt(observed)
            if self.approved_pin != receipt:
                raise GarminError("explicit approval of the verified candidate required")
        if existing is None:
            session.add(
                SourceAccount(
                    id=source.source_account_id,
                    user_id=source.owner_id,
                    provider="garmin",
                    provider_account_id=str(observed.profile_id),
                    status="active",
                )
            )
            session.flush()
        policy = session.scalar(
            select(GarminEnrollment).filter_by(
                user_id=source.owner_id, source_account_id=source.source_account_id
            )
        )
        if policy is None:
            session.add(
                GarminEnrollment(
                    source_account_id=source.source_account_id,
                    user_id=source.owner_id,
                    provider="garmin",
                    evidence_type=self.kind,
                    approved_pin=receipt,
                )
            )


class ComparisonError(GarminError):
    """Contains only the fixed check name and a fixed outcome."""


def compare_profile(binding: GarminBinding, row: Row, key: str, comparison: str) -> None:
    try:
        value = integer(row.get(key), minimum=1, bits=64)
    except MappingError:
        raise ComparisonError(f"{comparison}: insufficient evidence") from None
    if value != binding.profile_id:
        raise ComparisonError(f"{comparison}: mismatch")


def read_page(client: GarminClient, day: date) -> dict[int, Row]:
    payload = client.read(
        Endpoint.ACTIVITIES,
        params={
            "startDate": day.isoformat(),
            "endDate": day.isoformat(),
            "start": 0,
            "limit": 3,
        },
    )
    page = rows(payload)
    if len(page) > 3:
        raise ComparisonError("activity page: exceeds bound")
    found = {}
    for row in page:
        ident = integer(row.get("activityId"), minimum=1, bits=64)
        if ident in found or stamp(row.get("startTimeLocal"), LIST_STAMP).date() != day:
            raise ComparisonError("activity page: duplicate or wrong date")
        found[ident] = row
    return found


def check_owners(page: dict[int, Row], binding: GarminBinding) -> None:
    for row in page.values():
        compare_profile(binding, row, "ownerId", "activity search owner")


def search_page(client: GarminClient, binding: GarminBinding, day: date) -> dict[int, Row]:
    page = read_page(client, day)
    check_owners(page, binding)
    return page


def detail_for(client: GarminClient, binding: GarminBinding, ident: int) -> Row:
    detail = obj(client.read(Endpoint.DETAIL, activity_id=ident))
    if integer(detail.get("activityId"), minimum=1, bits=64) != ident:
        raise ComparisonError("activity detail: request mismatch")
    compare_profile(binding, detail, "userProfileId", "activity detail owner")
    return detail


def feed_for(client: GarminClient, binding: GarminBinding, day: date, feed: Feed) -> Row:
    if feed == Feed.HRV:
        row = obj(client.read(Endpoint.HRV, day=day.isoformat()))
    elif feed == Feed.SLEEP:
        row = obj(client.read(Endpoint.SLEEP, params={"date": day.isoformat()}))
    else:
        row = obj(client.read(Endpoint.DAILY, params={"calendarDate": day.isoformat()}))
    compare_profile(binding, row, PROFILE_FIELDS[feed], feed.value)
    dated = row.get("hrvSummary") if feed == Feed.HRV else row
    if dated is None or obj(dated).get("calendarDate") is None:
        raise ComparisonError(f"{feed.value} date: insufficient evidence")
    if obj(dated)["calendarDate"] != day.isoformat():
        raise ComparisonError(f"{feed.value} date: mismatch")
    return row


@dataclass(repr=False)
class VerifiedSample:
    binding: GarminBinding
    page: dict[int, Row]
    detail: Row
    feeds: dict[Feed, Row] = field(default_factory=dict)


def verify(
    client: GarminClient, evidence: Evidence, expected: GarminBinding | None = None
) -> VerifiedSample:
    comparison = "activity search"
    try:
        page = read_page(client, evidence.day)
        if evidence.activity_id not in page:
            raise ComparisonError("known activity: insufficient evidence")
        if expected is None:
            profile = evidence.profile_id
            if evidence.kind == EvidenceType.WITNESSED:
                profile = integer(page[evidence.activity_id].get("ownerId"), minimum=1, bits=64)
            if profile is None:
                raise ComparisonError("independent profile evidence required")
            expected = GarminBinding(evidence.source, profile)
        check_owners(page, expected)
        comparison = "activity detail"
        result = VerifiedSample(expected, page, detail_for(client, expected, evidence.activity_id))
        for feed in evidence.feeds:
            comparison = feed.value
            result.feeds[feed] = feed_for(client, expected, evidence.day, feed)
        return result
    except ComparisonError:
        raise
    except (MappingError, GarminError):
        raise ComparisonError(f"{comparison}: insufficient evidence") from None

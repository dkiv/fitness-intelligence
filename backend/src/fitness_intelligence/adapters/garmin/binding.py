"""Trusted single-owner evidence, and the five-read B2 comparison."""

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from pathlib import Path
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from fitness_intelligence.adapters.local_account import private_config
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


@dataclass(frozen=True, repr=False)
class Evidence:
    binding: GarminBinding
    activity_id: int
    day: date
    feeds: tuple[Feed, ...]
    durability_confirmed: bool

    @classmethod
    def load(cls, path: Path) -> "Evidence":
        config = private_config(path)
        if config.get("independent_profile_confirmed") is not True:
            raise GarminError("independent profile evidence required")
        feeds = config["feeds"]
        if not isinstance(feeds, list) or len(feeds) != len(set(feeds)):
            raise GarminError("invalid feed selection")
        source = Source(UUID(config["user_id"]), "garmin", UUID(config["source_account_id"]))
        return cls(
            GarminBinding(source, config["profile_id"]),
            integer(config["known_activity_id"], minimum=1, bits=64),
            date.fromisoformat(config["known_day"]),
            tuple(Feed(feed) for feed in feeds),
            config.get("durability_confirmed") is True,
        )

    def account(
        self, session: Session, *, allow_new: bool, for_write: bool = False
    ) -> SourceAccount | None:
        """Resolve the owner and both account keys. Never reactivate or transfer a binding."""
        source = self.binding.source
        if session.scalar(select(User.id).where(User.id == source.owner_id)) is None:
            raise GarminError("local owner unresolved")
        query = (
            select(SourceAccount)
            .where(
                SourceAccount.user_id == source.owner_id,
                or_(
                    SourceAccount.id == source.source_account_id,
                    (SourceAccount.provider == "garmin")
                    & (SourceAccount.provider_account_id == str(self.binding.profile_id)),
                ),
            )
            .execution_options(populate_existing=True)
        )
        if for_write:
            query = query.with_for_update()
        account = session.scalars(query).one_or_none()
        if account is None and allow_new:
            return None
        if (
            account is None
            or GarminBinding.from_account(owner_id=source.owner_id, account=account) != self.binding
        ):
            raise GarminError("local account mismatch or inactive")
        return account


class ComparisonError(GarminError):
    """Contains only the fixed check name and a fixed outcome."""


def compare_profile(binding: GarminBinding, row: Row, key: str, comparison: str) -> None:
    try:
        value = integer(row.get(key), minimum=1, bits=64)
    except MappingError:
        raise ComparisonError(f"{comparison}: insufficient evidence") from None
    if value != binding.profile_id:
        raise ComparisonError(f"{comparison}: mismatch")


def search_page(client: GarminClient, binding: GarminBinding, day: date) -> dict[int, Row]:
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
        compare_profile(binding, row, "ownerId", "activity search owner")
        ident = integer(row.get("activityId"), minimum=1, bits=64)
        if ident in found or stamp(row.get("startTimeLocal"), LIST_STAMP).date() != day:
            raise ComparisonError("activity page: duplicate or wrong date")
        found[ident] = row
    return found


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
    page: dict[int, Row]
    detail: Row
    feeds: dict[Feed, Row] = field(default_factory=dict)


def verify(client: GarminClient, evidence: Evidence) -> VerifiedSample:
    comparison = "activity search"
    try:
        page = search_page(client, evidence.binding, evidence.day)
        if evidence.activity_id not in page:
            raise ComparisonError("known activity: insufficient evidence")
        comparison = "activity detail"
        result = VerifiedSample(page, detail_for(client, evidence.binding, evidence.activity_id))
        for feed in evidence.feeds:
            comparison = feed.value
            result.feeds[feed] = feed_for(client, evidence.binding, evidence.day, feed)
        return result
    except ComparisonError:
        raise
    except (MappingError, GarminError):
        raise ComparisonError(f"{comparison}: insufficient evidence") from None

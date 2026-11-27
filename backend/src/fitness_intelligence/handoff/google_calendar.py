"""Offline G1D rehearsal against an injected Google Calendar API double."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Self
from uuid import UUID, uuid5
from zoneinfo import ZoneInfo

import httpx
from pydantic import AwareDatetime, BaseModel, model_validator

from fitness_intelligence.db.plan_commands import FamiliarPreview, PlanCommands
from fitness_intelligence.db.plan_snapshot import calendar
from fitness_intelligence.planning.planner import Slot

from .prescription import from_revision

AVAILABILITY = "fixture-availability"
DESTINATION = "fixture-reservations"
EVENTS = f"calendars/{DESTINATION}/events"


class BusyInterval(BaseModel):
    start: AwareDatetime
    end: AwareDatetime

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end <= self.start:
            raise ValueError("busy interval ends before or at its start")
        return self


class CalendarBusy(BaseModel):
    busy: list[BusyInterval]
    errors: list[dict[str, Any]] = []


class FreeBusyResult(BaseModel):
    timeMin: AwareDatetime
    timeMax: AwareDatetime
    calendars: dict[str, CalendarBusy]


@dataclass(frozen=True)
class ReservationReceipt:
    calendar_id: str
    event_id: str
    revision: str
    etag: str
    start: datetime
    end: datetime
    zone: str

    @property
    def duration_seconds(self) -> int:
        return int((self.end.astimezone(UTC) - self.start.astimezone(UTC)).total_seconds())


@dataclass(frozen=True)
class _Slot:
    key: str
    start: datetime
    end: datetime
    zone: ZoneInfo
    approved_head: bool


class CalendarRehearsal:
    """Two synthetic calendars. All requests stay inside the injected API double."""

    def __init__(
        self,
        transport: httpx.MockTransport,
        commands: PlanCommands,
        cycle: UUID,
        occurrence: UUID | tuple[int, Slot],
    ) -> None:
        if not isinstance(transport, httpx.MockTransport):
            raise TypeError("calendar rehearsal requires a synthetic transport")
        self.transport = transport
        self.commands = commands
        self.cycle = cycle
        self.occurrence = occurrence

    def _slot(self, revision: UUID) -> _Slot:
        preview = self.commands.preview(self.cycle, revision)
        receipt = preview.decision
        approved = bool(receipt and receipt.choice == "approve" and preview.head_id == revision)
        if isinstance(preview, FamiliarPreview):
            if not isinstance(self.occurrence, UUID):
                raise ValueError("expected a familiar week occurrence UUID")
            source = from_revision(self.commands, self.cycle, revision, self.occurrence)
            return _Slot(
                str(self.occurrence),
                source.session.start_utc,
                source.session.end,
                ZoneInfo(source.zone),
                approved,
            )
        if isinstance(self.occurrence, UUID):
            raise ValueError("expected a week number and a stable plan slot")
        week = preview.candidate.week
        session = calendar(week)[self.occurrence]
        zone = week.inputs.availability.zone
        # The planner accepts only unambiguous local starts. Add elapsed time in UTC.
        start = datetime.combine(session.day, session.start, zone).astimezone(UTC)
        end = start + timedelta(seconds=session.prescription.reserved_seconds)
        number, slot = self.occurrence
        return _Slot(f"{number}/{slot.value}", start, end, zone, approved)

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        with httpx.Client(transport=self.transport, base_url="https://calendar.invalid/v3/") as c:
            return c.request(method, path, **kwargs)

    def conflicts(self, revision: UUID) -> tuple[BusyInterval, ...]:
        """Return overlapping busy intervals only, without requesting event details."""
        return self._conflicts(self._slot(revision))

    def _event_id(self, slot: _Slot) -> str:
        return uuid5(self.cycle, f"google-calendar/{DESTINATION}/{slot.key}").hex

    def _conflicts(self, slot: _Slot) -> tuple[BusyInterval, ...]:
        start, end = slot.start, slot.end
        request = {
            "timeMin": start.isoformat(),
            "timeMax": end.isoformat(),
            "items": [{"id": AVAILABILITY}, {"id": DESTINATION}],
        }
        result = self._request("POST", "freeBusy", json=request).raise_for_status()
        data = FreeBusyResult.model_validate(result.json())
        overlaps: list[BusyInterval] = []
        for name in (AVAILABILITY, DESTINATION):
            calendar = data.calendars.get(name)
            if not calendar or calendar.errors or data.timeMin > start or data.timeMax < end:
                raise ValueError("availability incomplete")
            busy = [b for b in calendar.busy if b.start < end and start < b.end]
            if name == DESTINATION and busy and self._only_own_event(slot):
                continue
            overlaps.extend(busy)
        return tuple(overlaps)

    def _only_own_event(self, slot: _Slot) -> bool:
        # Free/busy merges overlapping intervals. Subtracting our own times could hide a conflict.
        params = {
            "timeMin": slot.start.isoformat(),
            "timeMax": slot.end.isoformat(),
            "singleEvents": "true",
            "fields": "nextPageToken,items(id,transparency)",
        }
        page = self._request("GET", EVENTS, params=params).raise_for_status().json()
        opaque = [e.get("id") for e in page["items"] if e.get("transparency") != "transparent"]
        return not page.get("nextPageToken") and opaque == [self._event_id(slot)]

    def _read(self, event_id: str) -> dict[str, Any] | None:
        result = self._request("GET", f"{EVENTS}/{event_id}")
        if result.status_code == 404:
            return None
        return result.raise_for_status().json()

    @staticmethod
    def _receipt(event: dict[str, Any], expected: dict[str, Any]) -> ReservationReceipt:
        start, end = (datetime.fromisoformat(event[k]["dateTime"]) for k in ("start", "end"))
        for key, instant in (("start", start), ("end", end)):
            if (
                instant.tzinfo is None
                or instant != datetime.fromisoformat(expected[key]["dateTime"])
                or event[key].get("timeZone") != expected[key]["timeZone"]
            ):
                raise ValueError("calendar readback time differs")
        revision = expected["extendedProperties"]["private"]["fiRevision"]
        if (
            event.get("id") != expected["id"]
            or event.get("summary") != expected["summary"]
            or event.get("extendedProperties", {}).get("private", {}).get("fiRevision") != revision
            or event.get("visibility") != expected["visibility"]
            or event.get("reminders", {}).get("useDefault") is not False
            or event.get("reminders", {}).get("overrides")
            or event.get("attendees")
            or event.get("transparency") == "transparent"
            or event.get("status") == "cancelled"
            or not event.get("etag")
        ):
            raise ValueError("calendar readback identity or content differs")
        return ReservationReceipt(
            DESTINATION,
            event["id"],
            revision,
            event["etag"],
            start.astimezone(ZoneInfo(event["start"]["timeZone"])),
            end.astimezone(ZoneInfo(event["end"]["timeZone"])),
            event["start"]["timeZone"],
        )

    def reserve(
        self, revision: UUID, previous: ReservationReceipt | None = None
    ) -> ReservationReceipt:
        """Create, replay, or revise the same synthetic occurrence using its last readback."""
        slot = self._slot(revision)
        if not slot.approved_head:
            raise ValueError("calendar reservation requires the currently approved revision")
        event_id = self._event_id(slot)
        expected = {
            "id": event_id,
            "summary": "FI synthetic workout reservation",
            "visibility": "private",
            "reminders": {"useDefault": False},
            "start": {
                "dateTime": slot.start.astimezone(slot.zone).isoformat(),
                "timeZone": slot.zone.key,
            },
            "end": {
                "dateTime": slot.end.astimezone(slot.zone).isoformat(),
                "timeZone": slot.zone.key,
            },
            "extendedProperties": {"private": {"fiRevision": str(revision)}},
        }
        if previous and (previous.calendar_id, previous.event_id) != (DESTINATION, event_id):
            raise ValueError("previous receipt belongs to a different reservation")
        current = self._read(event_id)
        if current is not None:
            saved_revision = (
                current.get("extendedProperties", {}).get("private", {}).get("fiRevision")
            )
            if saved_revision == str(revision):
                return self._receipt(current, expected)
            if (
                not previous
                or saved_revision != previous.revision
                or current.get("etag") != previous.etag
                or current.get("id") != event_id
                or current.get("status") == "cancelled"
            ):
                raise ValueError("existing event differs from previous receipt")
        elif previous:
            raise ValueError("previously verified event missing")

        if self._conflicts(slot):
            raise ValueError("reservation overlaps busy time")
        if current is None:
            response = self._request("POST", EVENTS, json=expected)
        else:
            properties = current.get("extendedProperties", {})
            changes = {
                "start": expected["start"],
                "end": expected["end"],
                "extendedProperties": properties
                | {"private": properties.get("private", {}) | {"fiRevision": str(revision)}},
            }
            response = self._request(
                "PATCH", f"{EVENTS}/{event_id}", headers={"If-Match": current["etag"]}, json=changes
            )
        response.raise_for_status()
        saved = self._read(event_id)
        if saved is None:
            raise ValueError("written event missing at readback")
        return self._receipt(saved, expected)

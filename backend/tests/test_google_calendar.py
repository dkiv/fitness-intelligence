"""Google-shaped wire requests with synthetic busy intervals and real FI approval commands."""

import json
from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time
from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy.orm import Session

from fitness_intelligence.db.familiar_snapshot import PREVIEW_OWNER
from fitness_intelligence.db.models import User
from fitness_intelligence.db.plan_commands import PlanCommands
from fitness_intelligence.db.plan_snapshot import Generate, Move, PlanningContext
from fitness_intelligence.handoff.google_calendar import CalendarRehearsal
from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning.familiar_examples import example
from fitness_intelligence.planning.planner import Slot
from fitness_intelligence.planning.press_block import RUN, Availability, PressBlock

pytestmark = pytest.mark.postgres


class GoogleDouble:
    def __init__(self) -> None:
        self.events: dict[str, dict[str, Any]] = {}
        self.calls: list[str] = []
        self.busy = [{"start": "2027-01-09T14:05:00Z", "end": "2027-01-09T14:15:00Z"}]
        self.errors: list[dict[str, str]] = []
        self.lose_response = False

    def handle(self, req: httpx.Request) -> httpx.Response:
        assert req.url.host == "calendar.invalid"
        path = req.url.path
        self.calls.append(f"{req.method} {path}")
        body = json.loads(req.content) if req.content else {}
        collection = "/v3/calendars/fixture-reservations/events"
        if path == "/v3/freeBusy" or (path == collection and req.method == "GET"):
            bounds = body if path == "/v3/freeBusy" else req.url.params
            start, end = (datetime.fromisoformat(bounds[k]) for k in ("timeMin", "timeMax"))
            overlapping = [
                event
                for event in self.events.values()
                if datetime.fromisoformat(event["start"]["dateTime"]) < end
                and start < datetime.fromisoformat(event["end"]["dateTime"])
            ]
            if req.method == "GET":
                return httpx.Response(200, json={"items": [{"id": e["id"]} for e in overlapping]})
            assert body["items"] == [{"id": "fixture-availability"}, {"id": "fixture-reservations"}]
            occupied = [
                {"start": e["start"]["dateTime"], "end": e["end"]["dateTime"]} for e in overlapping
            ]
            return httpx.Response(
                200,
                json={
                    "timeMin": body["timeMin"],
                    "timeMax": body["timeMax"],
                    "calendars": {
                        "fixture-availability": {"busy": self.busy, "errors": self.errors},
                        "fixture-reservations": {"busy": occupied},
                    },
                },
            )
        if req.method == "POST":
            assert path == collection
            key = body["id"]
            if key in self.events:
                return httpx.Response(409)
            self.events[key] = body | {"etag": '"1"', "status": "confirmed"}
        else:
            key = path.removeprefix(collection + "/")
            assert path == f"{collection}/{key}"
            if key not in self.events:
                return httpx.Response(404)
            if req.method == "GET":
                return httpx.Response(200, json=self.events[key])
            assert req.method == "PATCH"
            if req.headers["If-Match"] != self.events[key]["etag"]:
                return httpx.Response(412)
            self.events[key].update(body, etag='"2"')
        if self.lose_response:
            raise httpx.ReadTimeout("synthetic lost acknowledgement")
        # Never return the event times on a write. Verification must issue an independent GET.
        return httpx.Response(200, json={"id": key})


def test_conflict_approval_move_and_readback(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    owner = User()
    db.add(owner)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(owner.id))
    monkeypatch.setattr(PlanCommands, "_now", lambda _: datetime(2027, 1, 2, tzinfo=UTC))
    cmd = PlanCommands(db)
    availability = Availability()
    context = cmd.capture_context(PlanningContext(availability), expected_context=None)
    plan = cmd.create_cycle(PressBlock())
    provider = GoogleDouble()
    rehearsal = CalendarRehearsal(
        httpx.MockTransport(provider.handle), cmd, plan, (1, Slot.LONG_RUN)
    )

    blocked = cmd.submit(plan, None, Generate(1))
    (conflict,) = rehearsal.conflicts(blocked)
    assert conflict.start.isoformat() == "2027-01-09T14:05:00+00:00"
    with pytest.raises(ValueError, match="currently approved"):
        rehearsal.reserve(blocked)
    assert not provider.events and provider.calls == ["POST /v3/freeBusy"]

    # Review a different window on the same local day. The busy fixture stays in place.
    saturday = date(2027, 1, 9)
    later = replace(availability, overrides=((saturday, replace(RUN, start=time(10))),))
    cmd.capture_context(PlanningContext(later), expected_context=context)
    first = cmd.submit(plan, None, Generate(1))
    assert rehearsal.conflicts(first) == ()
    cmd.decide(plan, first, expected_head=None, choice="approve", command_id=uuid4())

    db.commit()
    provider.errors = [{"reason": "notFound"}]
    with pytest.raises(ValueError, match="availability incomplete"):
        rehearsal.reserve(first)
    provider.errors.clear()
    provider.busy.append({"start": "2027-01-09T15:00:00Z", "end": "2027-01-09T15:01:00Z"})
    with pytest.raises(ValueError, match="overlaps busy"):
        rehearsal.reserve(first)
    provider.busy.pop()
    assert not provider.events

    # The remote side commits, then drops the acknowledgement. Resolve using the same ID.
    provider.lose_response = True
    with pytest.raises(httpx.ReadTimeout):
        rehearsal.reserve(first)
    provider.lose_response = False
    created = rehearsal.reserve(first)
    assert created.start.isoformat() == "2027-01-09T10:00:00-05:00"
    assert created.zone == "America/Toronto"
    assert (
        created.duration_seconds
        == cmd.preview(plan, first)
        .candidate.week.session(Slot.LONG_RUN)
        .prescription.reserved_seconds
    )
    assert created.revision == str(first)
    assert list(provider.events) == [created.event_id]

    assert provider.events[created.event_id]["visibility"] == "private"
    assert provider.events[created.event_id]["reminders"] == {"useDefault": False}
    assert rehearsal.conflicts(first) == ()  # Our event occupies this slot.
    provider.events["external"] = provider.events[created.event_id] | {"id": "external"}
    assert rehearsal.conflicts(first)  # Another event in exactly the same slot is still visible.
    del provider.events["external"]

    moved = cmd.submit(plan, first, Move(Slot.LONG_RUN, date(2027, 1, 10), time(9)))
    with pytest.raises(ValueError, match="currently approved"):
        rehearsal.reserve(moved, created)
    cmd.decide(plan, moved, expected_head=first, choice="approve", command_id=uuid4())
    db.commit()
    with pytest.raises(ValueError, match="currently approved"):
        rehearsal.reserve(first, created)
    event = provider.events[created.event_id]
    event["etag"] = '"external"'
    with pytest.raises(ValueError, match="previous receipt"):
        rehearsal.reserve(moved, created)
    event["etag"] = created.etag
    provider.lose_response = True
    with pytest.raises(httpx.ReadTimeout):
        rehearsal.reserve(moved, created)
    provider.lose_response = False
    updated = rehearsal.reserve(moved, created)
    assert updated.event_id == created.event_id and updated.calendar_id == created.calendar_id
    assert updated.start.isoformat() == "2027-01-10T09:00:00-05:00"
    assert updated.end.date() == updated.start.date()
    assert updated.zone == created.zone and updated.duration_seconds == created.duration_seconds
    assert updated.revision == str(moved) and updated.etag != created.etag
    assert rehearsal.reserve(moved, created) == updated
    assert list(provider.events) == [created.event_id]
    path = "/v3/calendars/fixture-reservations/events"
    assert provider.calls.count(f"POST {path}") == 1
    assert provider.calls.count(f"PATCH {path}/{created.event_id}") == 1
    assert provider.calls[-2:] == [f"GET {path}/{created.event_id}"] * 2
    event["start"]["timeZone"] = "America/New_York"  # Same offset, different zone.
    with pytest.raises(ValueError, match="readback time"):
        rehearsal.reserve(moved, updated)
    del provider.events[created.event_id]
    with pytest.raises(ValueError, match="verified event missing"):
        rehearsal.reserve(moved, updated)


def test_sealed_g1b_occurrence_includes_preparation(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    db.add(User(id=PREVIEW_OWNER))
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(PREVIEW_OWNER))
    monkeypatch.setattr(PlanCommands, "_now", lambda _: datetime(2027, 1, 2, tzinfo=UTC))
    cmd = PlanCommands(db)
    block, ctx = example("balanced")
    cmd.capture_context(ctx, expected_context=None)
    plan = cmd.create_cycle(block)
    base = cmd.submit(plan, None, f.ProposeBlock())
    cmd.decide(plan, base, expected_head=None, choice="approve", command_id=uuid4())
    week = cmd.submit(plan, base, f.FamiliarWeek(number=1))
    run = next(
        s
        for d in cmd.preview(plan, week).candidate.days
        for s in d.sessions
        if s.template == "cruise"
    )
    provider = GoogleDouble()
    rehearsal = CalendarRehearsal(httpx.MockTransport(provider.handle), cmd, plan, run.occurrence)
    assert rehearsal.conflicts(week) == ()
    cmd.decide(plan, week, expected_head=base, choice="approve", command_id=uuid4())
    db.commit()
    receipt = rehearsal.reserve(week)
    assert receipt.start.isoformat() == "2027-01-06T18:00:00-05:00"
    assert receipt.end.isoformat() == "2027-01-06T18:34:00-05:00"
    assert receipt.duration_seconds == 2040 and receipt.zone == "America/Toronto"
    assert receipt.event_id != run.occurrence.hex


@dataclass(frozen=True)
class ProposedReservation:
    commands: PlanCommands
    plan: UUID
    first: UUID
    calendar: CalendarRehearsal
    provider: GoogleDouble


@pytest.fixture
def proposed(db: Session, monkeypatch: pytest.MonkeyPatch) -> ProposedReservation:
    owner = User()
    db.add(owner)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(owner.id))
    monkeypatch.setattr(PlanCommands, "_now", lambda _: datetime(2027, 1, 2, tzinfo=UTC))
    commands = PlanCommands(db)
    commands.capture_context(PlanningContext(Availability()), expected_context=None)
    plan = commands.create_cycle(PressBlock())
    first = commands.submit(plan, None, Generate(1))
    db.commit()
    provider = GoogleDouble()
    provider.busy.clear()
    calendar = CalendarRehearsal(
        httpx.MockTransport(provider.handle), commands, plan, (1, Slot.LONG_RUN)
    )
    return ProposedReservation(commands, plan, first, calendar, provider)


def test_initial_approval_must_commit(db: Session, proposed: ProposedReservation) -> None:
    p = proposed
    p.commands.decide(p.plan, p.first, expected_head=None, choice="approve", command_id=uuid4())
    with pytest.raises(ValueError, match="committed"):
        p.calendar.reserve(p.first)
    db.rollback()
    assert p.commands.current(p.plan) is None
    assert p.provider.calls == [] and p.provider.events == {}

    p.commands.decide(p.plan, p.first, expected_head=None, choice="approve", command_id=uuid4())
    db.commit()
    created = p.calendar.reserve(p.first)
    assert list(p.provider.events) == [created.event_id]
    assert p.provider.calls.count("POST /v3/calendars/fixture-reservations/events") == 1


def test_move_approval_must_commit(db: Session, proposed: ProposedReservation) -> None:
    p = proposed
    p.commands.decide(p.plan, p.first, expected_head=None, choice="approve", command_id=uuid4())
    db.commit()
    created = p.calendar.reserve(p.first)
    original = deepcopy(p.provider.events)
    moved = p.commands.submit(p.plan, p.first, Move(Slot.LONG_RUN, date(2027, 1, 10), time(9)))
    db.commit()
    p.commands.decide(p.plan, moved, expected_head=p.first, choice="approve", command_id=uuid4())
    before = list(p.provider.calls)
    with pytest.raises(ValueError, match="committed"):
        p.calendar.reserve(moved, created)
    db.rollback()
    assert p.commands.current(p.plan).revision_id == p.first
    assert p.provider.calls == before and p.provider.events == original

    p.commands.decide(p.plan, moved, expected_head=p.first, choice="approve", command_id=uuid4())
    db.commit()
    updated = p.calendar.reserve(moved, created)
    assert updated.event_id == created.event_id and updated.start.date() == date(2027, 1, 10)
    assert list(p.provider.events) == [created.event_id]
    collection = "/v3/calendars/fixture-reservations/events"
    assert p.provider.calls.count(f"POST {collection}") == 1
    assert p.provider.calls.count(f"PATCH {collection}/{created.event_id}") == 1


def test_same_revision_replay_requires_verified_etag(
    db: Session, proposed: ProposedReservation
) -> None:
    p = proposed
    p.commands.decide(p.plan, p.first, expected_head=None, choice="approve", command_id=uuid4())
    db.commit()
    created = p.calendar.reserve(p.first)
    assert p.calendar.reserve(p.first, created) == created
    event = p.provider.events[created.event_id]
    event.update(location="Synthetic track", etag='"external"')
    assert event["extendedProperties"]["private"]["fiRevision"] == created.revision
    with pytest.raises(ValueError, match="ETag"):
        p.calendar.reserve(p.first, created)

    moved = p.commands.submit(p.plan, p.first, Move(Slot.LONG_RUN, date(2027, 1, 10), time(9)))
    p.commands.decide(p.plan, moved, expected_head=p.first, choice="approve", command_id=uuid4())
    db.commit()
    with pytest.raises(ValueError, match="previous receipt"):
        p.calendar.reserve(moved, created)
    assert list(p.provider.events) == [created.event_id]
    assert event["location"] == "Synthetic track" and event["etag"] == '"external"'
    assert p.provider.calls.count("POST /v3/calendars/fixture-reservations/events") == 1
    assert not any(call.startswith("PATCH ") for call in p.provider.calls)

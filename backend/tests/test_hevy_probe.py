from copy import deepcopy
from datetime import UTC, datetime

import httpx
import pytest
from test_hevy_mapping import snapshot

from fitness_intelligence.adapters.hevy.client import HevyClient, HevyError
from fitness_intelligence.adapters.hevy.probe import observe_feed, rehearse
from fitness_intelligence.adapters.hevy.schemas import HevyWorkout


def test_lifecycle(capsys: pytest.CaptureFixture[str]) -> None:
    fixture = snapshot()
    fixture["title"] = "Contract A"
    a = fixture["exercises"][0]
    b = deepcopy(a)
    a["sets"] += [deepcopy(a["sets"][0])]
    for i, reps in enumerate([3, 7]):
        a["sets"][i].update(index=i, reps=reps)
    b.update(index=8, exercise_template_id="T2")
    b["sets"][0]["reps"] = 5
    fixture["exercises"].append(b)
    events: list[dict] = []
    stage = 0
    window: str | None = None
    requests = 0

    def pause(_: str) -> str:
        nonlocal stage
        stage += 1
        now = datetime.now(UTC).isoformat()
        if stage == 2:
            fixture["title"] = "Contract B"
            b["index"] = 0
            a["sets"][0]["index"] = 2
        if stage == 3:
            events.insert(0, dict(type="deleted", id=fixture["id"], deleted_at=now))
        else:
            fixture["updated_at"] = now
            events.insert(0, dict(type="updated", workout=deepcopy(fixture)))
        return ""

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal requests, window
        requests += 1
        assert req.method == "GET"
        path = req.url.path
        if path == "/v1/user/info":
            body = {"data": {"id": "test"}}
        elif path == "/v1/workouts":
            items = [fixture] if stage in (1, 2) else []
            body = dict(page=1, page_count=len(items), workouts=items)
        elif path == "/v1/workouts/events":
            assert req.url.params["pageSize"] == "1"
            since = req.url.params["since"]
            if window is None:
                window = since
            assert since in (window, events[0].get("deleted_at") or fixture["updated_at"])
            eligible = [
                e for e in events if (e.get("deleted_at") or e["workout"]["updated_at"]) >= since
            ]
            page = int(req.url.params["page"])
            body = dict(page=page, page_count=len(eligible), events=eligible[page - 1 : page])
        else:
            assert path == "/v1/workouts/synthetic-workout"
            body = fixture
        return httpx.Response(200, json=body)

    client = HevyClient("test", max_pages=4, transport=httpx.MockTransport(handler))
    try:
        rehearse(client, "test", pause)
    finally:
        client.close()
    out = capsys.readouterr().out
    assert requests == 16
    assert out.count("same_event_at_exact_since=True") == 3
    assert "reorder_visible=True" in out and "same_workout_id=True" in out
    assert "pages=3 updates=2 deletions=1 matching_events=1" in out
    assert "workout_list_empty=True" in out
    assert "Private text" not in out and "synthetic-workout" not in out


@pytest.mark.parametrize("matched", [True, False])
def test_refuses_before_prompt(matched: bool) -> None:
    paths = []

    def handler(req: httpx.Request) -> httpx.Response:
        paths.append(req.url.path)
        if len(paths) == 1:
            return httpx.Response(200, json={"data": {"id": "expected" if matched else "other"}})
        return httpx.Response(200, json=dict(page=1, page_count=1, workouts=[snapshot()]))

    client = HevyClient("test", max_pages=4, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(HevyError, match="empty" if matched else "mismatch"):
            rehearse(client, "expected", lambda _: pytest.fail("unexpected prompt"))
    finally:
        client.close()
    assert len(paths) == (2 if matched else 1)


@pytest.mark.parametrize("missing_time", [True, False])
def test_missing_tombstone_time_and_exclusive_boundary(
    missing_time: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    target = HevyWorkout.model_validate(snapshot())
    since = datetime(2026, 1, 1, tzinfo=UTC)
    calls = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        since_arg = datetime.fromisoformat(req.url.params["since"])
        events = []
        if since_arg == since:
            events.append(
                dict(
                    type="deleted",
                    id=target.id,
                    deleted_at=None if missing_time else target.updated_at,
                )
            )
        else:
            assert since_arg == datetime.fromisoformat(target.updated_at)
        return httpx.Response(200, json=dict(page=1, page_count=len(events), events=events))

    client = HevyClient("test", max_pages=4, transport=httpx.MockTransport(handler))
    try:
        observe_feed(client, since, target, deleted=True)
    finally:
        client.close()
    out = capsys.readouterr().out
    assert calls == (1 if missing_time else 2)
    if missing_time:
        assert "missing_times=1" in out and "No matching timestamped event" in out
    else:
        assert "same_event_at_exact_since=False" in out

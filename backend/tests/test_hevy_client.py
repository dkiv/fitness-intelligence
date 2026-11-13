import json
from datetime import UTC, datetime

import httpx
import pytest
from test_hevy_mapping import snapshot

from fitness_intelligence.adapters.hevy.client import HevyClient, HevyError


def test_pages_and_fixed_since() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        page = int(request.url.params["page"])
        return httpx.Response(
            200,
            json=dict(page=page, page_count=2, events=[dict(type="updated", workout=snapshot())]),
        )

    client = HevyClient("synthetic", transport=httpx.MockTransport(handler))
    assert len(list(client.events(datetime(2026, 1, 1, tzinfo=UTC)))) == 2
    assert [r.url.params["page"] for r in requests] == ["1", "2"]
    assert len({r.url.params["since"] for r in requests}) == 1
    assert all(r.method == "GET" and r.headers["api-key"] == "synthetic" for r in requests)
    client.close()


@pytest.mark.parametrize("status", [429, 500, 503, "timeout"])
def test_bounded_retries(status: int | str) -> None:
    calls, delays = [], []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if status == "timeout":
            raise httpx.ReadTimeout("SECRET", request=request)
        return httpx.Response(status, headers={"Retry-After": "2"}, text="SECRET")

    client = HevyClient("synthetic", transport=httpx.MockTransport(handler), sleep=delays.append)
    with pytest.raises(HevyError) as error:
        client.identity()
    assert "SECRET" not in str(error.value)
    assert len(calls) == 4 and len(delays) == 3
    client.close()


@pytest.mark.parametrize("status", [301, 401, 403, 404])
def test_permanent_errors_never_retry(status: int) -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(status, text="SECRET")

    client = HevyClient("synthetic", transport=httpx.MockTransport(handler))
    with pytest.raises(HevyError):
        client.identity()
    assert len(calls) == 1
    client.close()


@pytest.mark.parametrize(
    "data",
    [
        dict(page=2, page_count=2, workouts=[]),
        dict(page=1, page_count=0, workouts=[snapshot()]),
        dict(page=1, page_count=20000, workouts=[]),
        dict(page=1, page_count=2, workouts=[]),
    ],
)
def test_invalid_pages(data: dict) -> None:
    client = HevyClient(
        "synthetic", transport=httpx.MockTransport(lambda _: httpx.Response(200, json=data))
    )
    with pytest.raises(HevyError):
        list(client.workouts())
    client.close()


def test_empty_identity_and_detail_validation() -> None:
    responses = iter(
        [dict(data=dict(id="account")), dict(page=1, page_count=0, workouts=[]), snapshot()]
    )
    client = HevyClient(
        "synthetic",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, content=json.dumps(next(responses)))
        ),
    )
    assert client.identity() == "account"
    assert list(client.workouts()) == []
    assert client.workout("synthetic-workout").id == "synthetic-workout"
    client.close()


def test_retry_recovers_and_timeout_configuration() -> None:
    calls, delays = [], []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.extensions["timeout"] == dict(connect=5, read=20, write=20, pool=5)
        if len(calls) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"data": {"id": "account"}})

    client = HevyClient("synthetic", transport=httpx.MockTransport(handler), sleep=delays.append)
    assert client.identity() == "account" and delays == [0]
    client.close()


@pytest.mark.parametrize("retry", ["9999", "-2", "nan", "inf"])
def test_retry_after_outside_budget(retry: str) -> None:
    client = HevyClient(
        "synthetic",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(429, headers={"Retry-After": retry})
        ),
    )
    with pytest.raises(HevyError, match="budget"):
        client.identity()
    client.close()


def test_changing_pages_and_size_limit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params["page"])
        return httpx.Response(200, json=dict(page=page, page_count=3 - page, workouts=[snapshot()]))

    client = HevyClient("synthetic", transport=httpx.MockTransport(handler))
    with pytest.raises(HevyError):
        list(client.workouts())
    client.close()
    client = HevyClient(
        "synthetic",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b"x" * 4_000_001)),
    )
    with pytest.raises(HevyError, match="size"):
        client.identity()
    client.close()


@pytest.mark.parametrize(
    ("identity", "items", "outcome"),
    [
        ("other", [], "mismatch"),
        ("bound", [], False),
        ("bound", [snapshot()], True),
        ("bound", [snapshot(), snapshot()], "pagination"),
        ("bound", [{"title": "private synthetic text"}], "pagination"),
    ],
)
def test_verification_request_scope(identity: str, items: list[dict], outcome: str | bool) -> None:
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        assert request.method == "GET"
        if len(paths) == 1:
            return httpx.Response(200, json={"data": {"id": identity}})
        assert dict(request.url.params) == {"page": "1", "pageSize": "1"}
        return httpx.Response(200, json=dict(page=1, page_count=3 if items else 0, workouts=items))

    client = HevyClient("synthetic", transport=httpx.MockTransport(handler))
    try:
        if isinstance(outcome, str):
            with pytest.raises(HevyError, match=outcome):
                client.verify_sample("bound")
        else:
            assert client.verify_sample("bound") is outcome
    finally:
        client.close()
    assert paths == ["/v1/user/info"] + (["/v1/workouts"] if identity == "bound" else [])

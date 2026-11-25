import base64
import json
import subprocess
import sys
from collections.abc import Callable, Iterator
from datetime import date

import httpx
import pytest

from fitness_intelligence.adapters.garmin import verify
from fitness_intelligence.adapters.garmin.client import (
    TOKEN_PATH,
    Endpoint,
    GarminClient,
    GarminError,
)
from fitness_intelligence.adapters.garmin.probe import Probe

KEY = "synthetic-only-key"
PRIVATE = "synthetic-private-marker"
RECENT = date(2025, 5, 10)
OLDER = date(2024, 5, 10)


def jwt(exp: int) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


@pytest.fixture
def make_client() -> Iterator[Callable[..., GarminClient]]:
    clients = []

    def create(
        handler: Callable[[httpx.Request], httpx.Response], clock: Callable[[], float] = lambda: 100
    ) -> GarminClient:
        client = GarminClient(KEY, transport=httpx.MockTransport(handler), clock=clock)
        clients.append(client)
        return client

    yield create
    for client in clients:
        client.close()


@pytest.mark.parametrize("success_status", [200, 201])
def test_token_exchange_reuse_expiry_and_401(
    make_client: Callable[..., GarminClient], success_status: int
) -> None:
    now = [100]
    tokens: list[str] = []
    reads = []

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.host == "personal.connectapi.garmin.com" and req.url.scheme == "https"
        if req.url.path == TOKEN_PATH:
            assert req.method == "POST" and req.content == b""
            assert req.headers["authorization"] == f"ApiKey {KEY}"
            assert req.headers["accept"] == "*/*"
            tokens.append(jwt(now[0] + 100 + len(tokens)))
            return httpx.Response(success_status, text=tokens[-1])
        assert req.method == "GET" and req.headers["authorization"] == "Bearer " + tokens[-1]
        reads.append(req.url.path)
        return httpx.Response(401 if len(reads) == 4 else 200, json=[])

    client = make_client(handler, lambda: now[0])
    client.read(Endpoint.TYPES)
    client.read(Endpoint.TYPES)
    assert len(tokens) == 1
    now[0] += 101
    client.read(Endpoint.TYPES)
    client.read(Endpoint.TYPES)
    assert len(tokens) == 3 and len(reads) == 5


@pytest.mark.parametrize(
    ("code", "content", "expected"),
    [
        (401, PRIVATE, "token_exchange_failed"),
        (403, PRIVATE, "token_exchange_failed"),
        (503, PRIVATE, "token_exchange_failed"),
        (204, "", "invalid_token_response"),
        (429, PRIVATE, "rate_limited"),
        (200, jwt(90), "invalid_token_response"),
        (200, '{"access_token":"private"}', "invalid_token_response"),
        (200, "a.ew.b", "invalid_token_response"),
        (200, "x" * 17000, "invalid_token_response"),
    ],
)
def test_exchange_errors(
    make_client: Callable[..., GarminClient], code: int, content: str, expected: str
) -> None:
    client = make_client(lambda _: httpx.Response(code, text=content))
    report = Probe(client).run(RECENT, OLDER)
    assert report["requests"] == 1
    if code != 200:
        assert report["token_http_status"] == code
    assert report["current"]["types"]["status"] == expected
    assert PRIVATE not in json.dumps(report) and KEY not in json.dumps(report)


@pytest.mark.parametrize(
    ("response", "expected", "requests"),
    [
        (httpx.Response(401, text=PRIVATE), "unauthorized", 4),
        (httpx.Response(403, text=PRIVATE), "forbidden", 2),
        (
            httpx.Response(302, headers={"location": "https://example.org/private"}),
            "http_error_302",
            2,
        ),
        (httpx.Response(200, text=PRIVATE), "invalid_json", 2),
        (httpx.Response(200, json=None), "invalid_json", 2),
        (httpx.Response(200, text="[]" + " " * 2_000_000), "response_too_large", 2),
    ],
)
def test_data_errors(
    make_client: Callable[..., GarminClient], response: httpx.Response, expected: str, requests: int
) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=jwt(200)) if req.method == "POST" else response

    client = make_client(handler)
    with pytest.raises(GarminError) as err:
        client.read(Endpoint.TYPES)
    assert str(err.value) == expected
    assert client.requests == requests


class UnreadArchive(httpx.SyncByteStream):
    def __iter__(self) -> Iterator[bytes]:
        raise AssertionError("archive stream must close unread")


def test_two_window_probe_and_privacy(make_client: Callable[..., GarminClient]) -> None:
    offsets = []
    details = []

    def handler(req: httpx.Request) -> httpx.Response:
        p, q = req.url.path, req.url.params
        if p == TOKEN_PATH:
            return httpx.Response(200, text=jwt(200))
        if p == Endpoint.ACTIVITIES:
            day = date.fromisoformat(q["endDate"])
            assert (day - date.fromisoformat(q["startDate"])).days == 6
            offsets.append((day, int(q["start"])))
            assert q["limit"] == "3"
            rows = [
                {
                    "activityId": 998761 + i,
                    "startTimeLocal": str(day) + " 05:00:00",
                    "activityName": PRIVATE,
                    "startLatitude": 84.98765,
                    "activityType": {"typeKey": sport},
                }
                for i, sport in enumerate(("squash", "running", "ultimate_disc"))
            ]
            return httpx.Response(200, json=rows if q["start"] == "0" else [])
        if p.startswith("/download-service/"):
            return httpx.Response(
                200,
                headers={"content-type": "application/x-zip-compressed"},
                stream=UnreadArchive(),
            )
        if p.endswith("/workouts"):
            return httpx.Response(200, json=[{"steps": [{"workoutName": PRIVATE}]}])
        if p == Endpoint.TYPES:
            return httpx.Response(200, json=[{"key": "squash", "parent": "racket_sports"}])
        if p.startswith("/activity-service/"):
            details.append(p)
            return httpx.Response(
                200,
                json={
                    "activityId": 998762,
                    "metadataDTO": {"fileFormat": {"formatKey": "fit"}},
                    "summaryDTO": {"averageSpeed": 3.89765},
                },
            )
        if p.startswith("/nutrition-service/"):
            assert q["includeGoals"] == q["includeMedia"] == "false"
            return httpx.Response(
                200,
                json={
                    "mealDate": p.split("/")[-1],
                    "dailyNutritionContent": {"calories": 1897, "protein": 0, "carbs": None},
                    "mealDetails": [
                        {
                            "loggedFoods": [
                                {"logSource": "MyFitnessPal", "foodMetaData": {"source": PRIVATE}}
                            ]
                        }
                    ],
                },
            )
        if p.startswith("/weight-service/"):
            return httpx.Response(
                200,
                json=[
                    {
                        "weight": 72.45678,
                        "calendarDate": p.split("/")[-1],
                        "sourceName": "RENPHO",
                        "serialNumber": PRIVATE,
                    }
                ],
            )
        if p.startswith("/hrv-service/"):
            return httpx.Response(204)
        if p == Endpoint.ZONES:
            assert q["generateDefaults"] == "false"
        return httpx.Response(200, json=[] if p in (Endpoint.ZONES, Endpoint.BATTERY) else {})

    client = make_client(handler)
    report = Probe(client).run(RECENT, OLDER)
    assert report["status"] == "complete"
    assert offsets == [(RECENT, 0), (RECENT, 3), (OLDER, 0), (OLDER, 3)]
    assert details == ["/activity-service/activity/998762"] * 2
    assert report["requests"] == 27
    for sample in (report["recent"], report["older"]):
        assert sample["hrv"] == {"status": "no_content"}
        assert sample["sleep"]["records"] == 0
        assert sample["original"]["status"] == "archive_headers_received"
        assert (
            sample["detail"]["fit_format_declared"]
            and sample["detail"]["pace_derivable_from_speed"]
        )
        assert all(sample["activity_pages"][0]["activities"]["sport_keys_in_sample"].values())
        fields = sample["food"]["fields"]
        assert fields["dailyNutritionContent.calories"] == {"present": 1}
        assert fields["dailyNutritionContent.protein"] == {"zero": 1}
        assert fields["dailyNutritionContent.carbs"] == {"null": 1}
        assert fields["dailyNutritionContent.fat"] == {"missing": 1}
        assert sample["food"]["myfitnesspal_markers"]["mealDetails.loggedFoods.logSource"] == 1
        assert sample["weight"]["record_dates"] == {"matched": 1}
        assert sample["weight"]["undocumented_source_fields"]["sourceName"]["renpho_marker"] == 1
    serialized = json.dumps(report)
    for forbidden in (
        KEY,
        PRIVATE,
        jwt(200),
        "998762",
        "84.98765",
        "1897",
        "72.45678",
        "3.89765",
        str(RECENT),
        str(OLDER),
    ):
        assert forbidden not in serialized


@pytest.mark.parametrize("mode", ["over_limit", "duplicate", "wrong_date", "bad_id"])
def test_invalid_pagination(make_client: Callable[..., GarminClient], mode: str) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "POST":
            return httpx.Response(200, text=jwt(200))
        assert req.url.path == Endpoint.ACTIVITIES
        rows = [
            {
                "activityId": PRIVATE if mode == "bad_id" else i + 1,
                "startTimeLocal": str(OLDER if mode == "wrong_date" else RECENT),
            }
            for i in range(4 if mode == "over_limit" else 3)
        ]
        return httpx.Response(200, json=rows)

    client = make_client(handler)
    probe, out = Probe(client), {}
    probe.activities(out, RECENT)
    assert probe.partial
    assert out["activity_pages"][-1]["activities"] == {"status": "invalid_activity_page"}
    assert "detail" not in out
    assert client.requests == (3 if mode == "duplicate" else 2)


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ({"unknownPrivateKey": PRIVATE}, "unrecognized_fields"),
        ({"weight": 45}, "unexpected_schema"),
        ([{"weight": True}], "unexpected_field_type"),
        ([{"weight": 2.5, "calendarDate": str(OLDER)}], "date_mismatch"),
    ],
)
def test_weight_schema_drift(
    make_client: Callable[..., GarminClient], body: object, expected: str
) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return (
            httpx.Response(200, text=jwt(200))
            if req.method == "POST"
            else httpx.Response(200, json=body)
        )

    endpoint = Endpoint.DAILY if expected == "unrecognized_fields" else Endpoint.WEIGHT
    probe, out = Probe(make_client(handler)), {}
    probe.sample(out, endpoint, day=str(RECENT))
    assert probe.partial and out[endpoint.name.lower()]["status"] == expected
    assert PRIVATE not in json.dumps(out)


def test_rate_limit_stops_entire_run(make_client: Callable[..., GarminClient]) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=jwt(200)) if req.method == "POST" else httpx.Response(429)

    report = Probe(make_client(handler)).run(RECENT, OLDER)
    assert report["stopped"] == "rate_limited" and report["requests"] == 2


def test_cli_keychain_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, PRIVATE, output=KEY, stderr=PRIVATE)

    monkeypatch.setattr(verify.subprocess, "run", fail)
    monkeypatch.setattr(sys, "argv", ["probe"])
    assert verify.main() == 1
    output = capsys.readouterr()
    assert json.loads(output.out) == {"status": "partial", "stopped": "keychain_unavailable"}
    assert output.err == ""


def test_series_uses_descriptor_index(make_client: Callable[..., GarminClient]) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "POST":
            return httpx.Response(200, text=jwt(200))
        return httpx.Response(
            200,
            json={
                "calendarDate": {"date": str(RECENT) + "T00:00:00Z"},
                "heartRateValueDescriptors": [{"key": "heartrate", "index": 2}],
                "heartRateValues": [[1, 9, None], [2, 9, 0], [3, 9, 75], [4, 9]],
            },
        )

    out = {}
    Probe(make_client(handler)).sample(out, Endpoint.HEART, params={"date": str(RECENT)})
    assert out["heart"]["record_dates"] == {"matched": 1}
    assert out["heart"]["reading_states"] == {"null": 1, "zero": 1, "present": 1, "invalid": 1}

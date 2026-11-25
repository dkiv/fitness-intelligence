"""Bounded, in-memory transport for Garmin's global Personal API."""

import base64
import json
import re
import time
from collections import Counter
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any

import httpx

TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
MAX_JSON_BYTES = 2_000_000


class Endpoint(StrEnum):
    TYPES = "/activity-service/activity/activityTypes/simple"
    ZONES = "/biometric-service/heartRateZones/v2"
    ACTIVITIES = "/activitylist-service/activities/search/activities"
    DETAIL = "/activity-service/activity/{activity_id}"
    WORKOUTS = "/activity-service/activity/{activity_id}/workouts"
    ORIGINAL = "/download-service/files/activity/{activity_id}"
    DAILY = "/usersummary-service/usersummary/daily"
    HEART = "/wellness-service/wellness/dailyHeartRate"
    HRV = "/hrv-service/hrv/{day}"
    SLEEP = "/sleep-service/sleep/dailySleep"
    BATTERY = "/wellness-service/wellness/bodyBattery/reports/daily"
    DAILY_RANGE = "/usersummary-service/v2/dailysummaries"
    SLEEP_RANGE = "/sleep-service/sleep/dailySleepSummariesByDate"
    HRV_RANGE = "/hrv-service/hrv/daily/{day}/{end_day}"
    WEIGHT_RANGE = "/weight-service/weight/all/{day}/{end_day}"
    FOOD = "/nutrition-service/food/logs/{day}"
    WEIGHT = "/weight-service/weight/all/{day}/{day}"


class GarminError(Exception):
    """Only fixed diagnostic categories may cross the adapter boundary."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    row = dict(pairs)
    if len(row) != len(pairs):
        raise ValueError("duplicate key")
    return row


def invalid_constant(_: str) -> None:
    raise ValueError("invalid number")


class TokenExchangeError(GarminError):
    def __init__(self, category: str, http_status: int) -> None:
        super().__init__(category)
        self.http_status = http_status


@dataclass
class Reply:
    status: int
    body: bytes = field(repr=False)


class GarminClient:
    def __init__(
        self,
        key: str,
        *,
        transport: httpx.BaseTransport | None = None,
        request_limit: int = 40,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if not re.fullmatch(r"[!-~]{1,8192}", key):
            raise GarminError("invalid_key")
        self._key = key
        self._token = ""
        self._expires = 0
        self._clock = clock
        self._deadline = time.monotonic() + 180
        self._fixed_token = False
        if not 1 <= request_limit <= 40:
            raise GarminError("invalid request limit")
        self.request_limit = request_limit
        self.attempts: Counter[str] = Counter()
        self.requests = 0
        self._http = httpx.Client(
            base_url="https://personal.connectapi.garmin.com",
            transport=transport,
            trust_env=False,
            follow_redirects=False,
            timeout=httpx.Timeout(10, connect=5),
            headers={"Accept-Encoding": "identity"},
        )

    def close(self) -> None:
        self._key = self._token = ""
        self._http.close()

    def _request(
        self,
        path: str,
        *,
        category: str,
        exchange: bool = False,
        archive: bool = False,
        params: dict[str, str | int] | None = None,
    ) -> Reply:
        if self.requests >= self.request_limit or time.monotonic() >= self._deadline:
            raise GarminError("budget_exhausted")
        self.requests += 1
        self.attempts[category] += 1
        headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}
        if exchange:
            headers = {"Authorization": f"ApiKey {self._key}", "Accept": "*/*"}
        if archive:
            headers["Accept"] = (
                "application/zip, application/x-zip-compressed, application/octet-stream"
            )
        limit = 16_384 if exchange else MAX_JSON_BYTES
        try:
            with self._http.stream(
                "POST" if exchange else "GET", path, params=params, headers=headers
            ) as response:
                success = response.is_success if exchange else response.status_code == 200
                if not success:
                    return Reply(response.status_code, b"")
                if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                    raise GarminError("unsupported_encoding")
                if archive:
                    media = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
                    if media not in (
                        "application/zip",
                        "application/x-zip-compressed",
                        "application/octet-stream",
                    ):
                        raise GarminError("unexpected_archive_type")
                    # Never read the ZIP, its filenames, or its contents.
                    return Reply(200, b"")
                data = bytearray()
                for chunk in response.iter_bytes():
                    if time.monotonic() >= self._deadline:
                        raise GarminError("budget_exhausted")
                    if len(data) + len(chunk) > limit:
                        raise GarminError("response_too_large")
                    data.extend(chunk)
                return Reply(response.status_code, bytes(data))
        except httpx.HTTPError:
            raise GarminError("transport_error") from None

    def _exchange(self) -> None:
        try:
            reply = self._request(TOKEN_PATH, category="exchange", exchange=True)
        except GarminError as exc:
            if str(exc) in {"response_too_large", "unsupported_encoding"}:
                raise GarminError("invalid_token_response") from None
            raise
        if not 200 <= reply.status < 300:
            category = "rate_limited" if reply.status == 429 else "token_exchange_failed"
            raise TokenExchangeError(category, reply.status)
        try:
            token = reply.body.decode("ascii").strip()
            if not re.fullmatch(r"[\w-]+\.[\w-]+\.[\w-]+", token, flags=re.ASCII):
                raise ValueError
            payload = token.split(".")[1]
            exp = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["exp"]
            if type(exp) is not int or exp <= self._clock():
                raise ValueError
        except (UnicodeError, ValueError, TypeError, KeyError, RecursionError):
            raise TokenExchangeError("invalid_token_response", reply.status) from None
        self._token, self._expires = token, exp

    @contextmanager
    def verified_session(self) -> Iterator[None]:
        """Use a single bearer for the pin checks and subsequent account-scoped feeds."""
        if self._expires <= self._clock() + 5:
            self._exchange()
        self._fixed_token = True
        try:
            yield
        finally:
            self._fixed_token = False

    def check_verified_session(self) -> None:
        if not self._fixed_token or self._expires <= self._clock() + 5:
            raise GarminError("verified session expired")
        if time.monotonic() >= self._deadline:
            raise GarminError("budget_exhausted")

    def read(
        self,
        endpoint: Endpoint,
        *,
        day: str = "",
        end_day: str = "",
        activity_id: int = 0,
        params: dict[str, str | int] | None = None,
    ) -> Any:
        if "{day}" in endpoint.value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day, re.ASCII):
            raise GarminError("invalid_date")
        if "{activity_id}" in endpoint.value and (
            type(activity_id) is not int or not 0 < activity_id < 2**63
        ):
            raise GarminError("invalid_activity_id")
        if "{end_day}" in endpoint.value and (
            not re.fullmatch(r"\d{4}-\d{2}-\d{2}", end_day, re.ASCII) or end_day < day
        ):
            raise GarminError("invalid_date")
        path = endpoint.value.format(day=day, end_day=end_day, activity_id=activity_id)
        archive = endpoint is Endpoint.ORIGINAL
        if self._expires <= self._clock() + 5:
            if self._fixed_token:
                raise GarminError("verified session expired")
            self._exchange()
        reply = self._request(path, category=endpoint.name.lower(), archive=archive, params=params)
        if reply.status == 401 and not self._fixed_token:
            self._exchange()
            reply = self._request(
                path, category=endpoint.name.lower(), archive=archive, params=params
            )
        if reply.status != 200:
            raise GarminError(
                {
                    204: "no_content",
                    401: "unauthorized",
                    403: "forbidden",
                    404: "not_found",
                    429: "rate_limited",
                }.get(reply.status, "http_error_" + str(reply.status))
            )
        if archive:
            return None
        try:
            result = json.loads(
                reply.body.decode("utf-8"),
                parse_float=Decimal,
                parse_constant=invalid_constant,
                object_pairs_hook=unique_object,
            )
            if not isinstance(result, (list, dict)):
                raise ValueError
            return result
        except (UnicodeError, ValueError, InvalidOperation, RecursionError):
            raise GarminError("invalid_json") from None

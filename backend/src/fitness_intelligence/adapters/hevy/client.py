"""Read-only Hevy REST transport. Never expose response bodies or request exceptions."""

import random
import time
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import httpx

from .schemas import (
    MAX_RESPONSE_BYTES,
    DeletedEvent,
    EventPage,
    HevyWorkout,
    UpdatedEvent,
    WorkoutPage,
    decode_response,
)


class HevyError(Exception):
    """Sanitized operational error; arguments contain only fixed categories."""


class HevyClient:
    def __init__(
        self,
        api_key: str,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        max_pages: int = 10000,
    ) -> None:
        if not api_key or any(c.isspace() for c in api_key):
            raise HevyError("invalid credential")
        self._http = httpx.Client(
            base_url="https://api.hevyapp.com",
            headers={"api-key": api_key},
            timeout=httpx.Timeout(20, connect=5, pool=5),
            follow_redirects=False,
            transport=transport,
        )
        self._sleep = sleep
        self.max_pages = max_pages

    def close(self) -> None:
        self._http.close()

    def _get(self, path: str, params: dict[str, str | int] | None = None) -> bytes:
        deadline = time.monotonic() + 90
        for attempt in range(4):
            delay = min(2**attempt + random.random(), 10)
            try:
                with self._http.stream("GET", path, params=params) as response:
                    status = response.status_code
                    if status == 200:
                        data = bytearray()
                        for chunk in response.iter_bytes():
                            if time.monotonic() > deadline:
                                raise HevyError("request deadline exceeded")
                            data.extend(chunk)
                            if len(data) > MAX_RESPONSE_BYTES:
                                raise HevyError("response size limit")
                        return bytes(data)
                    if status != 429 and not 500 <= status <= 599:
                        raise HevyError(
                            "access denied" if status in (401, 403) else "request rejected"
                        )
                    retry = response.headers.get("Retry-After")
                    if retry:
                        try:
                            delay = float(retry)
                        except ValueError:
                            try:
                                delay = (
                                    parsedate_to_datetime(retry) - datetime.now(UTC)
                                ).total_seconds()
                            except (ValueError, TypeError, OverflowError):
                                delay = min(2**attempt + random.random(), 10)
                        if not 0 <= delay <= 30:
                            raise HevyError("rate limit wait exceeds budget")
            except httpx.TransportError:
                pass
            if attempt == 3 or time.monotonic() + delay >= deadline:
                break
            self._sleep(delay)
        raise HevyError("request retry budget exhausted") from None

    def identity(self) -> str:
        try:
            value = decode_response(self._get("/v1/user/info"))["data"]["id"]
            if not isinstance(value, str) or not 1 <= len(value) <= 1024:
                raise ValueError
            return value
        except (ValueError, KeyError, TypeError):
            raise HevyError("invalid identity response") from None

    def workout(self, external_id: str) -> HevyWorkout:
        if external_id in (".", ".."):
            raise HevyError("unsupported workout identity path")
        try:
            result = HevyWorkout.model_validate_json(
                self._get("/v1/workouts/" + quote(external_id, safe=""))
            )
            if result.id != external_id:
                raise ValueError
            return result
        except ValueError:
            raise HevyError("invalid workout response") from None

    def _pages(self, since: datetime | None) -> Iterator[WorkoutPage | EventPage]:
        expected_count: int | None = None
        for page in range(1, self.max_pages + 1):
            params: dict[str, str | int] = {"page": page, "pageSize": 10}
            if since is not None:
                params["since"] = since.isoformat()
            try:
                model = WorkoutPage if since is None else EventPage
                result = model.model_validate_json(
                    self._get("/v1/workouts" + ("/events" if since is not None else ""), params)
                )
                items = result.workouts if isinstance(result, WorkoutPage) else result.events
                if (
                    result.page != page
                    or result.page_count > self.max_pages
                    or (expected_count is not None and result.page_count != expected_count)
                    or (result.page_count == 0 and (page != 1 or items))
                    or (
                        result.page_count > 0
                        and (page > result.page_count or (not items and page < result.page_count))
                    )
                    or len(items) > 10
                ):
                    raise ValueError
            except ValueError:
                raise HevyError("invalid or changing pagination") from None
            expected_count = result.page_count
            yield result
            if page >= result.page_count:
                return
        raise HevyError("page budget exhausted")

    def workouts(self) -> Iterator[HevyWorkout]:
        for page in self._pages(None):
            assert isinstance(page, WorkoutPage)
            yield from page.workouts

    def events(self, since: datetime) -> Iterator[UpdatedEvent | DeletedEvent]:
        for page in self._pages(since):
            assert isinstance(page, EventPage)
            yield from page.events

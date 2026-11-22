"""Interactive, read-only contract observations for an empty dedicated Hevy account."""

import logging
import os
from collections.abc import Callable
from datetime import UTC, datetime

from .client import HevyClient, HevyError
from .mapping import map_workout
from .schemas import DeletedEvent, HevyWorkout, UpdatedEvent, utc


def observe_feed(
    client: HevyClient, since: datetime, target: HevyWorkout, *, deleted: bool
) -> None:
    pages = list(client.event_pages(since, page_size=1))
    events = [event for page in pages for event in page.events]
    times: list[datetime] = []
    matches = 0
    updates = 0
    deletions = 0
    boundary: datetime | None = None
    mapped = map_workout(target)
    for event in events:
        if isinstance(event, UpdatedEvent):
            if event.workout.id != target.id:
                raise HevyError("unexpected event identity")
            updates += 1
            stamp = utc(event.workout.updated_at)
            if not deleted and map_workout(event.workout).content_hash == mapped.content_hash:
                matches += 1
                boundary = stamp
        else:
            if event.id != target.id:
                raise HevyError("unexpected event identity")
            deletions += 1
            if event.deleted_at is None:
                continue
            stamp = utc(event.deleted_at)
            if deleted:
                matches += 1
                boundary = stamp if boundary is None else max(boundary, stamp)
        times.append(stamp)
    print(f"pages={len(pages)} updates={updates} deletions={deletions} matching_events={matches}")
    print(
        f"missing_times={len(events) - len(times)} newest_first_for_timed_events="
        f"{times == sorted(times, reverse=True)}"
    )
    if boundary is None:
        print("No matching timestamped event for the boundary check.")
        return
    print(
        f"event_has_subseconds={bool(boundary.microsecond)} "
        f"event_at_or_after_edit={boundary >= utc(target.updated_at)}"
    )
    for page in client.event_pages(boundary, page_size=1):
        for entry in page.events:
            if isinstance(entry, DeletedEvent):
                equal = (
                    deleted
                    and entry.id == target.id
                    and entry.deleted_at is not None
                    and utc(entry.deleted_at) == boundary
                )
            else:
                equal = (
                    not deleted and map_workout(entry.workout).content_hash == mapped.content_hash
                )
            if equal:
                print("same_event_at_exact_since=True")
                return
    print("same_event_at_exact_since=False")


def single_detail(client: HevyClient) -> HevyWorkout:
    items = list(client.workouts())
    if len(items) != 1:
        raise HevyError("expected one fixture")
    detail = client.workout(items[0].id)
    matched = map_workout(items[0]).content_hash == map_workout(detail).content_hash
    print(f"list_matches_detail={matched}")
    return detail


def order(workout: HevyWorkout) -> list[tuple[str, list[int | None]]]:
    return [
        (ex.exercise_template_id, [s.reps for s in sorted(ex.sets, key=lambda s: s.index)])
        for ex in sorted(workout.exercises, key=lambda ex: ex.index)
    ]


def rehearse(client: HevyClient, expected: str, pause: Callable[[str], str]) -> None:
    if client.identity() != expected:
        raise HevyError("dedicated identity mismatch")
    if next(client.workouts(), None) is not None:
        raise HevyError("dedicated account must start empty")
    since = datetime.now(UTC)
    pause("In the test app create the fixture described in the runbook, then press Enter. ")
    first = single_detail(client)
    initial = order(first)
    if (
        first.title != "Contract A"
        or len(initial) != 2
        or initial[0][0] == initial[1][0]
        or initial[0][1] != [3, 7]
        or initial[1][1] != [5]
    ):
        raise HevyError("unexpected fixture")
    observe_feed(client, since, first, deleted=False)
    pause(
        "In the test app rename to Contract B and reverse exercises and the two sets. Press Enter. "
    )
    second = single_detail(client)
    print(
        f"same_workout_id={first.id == second.id} title_edit_visible={second.title == 'Contract B'}"
    )
    print(
        f"created_time_stable={utc(first.created_at) == utc(second.created_at)} "
        f"updated_time_advanced={utc(second.updated_at) > utc(first.updated_at)}"
    )
    print(f"reorder_visible={order(second) == [initial[1], (initial[0][0], [7, 3])]}")
    if second.id != first.id:
        raise HevyError("workout identity changed")
    observe_feed(client, since, second, deleted=False)
    pause("In the test app delete only the synthetic fixture. Press Enter. ")
    print(f"workout_list_empty={next(client.workouts(), None) is None}")
    observe_feed(client, since, second, deleted=True)


def main() -> None:
    # Standalone process: even HTTP request paths can contain private identifiers.
    logging.disable(logging.CRITICAL)
    client = None
    try:
        if os.environ.get("SSLKEYLOGFILE"):
            raise HevyError("TLS key logging enabled")
        expected = os.environ["HEVY_TEST_ACCOUNT_ID"]
        client = HevyClient(os.environ["HEVY_TEST_API_KEY"], max_pages=4)
        rehearse(client, expected, input)
    except HevyError as exc:
        raise SystemExit(f"Probe stopped: {exc}") from None
    except (KeyboardInterrupt, Exception):
        raise SystemExit("Probe stopped. Check test configuration and provider contract.") from None
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()

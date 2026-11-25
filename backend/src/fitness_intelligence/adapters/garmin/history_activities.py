"""Converging offset scans and resumable, per-activity detail commits."""

from collections import Counter
from collections.abc import Iterator
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from fitness_intelligence.db.history_models import GarminCoverage

from .binding import detail_for
from .client import Endpoint, GarminError
from .history_state import Category, close_issues, day_key, days, digest, issue
from .importer import activity_snapshot
from .mapping import LIST_STAMP, MappingError, Row, WorkoutResponse, map_activity, rows, stamp
from .persistence import save_activity
from .projection import activity_inputs

if TYPE_CHECKING:
    from .history import HistoryRun

PAGE_SIZE = 10


def listing(run: "HistoryRun", first: date, last: date) -> Iterator[tuple[int, date, str, Row]]:
    seen = set()
    previous = None
    offset = 0
    while True:
        page = rows(
            run.client.read(
                Endpoint.ACTIVITIES,
                params={
                    "startDate": first.isoformat(),
                    "endDate": last.isoformat(),
                    "start": offset,
                    "limit": PAGE_SIZE,
                    "excludeChildren": "true",
                    "sortBy": "startLocal",
                    "sortOrder": "asc",
                },
            )
        )
        if len(page) > PAGE_SIZE:
            raise GarminError("activity page exceeds bound")
        for row in page:
            item = map_activity(run.binding, row)
            ident = int(item.external_id)
            local = stamp(row.get("startTimeLocal"), LIST_STAMP)
            if not first <= local.date() <= last:
                raise GarminError("activity outside requested range")
            if ident in seen or (previous is not None and local <= previous):
                raise GarminError("activity listing did not converge")
            previous = local
            seen.add(ident)
            signature = digest(activity_inputs(item, row, {}, None)["search"])
            yield ident, local.date(), signature, row
        if len(page) < PAGE_SIZE:
            break
        offset += len(page)


def activity_window(run: "HistoryRun", first: date, last: date) -> None:
    source = run.binding.source
    steps = Category.STEPS in run.scope.categories
    cats = (Category.ACTIVITIES, Category.STEPS) if steps else (Category.ACTIVITIES,)
    receipts = {}
    with run.session.begin():
        for d in days(first, last):
            row = run.session.get(GarminCoverage, day_key(source, Category.ACTIVITIES, d))
            receipts[d] = (
                dict(row.receipts) if row and row.pass_key == str(run.scope.pass_id) else {}
            )
            receipts[d].pop("unavailable", None)
    order = []
    totals: Counter[date] = Counter()
    step_counts: Counter[date] = Counter()
    first_scan_finished = False
    attempts = run.client.requests
    try:
        for ident, day, signature, row in listing(run, first, last):
            order.append((ident, signature))
            totals[day] += 1
            key = str(ident)
            receipt = receipts[day].get(key)
            if receipt and receipt["listing"] == signature and receipt["with_steps"] == steps:
                step_counts[day] += receipt["step_count"]
                continue
            detail = detail_for(run.client, run.binding, ident)
            activity = map_activity(run.binding, row, detail=detail)
            workouts = None
            if steps and activity.sport == "running":
                workouts = WorkoutResponse(
                    source, ident, run.client.read(Endpoint.WORKOUTS, activity_id=ident)
                )
            snapshot = activity_snapshot(run.binding, row, detail, workouts)
            now = datetime.now(UTC)
            reason = None
            try:
                with run.write() as counts:
                    result = save_activity(run.session, snapshot, now)
                    counts[result] += 1
                    if result in ("unresolved", "older", "partial"):
                        reason = "activity_revision_or_children"
                    if steps and (
                        activity.subtype is None
                        or (workouts is not None and snapshot.activity.steps is None)
                    ):
                        reason = "incomplete_steps"
                    if reason:
                        category = (
                            Category.STEPS if reason == "incomplete_steps" else Category.ACTIVITIES
                        )
                        issue(
                            run.session,
                            source,
                            category,
                            day,
                            key,
                            reason,
                            [signature, snapshot.updated],
                            now,
                        )
                    else:
                        if steps:
                            close_issues(
                                run.session,
                                source,
                                Category.STEPS,
                                day,
                                key,
                                ("incomplete_steps",),
                                now,
                            )
                        if snapshot.updated is not None:
                            close_issues(
                                run.session,
                                source,
                                Category.ACTIVITIES,
                                day,
                                key,
                                ("activity_revision_or_children",),
                                now,
                            )
                        # A same-revision contradiction needs positive evidence for the
                        # disputed fields. A later sparse receipt alone cannot identify them.
                        n = len(snapshot.activity.steps or ())
                        receipts[day] = receipts[day] | {
                            key: dict(listing=signature, with_steps=steps, step_count=n)
                        }
                        step_counts[day] += n
                    run.mark(Category.ACTIVITIES, day, "partial", receipts=receipts[day])
                    if steps or (
                        result in ("created", "updated", "partial")
                        and run.session.get(GarminCoverage, day_key(source, Category.STEPS, day))
                    ):
                        run.mark(Category.STEPS, day, "partial")
            except GarminError as exc:
                if str(exc) == "conflicting activity version":
                    with run.write() as counts:
                        issue(
                            run.session,
                            source,
                            Category.ACTIVITIES,
                            day,
                            key,
                            "contradictory_revision",
                            [signature, snapshot.updated],
                            now,
                        )
                        counts["unresolved"] += 1
                raise
            if reason:
                raise GarminError("activity detail requires reconciliation")
        first_scan_finished = True
        check = [(ident, sig) for ident, _, sig, _ in listing(run, first, last)]
        if order != check:
            raise GarminError("activity listing did not converge")
    except (GarminError, MappingError) as exc:
        if run.client.requests > attempts and str(exc) != "verified session expired":
            with run.write():
                for day in days(first, last):
                    status = (
                        "partial" if order or first_scan_finished or receipts[day] else "failed"
                    )
                    run.mark(Category.ACTIVITIES, day, status, receipts=receipts[day])
                    if steps:
                        run.mark(Category.STEPS, day, status)
        raise
    with run.write():
        for d in days(first, last):
            for c in cats:
                n = (totals if c == Category.ACTIVITIES else step_counts)[d]
                run.mark(c, d, "observed" if n else "empty", n)

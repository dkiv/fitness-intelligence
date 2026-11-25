"""One operator invocation, one verified bearer and one account advisory lock."""

from collections import Counter
from collections.abc import Iterator, Sequence
from contextlib import ExitStack, contextmanager
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from fitness_intelligence.adapters.local_account import locked_account
from fitness_intelligence.db.history_models import GarminCoverage, GarminIssue
from fitness_intelligence.domain.endurance import DailyMetric, DailyObservation

from .binding import Evidence, EvidenceType, Feed, feed_for, verify
from .client import Endpoint, GarminClient, GarminError
from .history_activities import activity_window
from .history_feeds import (
    DAILY,
    expenditure,
    intake_conflict,
    read_range,
    recovery,
    save_recovery,
    targeted_intake,
    v2_intake,
)
from .history_state import Category, Scope, account_key, coverage, day_key, days
from .history_weight import reconcile_weight
from .mapping import GarminBinding, MappingError, Row, map_day
from .nutrition import save_intake


class HistoryRun:
    def __init__(
        self,
        session: Session,
        evidence: Evidence,
        binding: GarminBinding,
        client: GarminClient,
        scope: Scope,
    ) -> None:
        self.session, self.evidence, self.binding, self.client, self.scope = (
            session,
            evidence,
            binding,
            client,
            scope,
        )
        self.counts: Counter[str] = Counter()
        self.failures: list[str] = []
        self.affected: dict[date, tuple[Category, ...]] = {}
        self.partial_activity_days: set[date] = set()

    @contextmanager
    def write(self) -> Iterator[Counter[str]]:
        batch: Counter[str] = Counter()
        with self.session.begin():
            self.evidence.resolve(
                self.session, allow_new=False, observed=self.binding, for_write=True
            )
            yield batch
            self.client.check_verified_session()
        self.counts.update(batch)

    def mark(
        self,
        cat: Category,
        day: date,
        status: str,
        count: int | None = None,
        receipts: dict | None = None,
    ) -> None:
        coverage(self.session, self.binding.source, self.scope, cat, day, status, count, receipts)

    def observations(self, cat: Category, day: date, values: Sequence[DailyObservation]) -> None:
        when = datetime.now(UTC)
        with self.write() as counts:
            for value in values:
                counts[save_recovery(self.session, value, when)] += 1
            self.mark(cat, day, "observed" if values else "empty", len(values))

    def daily(self, day: date, series: list[Row], cats: tuple[Category, ...]) -> None:
        when = datetime.now(UTC)
        fallback = False
        total = None
        if Category.INTAKE in cats:
            total = v2_intake(series)
            with self.write() as counts:
                if total:
                    counts[save_intake(self.session, self.binding, day, total, when)] += 1
                conflict = intake_conflict(self.session, self.binding, day, when, total is not None)
                fallback = conflict or total is None or self.scope.mode == "repair"
                self.mark(
                    Category.INTAKE,
                    day,
                    "partial" if fallback else "observed",
                    int(total is not None),
                )
        energy = expenditure(self.binding, day, series) if Category.EXPENDITURE in cats else []
        need_energy = Category.EXPENDITURE in cats and len(energy) < 3
        if Category.EXPENDITURE in cats and not need_energy:
            self.observations(Category.EXPENDITURE, day, energy)
        if not (fallback or need_energy or Category.RESTING in cats):
            return
        daily = feed_for(self.client, self.binding, day, Feed.DAILY)
        if Category.RESTING in cats or need_energy:
            mapped = map_day(self.binding, day, daily=daily)
            if Category.RESTING in cats:
                self.observations(
                    Category.RESTING, day, [v for v in mapped if v.metric == DailyMetric.RESTING_HR]
                )
            if need_energy:
                known = {v.metric for v in energy}
                energy.extend(
                    v
                    for v in mapped
                    if v.metric != DailyMetric.RESTING_HR and v.metric not in known
                )
                self.observations(Category.EXPENDITURE, day, energy)
        if fallback:
            more = targeted_intake(self.client, self.binding, day, daily)
            with self.write() as counts:
                for value in more:
                    counts[save_intake(self.session, self.binding, day, value, when)] += 1
                if intake_conflict(self.session, self.binding, day, when, bool(more)):
                    counts["unresolved"] += 1
                n = len(more) + int(total is not None)
                self.mark(Category.INTAKE, day, "observed" if n else "empty", n)

    def pending(self) -> dict[date, tuple[Category, ...]]:
        s = self.scope
        with self.session.begin():
            records = self.session.scalars(
                select(GarminCoverage)
                .filter_by(**account_key(self.binding.source))
                .where(
                    GarminCoverage.local_date.between(s.start, s.end),
                    GarminCoverage.category.in_(s.categories),
                )
            )
            state = {(r.category, r.local_date): r for r in records}
            self.partial_activity_days = {
                day
                for (category, day), row in state.items()
                if category == Category.ACTIVITIES and row.status == "partial"
            }
            return {
                d: tuple(c for c in s.categories if not s.done(state.get((c, d)), c, d))
                for d in days(s.start, s.end)
            }

    def batch(self, group: tuple[Category, ...], first: date, last: date, pending: dict) -> None:
        self.affected = {d: tuple(c for c in group if c in pending[d]) for d in days(first, last)}
        if Category.ACTIVITIES in group:
            activity_window(self, first, last)
            return
        cat = group[0]
        endpoint = {
            Category.SLEEP: Endpoint.SLEEP_RANGE,
            Category.HRV: Endpoint.HRV_RANGE,
            Category.WEIGHT: Endpoint.WEIGHT_RANGE,
        }.get(cat, Endpoint.DAILY_RANGE)
        try:
            only_resting = all(cats == (Category.RESTING,) for cats in self.affected.values())
            by_day = (
                {} if only_resting else read_range(self.client, self.binding, endpoint, first, last)
            )
        except GarminError as exc:
            if endpoint == Endpoint.DAILY_RANGE and str(exc) == "not_found":
                by_day = {}
            elif first < last and str(exc) == "response_too_large":
                middle = first + (last - first) // 2
                self.batch(group, first, middle, pending)
                self.batch(group, middle + timedelta(days=1), last, pending)
                return
            else:
                raise
        stamps = Counter(
            row["timestampGMT"]
            for series in by_day.values()
            for row in series
            if endpoint == Endpoint.WEIGHT_RANGE and type(row.get("timestampGMT")) is int
        )
        collisions = {stamp for stamp, n in stamps.items() if n > 1}
        for d in days(first, last):
            cats = tuple(c for c in group if c in pending[d])
            if not cats:
                continue
            self.affected = {d: cats}
            series = by_day.get(d)
            if cat in DAILY:
                self.daily(d, series or [], cats)
            elif cat == Category.WEIGHT:
                assert self.scope.weight is not None
                with self.write() as counts:
                    result, stop = reconcile_weight(
                        self.session,
                        self.binding,
                        d,
                        series or [],
                        self.scope.weight,
                        datetime.now(UTC),
                        collisions,
                    )
                    counts.update(result)
                    n = sum(row.get("weight") is not None for row in series or ())
                    self.mark(cat, d, "partial" if stop else "observed" if n else "empty", n)
                if stop:
                    raise GarminError("weight verification required")
            else:
                self.observations(cat, d, recovery(self.client, self.binding, cat, d, series))

    def execute(self) -> dict:
        scope = self.scope
        pending = self.pending()
        stop = None
        groups = [
            ((Category.ACTIVITIES, Category.STEPS), 7),
            (DAILY, 28),
            ((Category.SLEEP,), 28),
            ((Category.HRV,), 7),
            ((Category.WEIGHT,), 28),
        ]
        for group, size in groups:
            todo = [d for d, missing in pending.items() if set(missing).intersection(group)]
            while todo and stop is None:
                first = last = todo.pop(0)
                while (
                    todo
                    and (todo[0] - last).days == 1
                    and (todo[0] - first).days < size
                    and not (
                        Category.ACTIVITIES in group
                        and (
                            first in self.partial_activity_days
                            or todo[0] in self.partial_activity_days
                        )
                    )
                ):
                    last = todo.pop(0)
                attempts = self.client.requests
                try:
                    self.batch(group, first, last, pending)
                except (MappingError, GarminError) as exc:
                    stop = str(exc)
                    self.failures.append(stop)
                    # Only the range read was necessarily attempted. Per-day completions
                    # already committed in this batch remain authoritative.
                    if self.client.requests > attempts and stop not in (
                        "budget_exhausted",
                        "verified session expired",
                    ):
                        with self.write():
                            for d, affected in self.affected.items():
                                for c in affected:
                                    row = self.session.get(
                                        GarminCoverage, day_key(self.binding.source, c, d)
                                    )
                                    if (
                                        row
                                        and row.pass_key == str(scope.pass_id)
                                        and row.status in ("empty", "observed", "partial")
                                    ):
                                        continue
                                    self.mark(c, d, "failed")
                    if stop in (
                        "not_found",
                        "transport_error",
                        "activity listing did not converge",
                    ) or stop.startswith("http_error_5"):
                        stop = None
                        break
        return self.report()

    def report(self) -> dict:
        scope = self.scope
        remaining = self.pending()
        status = {}
        with self.session.begin():
            for c in scope.categories:
                undone = [d for d, missing in remaining.items() if c in missing]
                q = (
                    select(func.count())
                    .select_from(GarminIssue)
                    .filter_by(
                        **account_key(self.binding.source), category=c.value, resolved_at=None
                    )
                    .where(GarminIssue.local_date.between(scope.start, scope.end))
                )
                status[c.value] = dict(
                    completed=len(remaining) - len(undone),
                    remaining=len(undone),
                    resume=undone[0].isoformat() if undone else None,
                    open_issues=self.session.scalar(q),
                )
        return dict(
            mode=scope.mode,
            start=scope.start.isoformat(),
            end=scope.end.isoformat(),
            pass_id=str(scope.pass_id),
            categories=status,
            requests=dict(self.client.attempts),
            stopped=self.failures[-1] if self.failures else None,
            failures=self.failures,
            failed_or_incomplete_batches=len(self.failures),
            observations={
                k: self.counts[k]
                for k in ("created", "updated", "unchanged", "unresolved", "partial", "older")
            },
        )


def synchronize(engine: Engine, evidence: Evidence, client: GarminClient, scope: Scope) -> dict:
    scope.validate()
    if scope.weight and scope.weight.source != evidence.source:
        raise GarminError("weight verification account mismatch")
    if evidence.kind == EvidenceType.INDEPENDENT and not evidence.durability_confirmed:
        raise GarminError("independent durability evidence required")
    with locked_account(engine, evidence.source.source_account_id) as session:
        with session.begin():
            expected = evidence.resolve(session, allow_new=False)
        assert expected is not None
        run = HistoryRun(session, evidence, expected, client, scope)
        with ExitStack() as stack:
            try:
                stack.enter_context(client.verified_session())
                verify(client, evidence, expected)
            except (GarminError, MappingError) as exc:
                run.failures.append(str(exc))
                return run.report()
            return run.execute()

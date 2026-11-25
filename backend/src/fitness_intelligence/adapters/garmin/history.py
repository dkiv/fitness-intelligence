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
    read_food_intake,
    read_range,
    recovery,
    save_recovery,
    v2_intake,
)
from .history_state import Category, Scope, account_key, coverage, day_key, days
from .history_weight import reconcile_weight
from .mapping import GarminBinding, MappingError, Row, map_day
from .nutrition import Intake, daily_intake, save_intake


# Unverified absence on a dated resource. Auth, schema and transport errors
# have distinct handling and must never enter the isolated-date path.
def unavailable_read(reason: str) -> bool:
    return reason in {"not_found", "no_content"} or reason.startswith("http_error_5")


class GroupUnavailable(Exception):
    """Two consecutive unavailable dates in this group during one invocation."""


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
        self.unavailable: dict[tuple[Category, date], datetime] = {}
        self.unit_holds: set[date] = set()
        self.incomplete_intake: set[date] = set()
        self.consecutive_gaps = 0
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

    def daily(
        self, day: date, series: list[Row], cats: tuple[Category, ...], v2_missing: bool
    ) -> None:
        # Each accepted source and its current corroboration status share a transaction.
        sources: dict[str, str] = {}
        confirmed: set[str] = set()

        def record(
            source: str,
            observation: Intake | None,
            *,
            unavailable: bool = False,
            final: bool = False,
        ) -> bool:
            sources[source] = (
                "unavailable" if unavailable else "observed" if observation else "no_eligible"
            )
            when = datetime.now(UTC)
            with self.write() as counts:
                if observation is not None:
                    counts[save_intake(self.session, self.binding, day, observation, when)] += 1
                    confirmed.add(observation.field)
                complete = final and "unavailable" not in sources.values()
                conflict = intake_conflict(
                    self.session, self.binding, day, when, confirmed if complete else set()
                )
                targeted = source == "v2" and (
                    conflict
                    or not observation
                    or self.scope.mode == "repair"
                    or day in self.incomplete_intake
                )
                status = (
                    "partial" if targeted or not complete else "observed" if confirmed else "empty"
                )
                self.mark(Category.INTAKE, day, status, len(confirmed), {"sources": dict(sources)})
                if final and conflict and not targeted:
                    counts["unresolved"] += 1
            return targeted

        fallback = False
        if Category.INTAKE in cats:
            fallback = record("v2", v2_intake(series), unavailable=v2_missing, final=True)
        energy = expenditure(self.binding, day, series) if Category.EXPENDITURE in cats else []
        need_energy = Category.EXPENDITURE in cats and len(energy) < 3
        if Category.EXPENDITURE in cats and not need_energy:
            self.observations(Category.EXPENDITURE, day, energy)
        if not (fallback or need_energy or Category.RESTING in cats):
            return
        missing = "not_found" if fallback and v2_missing else None
        try:
            daily = feed_for(self.client, self.binding, day, Feed.DAILY)
        except GarminError as exc:
            if not fallback or not unavailable_read(str(exc)):
                if fallback and str(exc) == "transport_error":
                    record("daily", None, unavailable=True)
                raise
            missing = str(exc)
            daily = None
        if fallback:
            observed = daily_intake(self.binding, day, daily) if daily is not None else None
            record("daily", observed, unavailable=daily is None)
        if daily is not None and (Category.RESTING in cats or need_energy):
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
            try:
                food = read_food_intake(self.client, day)
            except GarminError as exc:
                if unavailable_read(str(exc)) or str(exc) == "transport_error":
                    record("food", None, unavailable=True, final=True)
                raise
            record("food", food, final=True)
        if missing:
            raise GarminError(missing)

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
            if Category.WEIGHT in s.categories:
                self.unit_holds = set(
                    self.session.scalars(
                        select(GarminIssue.local_date)
                        .filter_by(
                            **account_key(self.binding.source),
                            category=Category.WEIGHT,
                            reason="unit_or_format",
                            resolved_at=None,
                        )
                        .where(GarminIssue.local_date.between(s.start, s.end))
                    )
                )
            self.unavailable = {
                (cat, d): row.attempted_at
                for (cat, d), row in state.items()
                if "unavailable" in row.receipts and row.status in ("failed", "partial")
            }
            self.incomplete_intake = {
                d
                for (cat, d), row in state.items()
                if cat == Category.INTAKE and row.status == "partial"
            }
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
        v2_missing = False
        try:
            only_resting = all(cats == (Category.RESTING,) for cats in self.affected.values())
            by_day = (
                {} if only_resting else read_range(self.client, self.binding, endpoint, first, last)
            )
        except GarminError as exc:
            if endpoint == Endpoint.DAILY_RANGE and str(exc) == "not_found":
                by_day = {}
                v2_missing = True
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
            try:
                self.process_day(cat, cats, d, by_day.get(d), collisions, v2_missing)
            except GarminError as exc:
                if not unavailable_read(str(exc)):
                    raise
                self.record_failure(str(exc), unavailable=True)
                self.consecutive_gaps += 1
                if self.consecutive_gaps >= 2:
                    raise GroupUnavailable from exc
            else:
                self.consecutive_gaps = 0

    def process_day(
        self,
        cat: Category,
        cats: tuple[Category, ...],
        d: date,
        series: list[Row] | None,
        collisions: set[int],
        v2_missing: bool,
    ) -> None:
        if cat in DAILY:
            self.daily(d, series or [], cats, v2_missing)
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
                accepted = result["created"] + result["updated"] + result["unchanged"]
                observed = any(row.get("weight") is not None for row in series or ())
                self.mark(
                    cat, d, "partial" if stop else "observed" if observed else "empty", accepted
                )
            if stop:
                raise GarminError("weight verification required")
        else:
            self.observations(cat, d, recovery(self.client, self.binding, cat, d, series))

    def record_failure(self, reason: str, *, unavailable: bool = False) -> None:
        self.failures.append(reason)
        with self.write():
            for d, cats in self.affected.items():
                for c in cats:
                    row = self.session.get(GarminCoverage, day_key(self.binding.source, c, d))
                    current = (
                        row is not None
                        and row.pass_key == str(self.scope.pass_id)
                        and row.policy == self.scope.policy(c)
                    )
                    if current and row.status in ("empty", "observed"):
                        continue
                    status = "partial" if current and row.status == "partial" else "failed"
                    receipts = dict(row.receipts) if current else {}
                    receipts.pop("unavailable", None)
                    if unavailable:
                        receipts["unavailable"] = {"reason": reason}
                    self.mark(c, d, status, receipts=receipts)

    def execute(self) -> dict:
        pending = self.pending()
        stop = None
        groups = [
            ((Category.ACTIVITIES, Category.STEPS), 7),
            (DAILY, 28),
            ((Category.SLEEP,), 28),
            ((Category.HRV,), 7),
            ((Category.WEIGHT,), 28),
        ]
        # A group consisting solely of known gaps must not spend every invocation's
        # remaining budget before another group's first eligible read.
        work = []
        for group, size in groups:
            todo = [d for d, missing in pending.items() if set(missing).intersection(group)]
            # Previously unavailable windows get single-day retries after new work.
            # Among known gaps, the least recently attempted day gets the next turn.
            retry = {
                d: max(self.unavailable[c, d] for c in group if (c, d) in self.unavailable)
                for d in todo
                if any((c, d) in self.unavailable for c in group)
            }
            holds = self.unit_holds if Category.WEIGHT in group else set()
            if todo:
                deferred_since = (
                    min(retry.values()) if len(retry) == len(todo) and not holds else None
                )
                work.append((deferred_since, group, size, todo, retry, holds))
        for _, group, size, todo, retry, holds in sorted(
            work, key=lambda item: (item[0] is not None, item[0])
        ):
            todo.sort(key=lambda d: (d not in holds, d in retry, retry.get(d), d))
            singles = set(retry) | holds
            if Category.ACTIVITIES in group:
                singles.update(self.partial_activity_days)
            self.consecutive_gaps = 0
            while todo and stop is None:
                first = last = todo.pop(0)
                while (
                    todo
                    and (todo[0] - last).days == 1
                    and first not in singles
                    and todo[0] not in singles
                    and (todo[0] - first).days < size
                ):
                    last = todo.pop(0)
                attempts = self.client.requests
                try:
                    self.batch(group, first, last, pending)
                except GroupUnavailable:
                    break
                except (MappingError, GarminError) as exc:
                    reason = str(exc)
                    dated = (
                        unavailable_read(reason) or reason == "activity listing did not converge"
                    )
                    if self.client.requests > attempts and reason not in (
                        "budget_exhausted",
                        "verified session expired",
                    ):
                        self.record_failure(
                            reason, unavailable=dated or reason == "transport_error"
                        )
                    else:
                        self.failures.append(reason)
                    if first in holds:
                        stop = reason
                    elif reason.startswith("http_error_5") and first != last:
                        # A server failure on the range GET cannot be localized this pass.
                        break
                    elif dated:
                        # A failed whole window has no sound per-day evidence. Retry it
                        # in singles on resume. Continue with the next disjoint window.
                        self.consecutive_gaps += 1
                        if self.consecutive_gaps >= 2:
                            break
                    elif reason == "transport_error":
                        break
                    else:
                        stop = reason
                else:
                    if Category.ACTIVITIES in group:
                        self.consecutive_gaps = 0
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
                gaps = []
                for d in undone:
                    if gaps and (d - gaps[-1][1]).days == 1:
                        gaps[-1][1] = d
                    else:
                        gaps.append([d, d])
                through = scope.end
                if undone:
                    through = undone[0] - timedelta(days=1) if undone[0] > scope.start else None
                status[c.value] = dict(
                    completed_through=through.isoformat() if through else None,
                    gaps=[[str(first), str(last)] for first, last in gaps],
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

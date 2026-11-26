"""Finite, deterministic placement of a familiar synthetic baseline."""

from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID, uuid5
from zoneinfo import ZoneInfo

from . import familiar as f

SEARCH_LIMIT = 20_000
GRID_MINUTES = 5


class PlacementFailure(ValueError):
    def __init__(
        self, *, incomplete: bool, examined: int, limit: int, reasons: tuple[str, ...]
    ) -> None:
        self.incomplete = incomplete
        self.examined = examined
        self.limit = limit
        self.reasons = reasons
        status = "search incomplete" if incomplete else "infeasible within stated domain"
        super().__init__(
            f"{status} ({examined} placements examined, limit {limit}, "
            f"{GRID_MINUTES}-minute grid plus fixed starts): " + ", ".join(reasons)
        )


def _validate_baseline(block: f.Block, ctx: f.Context, limit: int) -> None:
    """One distinct reported occurrence per template from the same recent representative week."""
    if not 7 <= (block.start - ctx.history_start).days <= 28:
        raise ValueError("baseline requires a recent completed representative week")
    by_template = {t.key: t.prescription for t in block.templates}
    if Counter(o.template for o in ctx.observations) != Counter(by_template.keys()):
        raise ValueError("insufficient or ambiguous comparable session history")
    for o in ctx.observations:
        p = by_template[o.template]
        if (
            not o.confirmed
            or o.provenance != "synthetic-athlete-report"
            or o.manageable is not True
            or o.role != p.role
        ):
            raise ValueError("familiar baseline requires confirmed, manageable role-specific work")
        if isinstance(p, f.Strength):
            expected = tuple(
                f.ActualSet(
                    movement=e.movement,
                    variation=e.variation,
                    equipment=e.equipment,
                    convention=e.load_convention,
                    group=g.key,
                    kind=g.kind,
                    ordinal=s.ordinal,
                    reps=s.reps.nominal,
                    kg=s.load.nominal,
                )
                for e in p.exercises
                for g in e.groups
                for s in g.sets
            )
            reported = tuple(
                a.model_copy(update={"familiar_max_reps": None, "familiar_max_kg": None})
                for a in o.sets
            )
            targets = (s for e in p.exercises for g in e.groups for s in g.sets)
            if reported != expected or any(
                s.reps.high > (a.familiar_max_reps or a.reps)
                or s.load.high > (a.kg if a.familiar_max_kg is None else a.familiar_max_kg)
                for s, a in zip(targets, o.sets, strict=True)
            ):
                raise ValueError("strength baseline differs from comparable actual work")
        elif len(o.steps) != len(p.steps) or any(
            a.purpose != s.purpose
            or a.elapsed_seconds != s.seconds.nominal
            or s.seconds.high > (a.familiar_max_seconds or a.elapsed_seconds)
            for a, s in zip(o.steps, p.steps, strict=True)
        ):
            raise ValueError("running baseline differs from confirmed elapsed work")
    for c in block.commitments:
        count = sum(
            p.sport == c.sport and p.role == c.role and p.minimum_exposure >= c.minimum_per_session
            for p in by_template.values()
        )
        if count < c.sessions:
            reason = (
                f"protected {c.role} needs {c.sessions} sessions at "
                f"{c.minimum_per_session}, found {count}"
            )
            raise PlacementFailure(incomplete=False, examined=0, limit=limit, reasons=(reason,))
    for protected in block.protections:
        if not any(
            p.sport == protected.sport
            and (
                p.role == protected.task
                or isinstance(p, f.Strength)
                and any(e.movement == protected.task for e in p.exercises)
            )
            for p in by_template.values()
        ):
            raise ValueError("protected outcome task absent from baseline")
    for pin in ctx.fixed:
        if pin.template not in by_template or not 0 <= (pin.day - block.start).days < 7 * len(
            block.phases
        ):
            raise ValueError("fixed session outside block or unknown template")
    f.unique(
        (((pin.day - block.start).days // 7, pin.template) for pin in ctx.fixed), "fixed occurrence"
    )


def _instant(day: date, minute: int, zone: ZoneInfo, fold: int | None = None) -> datetime | None:
    wall = datetime.combine(day, time.min) + timedelta(minutes=minute)
    first = wall.replace(tzinfo=zone, fold=0)
    second = wall.replace(tzinfo=zone, fold=1)
    if first.utcoffset() != second.utcoffset() and fold is None:
        return None
    local = second if fold == 1 else first
    instant = local.astimezone(UTC)
    returned = instant.astimezone(zone)
    if returned.replace(tzinfo=None) != wall or returned.fold != local.fold:
        return None
    return instant


def _conflicts(session: f.Session, others: tuple[f.Session, ...], block: f.Block) -> str | None:
    for other in others:
        if session.start_utc < other.end and other.start_utc < session.end:
            return f"{session.template}/{other.template} overlap"
        for gap in block.spacing:
            if {gap.first, gap.second} == {session.template, other.template}:
                actual = abs(session.start_utc - other.start_utc)
                if actual.total_seconds() < gap.elapsed_seconds:
                    pair = f"{session.template}/{other.template}"
                    seconds = actual.total_seconds()
                    return f"{pair} spacing {seconds:g}s requires {gap.elapsed_seconds}s"
    return None


@dataclass(frozen=True)
class _Option:
    session: f.Session | None
    reason: str = ""


def _options(
    cycle: UUID, block: f.Block, ctx: f.Context, number: int, template: f.Template
) -> Iterator[_Option]:
    """Enumerate eligible starts lazily so the search limit also bounds rejected placements."""
    zone = ZoneInfo(ctx.zone)
    start = block.start + timedelta(weeks=number - 1)
    days = [start + timedelta(days=i) for i in range(7)]
    preferred = {day: rank for rank, day in enumerate(ctx.preferred_weekdays)}
    habitual = next(o.day.weekday() for o in ctx.observations if o.template == template.key)
    days.sort(key=lambda d: (preferred.get(d.weekday(), 7), d.weekday() != habitual, d))
    key, p = template.key, template.prescription
    occurrence = uuid5(cycle, f"{block.key}/{number}/{key}")
    tasks = {key, p.role, p.sport}
    equipment: set[str] = set()
    if isinstance(p, f.Strength):
        tasks.update(e.movement for e in p.exercises)
        tasks.update(e.variation for e in p.exercises)
        equipment.update(e.equipment for e in p.exercises)
    if tasks.intersection(ctx.excluded_tasks):
        yield _Option(None, f"{key} is restricted")
        return
    fixed = next((pin for pin in ctx.fixed if pin.template == key and pin.day in days), None)
    for day in days:
        if (fixed and fixed.day != day) or day in ctx.unavailable_dates:
            continue
        for win in sorted(
            ctx.windows, key=lambda w: (w.weekday, w.start_minute, w.end_minute, w.equipment)
        ):
            if win.weekday != day.weekday():
                continue
            if not equipment.issubset(win.equipment):
                yield _Option(None, f"{key} lacks required equipment")
                continue
            begin = _instant(day, win.start_minute, zone)
            end = _instant(day, win.end_minute, zone)
            if begin is None or end is None:
                yield _Option(None, f"{key} unavailable DST window boundary")
                continue
            minutes = (
                (fixed.minute,)
                if fixed
                else range(
                    (win.start_minute + GRID_MINUTES - 1) // GRID_MINUTES * GRID_MINUTES,
                    win.end_minute,
                    GRID_MINUTES,
                )
            )
            for minute in minutes:
                instant = _instant(day, minute, zone, fixed.fold if fixed else None)
                if instant is None or not begin <= instant < end:
                    yield _Option(None, f"{key} invalid local start")
                    continue
                session = f.Session(
                    occurrence=occurrence, template=key, day=day, start_utc=instant, prescription=p
                )
                if p.reserved_seconds > (end - instant).total_seconds():
                    yield _Option(None, f"{key} requires {p.reserved_seconds}s within window")
                elif any(instant < e.end and e.start < session.end for e in ctx.events):
                    yield _Option(None, f"{key} conflicts with fixed event")
                else:
                    yield _Option(session)


def generate(
    cycle: UUID,
    block: f.Block,
    ctx: f.Context,
    number: int,
    adjacent: tuple[f.Session, ...] = (),
    *,
    limit: int = SEARCH_LIMIT,
) -> tuple[f.Day, ...]:
    if type(number) is not int or not 1 <= number <= len(block.phases):
        raise ValueError("week number outside block")
    _validate_baseline(block, ctx, limit)
    ordered = sorted(block.templates, key=lambda t: (ctx.rank(t.prescription.sport), t.key))
    examined = 0
    reasons: set[str] = set()

    # Known fixed occurrences beyond the requested week reserve real time now.
    # Weeks subsequently detailed retain their actual approved starts via adjacent.
    by_key = {t.key: t for t in block.templates}
    occupied = list(adjacent)
    existing = {s.occurrence for s in adjacent}
    for pin in ctx.fixed:
        pin_week = (pin.day - block.start).days // 7 + 1
        if pin_week <= number:
            continue
        options = _options(cycle, block, ctx, pin_week, by_key[pin.template])
        fixed = next((o.session for o in options if o.session is not None), None)
        if fixed is None:
            raise PlacementFailure(
                incomplete=False,
                examined=0,
                limit=limit,
                reasons=(f"{pin.template} fixed start is unavailable",),
            )
        if fixed.occurrence not in existing:
            conflict = _conflicts(fixed, tuple(occupied), block)
            if conflict:
                raise PlacementFailure(
                    incomplete=False, examined=0, limit=limit, reasons=(conflict,)
                )
            occupied.append(fixed)
            existing.add(fixed.occurrence)
    boundaries = tuple(occupied)

    def search(selected: tuple[f.Session, ...]) -> tuple[f.Session, ...] | None:
        nonlocal examined
        if len(selected) == len(ordered):
            return selected
        template = ordered[len(selected)]
        for option in _options(cycle, block, ctx, number, template):
            if examined >= limit:
                raise PlacementFailure(
                    incomplete=True,
                    examined=examined,
                    limit=limit,
                    reasons=tuple(sorted(reasons)) or ("placement limit",),
                )
            examined += 1
            s = option.session
            if s is None:
                reasons.add(option.reason)
                continue
            conflict = _conflicts(s, boundaries + selected, block)
            if conflict:
                reasons.add(conflict)
                continue
            result = search((*selected, s))
            if result is not None:
                return result
        reasons.add(f"{template.key} has no remaining eligible start")
        return None

    sessions = search(())
    if sessions is None:
        raise PlacementFailure(
            incomplete=False, examined=examined, limit=limit, reasons=tuple(sorted(reasons))
        )
    start = block.start + timedelta(weeks=number - 1)
    ordered_sessions = sorted(sessions, key=lambda s: (s.start_utc, s.template))
    return tuple(
        f.Day(day=day, sessions=tuple(s for s in ordered_sessions if s.day == day))
        for day in (start + timedelta(days=i) for i in range(7))
    )


def validate_retained(
    cycle: UUID, block: f.Block, ctx: f.Context, number: int, days: tuple[f.Day, ...], today: date
) -> None:
    """A changed context may retain future sessions only at their exact approved instants."""
    templates = {t.key: t for t in block.templates}
    for day in days:
        for session in day.sessions:
            pins = (
                pin
                for pin in ctx.fixed
                if pin.template == session.template and days[0].day <= pin.day <= days[-1].day
            )
            if any(pin.day != session.day for pin in pins):
                raise ValueError("fixed date conflicts with retained prescription")
            if day.day >= today and not any(
                option.session == session
                for option in _options(cycle, block, ctx, number, templates[session.template])
            ):
                raise ValueError("a retained prescription conflicts with current constraints")

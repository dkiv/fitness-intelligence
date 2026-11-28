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


def _require_familiar_effort(
    proposed: f.Effort, evidence: f.EffortEvidence | None, scope: str
) -> None:
    if evidence is None or evidence.confirmed_target is None:
        raise ValueError(f"{scope}: numeric effort target has no confirmed familiar instruction")
    if proposed.target != evidence.confirmed_target:
        raise ValueError(f"{scope}: effort range or nominal differs from confirmed instruction")
    if proposed.cap != evidence.confirmed_cap:
        raise ValueError(f"{scope}: execution cap lacks matching explicit confirmation")
    if evidence.observed_rpe is not None and evidence.observed_rpe > proposed.cap:
        raise ValueError(f"{scope}: observed effort exceeded the confirmed execution cap")


def validate_baseline(block: f.Block, ctx: f.Context, limit: int, rule: f.FamiliarRule) -> None:
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
            prescribed = tuple((e, g, s) for e in p.exercises for g in e.groups for s in g.sets)
            if len(o.sets) != len(prescribed):
                raise ValueError("strength baseline differs from comparable actual work")
            for (exercise, group, target), actual in zip(prescribed, o.sets, strict=True):
                identity = (
                    exercise.movement,
                    exercise.variation,
                    exercise.equipment,
                    exercise.load_convention,
                    group.key,
                    group.kind,
                    target.ordinal,
                )
                reported = (
                    actual.movement,
                    actual.variation,
                    actual.equipment,
                    actual.convention,
                    actual.group,
                    actual.kind,
                    actual.ordinal,
                )
                if (
                    identity != reported
                    or actual.reps != target.reps.nominal
                    or actual.kg != target.load.nominal
                    or target.reps.high > (actual.familiar_max_reps or actual.reps)
                    or target.load.high
                    > (actual.kg if actual.familiar_max_kg is None else actual.familiar_max_kg)
                ):
                    raise ValueError("strength baseline differs from comparable actual work")
                if rule == f.RULE:
                    scope = f"{o.template}/{exercise.movement}/{group.key} set {target.ordinal}"
                    _require_familiar_effort(group.effort, actual.effort, scope)
        elif len(o.steps) != len(p.steps) or any(
            a.purpose != s.purpose
            or a.elapsed_seconds != s.seconds.nominal
            or s.seconds.high > (a.familiar_max_seconds or a.elapsed_seconds)
            for a, s in zip(o.steps, p.steps, strict=True)
        ):
            raise ValueError("running baseline differs from confirmed elapsed work")
        elif rule == f.RULE:
            for index, (step, actual) in enumerate(zip(p.steps, o.steps, strict=True), 1):
                scope = f"{o.template}/{o.role} step {index} ({step.purpose})"
                _require_familiar_effort(step.effort, actual.effort, scope)
    _validate_commitments(block, by_template, limit)
    for pin in ctx.fixed:
        if pin.template not in by_template or not 0 <= (pin.day - block.start).days < 7 * len(
            block.phases
        ):
            raise ValueError("fixed session outside block or unknown template")
    f.unique(
        (((pin.day - block.start).days // 7, pin.template) for pin in ctx.fixed), "fixed occurrence"
    )


def _validate_commitments(
    block: f.Block, by_template: dict[str, f.Prescription], limit: int
) -> None:
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
    return generate_for_rule(cycle, block, ctx, number, adjacent, rule=f.RULE, limit=limit)


def generate_for_rule(
    cycle: UUID,
    block: f.Block,
    ctx: f.Context,
    number: int,
    adjacent: tuple[f.Session, ...],
    *,
    rule: f.FamiliarRule,
    limit: int = SEARCH_LIMIT,
) -> tuple[f.Day, ...]:
    """Pure regeneration. Only historical replay selects the earlier dose-only rule."""
    if rule not in ("synthetic.familiar.hold.v1", f.RULE):
        raise ValueError("unknown familiar planner rule")
    if type(number) is not int or not 1 <= number <= len(block.phases):
        raise ValueError("week number outside block")
    validate_baseline(block, ctx, limit, rule)
    return place_week(cycle, block, ctx, number, adjacent, block.templates, limit=limit)


def place_week(
    cycle: UUID,
    block: f.Block,
    ctx: f.Context,
    number: int,
    adjacent: tuple[f.Session, ...],
    templates: tuple[f.Template, ...],
    *,
    limit: int = SEARCH_LIMIT,
) -> tuple[f.Day, ...]:
    """Place a validated prescription vector and test its actual exposure and time endpoints."""
    if not 1 <= number <= len(block.phases):
        raise ValueError("week number outside block")
    _validate_commitments(block, {t.key: t.prescription for t in templates}, limit)
    profile = block.adaptation
    if (
        profile
        and profile.weekly_seconds
        and sum(t.prescription.reserved_seconds for t in templates) > profile.weekly_seconds
    ):
        raise PlacementFailure(
            incomplete=False, examined=0, limit=limit, reasons=("weekly time budget exceeded",)
        )
    ordered = sorted(templates, key=lambda t: (ctx.rank(t.prescription.sport), t.key))
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
            if (
                profile
                and profile.daily_seconds
                and s.prescription.reserved_seconds
                + sum(
                    other.prescription.reserved_seconds for other in selected if other.day == s.day
                )
                > profile.daily_seconds
            ):
                reasons.add("daily time budget exceeded")
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
                for option in _options(
                    cycle,
                    block,
                    ctx,
                    number,
                    f.Template(key=session.template, prescription=session.prescription),
                )
            ):
                raise ValueError("a retained prescription conflicts with current constraints")

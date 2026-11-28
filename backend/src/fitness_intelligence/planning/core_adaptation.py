"""Synthetic J-DEFAULT review of the next week against its approved predecessor."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from . import evidence as e
from . import familiar as f
from . import familiar_outcomes as actual
from .familiar_calendar import PlacementFailure, place_week
from .prescriptions import fixed


def _eligible(t: e.Task) -> bool:
    return {"familiar-dose-input", "progression-review-input"} <= {
        q.purpose for q in t.qualifications if q.eligible
    }


def _fields(t: e.Task) -> dict[str, e.Scalar]:
    return {v.name: v.value for v in t.fields if v.state == "actual"}


def _exercise(p: f.Strength, rule: f.DevelopingGroup) -> f.Exercise:
    return next(
        x for x in p.exercises if (x.movement, x.variation) == (rule.movement, rule.variation)
    )


def _group(p: f.Strength, rule: f.DevelopingGroup) -> f.Group:
    return next(g for g in _exercise(p, rule).groups if g.key == rule.group)


def _change_group(p: f.Strength, rule: f.DevelopingGroup, group: f.Group) -> f.Strength:
    x = _exercise(p, rule)
    updated = x.model_copy(
        update={"groups": tuple(group if g.key == group.key else g for g in x.groups)}
    )
    return p.model_copy(
        update={"exercises": tuple(updated if ex == x else ex for ex in p.exercises)}
    )


def _describe(dose: f.Group | f.Running) -> str:
    if isinstance(dose, f.Running):
        return f"{dose.duration.nominal} elapsed s"
    return ", ".join(f"{s.reps.nominal} × {s.load.nominal} kg" for s in dose.sets)


def _over_cap(row: e.Performance) -> bool:
    """Compare supported effort at the same ordinal or continuous outing only."""
    p = row.manual.prescribed.prescription
    for task in row.tasks:
        values = {v.name: v.value for v in task.fields if v.state in ("actual", "source-only")}
        if isinstance(p, f.Strength) and (item := task.manual_set):
            cap = next(
                g.effort.cap
                for x in p.exercises
                if (x.movement, x.variation) == (item.movement, item.variation)
                for g in x.groups
                if g.key == item.group
            )
            if values.get("set_rpe") is not None and values["set_rpe"] > cap:
                return True
        elif isinstance(p, f.Running):
            if (
                len(p.steps) == 1
                and values.get("session_rpe") is not None
                and values["session_rpe"] > p.steps[0].effort.cap
            ):
                return True
            for i, step in enumerate(p.steps, 1):
                effort = values.get(f"step.{i}.achieved_rpe")
                if effort is not None and effort > step.effort.cap:
                    return True
    return False


def easy_duration_step(nominal: int, maximum: int, initial: int) -> int:
    """Remaining whole seconds under outing, per-review and initial weekly limits."""
    return max(0, min(300, nominal + min(600, nominal // 10) - maximum, initial + 1200 - maximum))


def _manageable_completion(
    p: e.Performance, *, reduced: f.DevelopingGroup | str | None = None
) -> bool:
    """Check completed dose, tolerance, measured effort and sibling work."""
    m = p.manual
    if m is None or p.execution_state != "completed" or p.potential_duplicates or _over_cap(p):
        return False
    plan = m.prescribed.prescription
    report = m.history[-1].actual
    if report.manageable is not True or any(
        not _eligible(t) or _fields(t).get("tolerance") not in (None, "comfortable")
        for t in p.tasks
    ):
        return False
    if isinstance(plan, f.Running):
        if not isinstance(report, actual.RunExecution) or len(p.tasks) != 1:
            return False
        fields = _fields(p.tasks[0])
        seconds = fields.get("elapsed_seconds")
        if (
            seconds is None
            or seconds <= 0
            or (seconds != plan.duration.nominal and reduced != "easy")
        ):
            return False
        if report.differences(m.prescribed) and reduced != "easy":
            return False
        if any(
            step.status != "completed"
            or (
                step.achieved_rpe is not None
                and step.achieved_rpe > plan.steps[step.index - 1].effort.target.high
            )
            for step in report.steps
        ):
            return False
        if (
            len(plan.steps) == 1
            and (effort := fields.get("session_rpe")) is not None
            and effort > plan.steps[0].effort.cap
        ):
            return False
        if plan.role == "easy":
            effort = fields.get("session_rpe")
            return report.conversational is not False and (
                plan.steps[0].effort.target.low <= effort <= plan.steps[0].effort.target.high
                if effort is not None
                else report.conversational is True
            )
        return True
    sets = {t.manual_set.key: _fields(t) for t in p.tasks if t.manual_set}
    for x in plan.exercises:
        for g in x.groups:
            if g.kind != "working":
                continue
            for s in g.sets:
                v = sets.get((x.movement, x.variation, x.equipment, g.key, g.kind, s.ordinal), {})
                if v.get("status") != "completed" or v.get("kg") is None or not v.get("reps"):
                    return False
                effort = v.get("set_rpe")
                if effort is not None and not g.effort.target.low <= effort <= g.effort.target.high:
                    return False
                affected = isinstance(reduced, f.DevelopingGroup) and (
                    x.movement,
                    x.variation,
                    g.key,
                ) == (reduced.movement, reduced.variation, reduced.group)
                if not affected and (v["kg"], v["reps"]) != (s.load.nominal, s.reps.nominal):
                    return False
    return True


@dataclass(frozen=True)
class Option:
    decision: e.CoreDecision
    rule: f.DevelopingGroup | None
    dose: f.Group | f.Running

    def hold(self, reason: str) -> e.CoreDecision:
        d = self.decision
        return d.model_copy(
            update={"action": "hold", "after": d.before, "reason": reason, "considered": d.after}
        )


def _strength_step(
    rule: f.DevelopingGroup,
    p: f.Strength,
    initial: f.Strength,
    successes: list[e.Performance],
    restoration: bool,
) -> tuple[str, str, f.Group]:
    group = _group(p, rule)
    latest = successes[0]
    values = [
        _fields(t).get("set_rpe")
        for t in latest.tasks
        if t.manual_set
        and (t.manual_set.movement, t.manual_set.variation, t.manual_set.group)
        == (rule.movement, rule.variation, rule.group)
    ]
    if (restoration or any(v is None or v >= group.effort.target.high for v in values)) and len(
        successes
    ) < 2:
        return "hold", "two distinct manageable nominal successes required", group
    sets = list(group.sets)
    band = rule.rep_range
    if band:
        for i, s in enumerate(sets):
            if s.reps.nominal < band[1]:
                sets[i] = s.model_copy(
                    update={
                        "reps": fixed(s.reps.nominal + 1),
                        "execution_seconds": rule.set_seconds,
                    }
                )
                return (
                    "reps",
                    "one total rep on the first eligible ordinal",
                    group.model_copy(update={"sets": tuple(sets)}),
                )
    step = _exercise(p, rule).load_step_kg
    rate = Decimal("0.025") if rule.burden == "upper" else Decimal("0.05")
    for s, base in zip(sets, _group(initial, rule).sets, strict=True):
        if step is None or s.load.nominal + step > min(
            s.load.nominal * (1 + rate), base.load.nominal * (1 + 2 * rate)
        ):
            return (
                "hold",
                "smallest equipment step exceeds the predecessor or initial load ceiling",
                group,
            )
    return (
        "load",
        "smallest available load step within both ceilings",
        group.model_copy(
            update={
                "sets": tuple(
                    s.model_copy(
                        update={
                            "load": fixed(s.load.nominal + step),
                            "reps": fixed(band[0]) if band else s.reps,
                            "execution_seconds": rule.set_seconds,
                        }
                    )
                    for s in sets
                )
            }
        ),
    )


def _duration(p: f.Running, seconds: int) -> f.Running:
    return p.model_copy(
        update={"segments": (p.steps[0].model_copy(update={"seconds": fixed(seconds)}),)}
    )


def _resume(
    rule: f.DevelopingGroup | None, p: f.Prescription, row: e.Performance
) -> f.Group | f.Running:
    if not _manageable_completion(row, reduced=rule or "easy"):
        raise ValueError("defer re-entry: need scoped manageable work at a credible dose")
    if isinstance(p, f.Running):
        return _duration(p, min(p.duration.nominal, _fields(row.tasks[0])["elapsed_seconds"]))
    group = _group(p, rule)
    ex = _exercise(p, rule)
    values = {t.manual_set.key: _fields(t) for t in row.tasks if t.manual_set}
    sets = []
    for s in group.sets:
        v = values[ex.movement, ex.variation, ex.equipment, group.key, group.kind, s.ordinal]
        kg = min(s.load.nominal, v["kg"])
        reps = min(s.reps.nominal, v["reps"])
        if (
            (rule.rep_range and reps < rule.rep_range[0])
            or (not rule.rep_range and reps != s.reps.nominal)
        ) or (ex.load_step_kg and kg % ex.load_step_kg):
            raise ValueError(
                "defer re-entry: actual work falls outside the rep envelope or equipment increment"
            )
        sets.append(s.model_copy(update={"load": fixed(kg), "reps": fixed(reps)}))
    return group.model_copy(update={"sets": tuple(sets)})


def review_week(
    cycle: UUID,
    block: f.Block,
    ctx: f.Context,
    request: f.FamiliarWeek,
    predecessor: UUID,
    previous: tuple[f.Day, ...],
    prior_review: e.CoreReview | None,
    adjacent: tuple[f.Session, ...],
    inputs: e.DecisionInputs,
) -> tuple[tuple[f.Day, ...], e.CoreReview]:
    profile = block.adaptation
    assert profile
    sessions = {s.template: s for day in previous for s in day.sessions}
    initial = {t.key: t.prescription for t in block.templates}
    plan = {k: s.prescription for k, s in sessions.items()}
    zone = ZoneInfo(ctx.zone)
    rows = sorted(
        (
            p
            for p in inputs.projection.performances
            if p.manual
            and p.manual.cycle == cycle
            and p.occurred_at <= inputs.cutoff
            and inputs.cutoff - p.occurred_at <= timedelta(days=28)
        ),
        key=lambda p: (p.occurred_at, p.manual.prescribed.occurrence),
        reverse=True,
    )
    current = {p.manual.prescribed.occurrence: p for p in rows if p.manual.origin == predecessor}
    representative = all(
        s.occurrence in current and _manageable_completion(current[s.occurrence])
        for s in sessions.values()
    )
    interrupted = {i.template: i for i in ctx.interruptions}
    rules = [(r.template, r) for r in profile.groups]
    if profile.easy_template:
        rules.append((profile.easy_template, None))
    latest_by_template = {}
    for row in rows:
        if row.manual.history[-1].actual.performed:
            latest_by_template.setdefault(row.manual.prescribed.template, row)
    day = inputs.cutoff.astimezone(zone).date()
    for obs in ctx.observations:
        if (day - obs.day).days > 28 and obs.template not in latest_by_template:
            raise ValueError(
                f"defer {obs.template}: no recent performance supports a numeric repeat"
            )
    for row in latest_by_template.values():
        m = row.manual
        if m.prescribed.template not in interrupted and (
            m.history[-1].actual.manageable is False or _over_cap(row)
        ):
            raise ValueError(f"defer {m.prescribed.template}: adverse tolerance needs a new review")
    if interrupted.keys() - {k for k, _ in rules}:
        raise ValueError("defer interrupted task outside the approved adaptation envelope")
    running = sum(p.duration.high for p in plan.values() if isinstance(p, f.Running))
    nominal = sum(p.duration.nominal for p in plan.values() if isinstance(p, f.Running))
    baseline = sum(p.duration.nominal for p in initial.values() if isinstance(p, f.Running))
    options = []
    for key, rule in rules:
        p = plan[key]
        task = f"{rule.movement}/{rule.variation}/{rule.group}" if rule else "easy"
        before = _group(p, rule) if rule else p
        past = (
            next((d for d in prior_review.decisions if (d.template, d.task) == (key, task)), None)
            if prior_review
            else None
        )
        since_week = past.ceiling_since_week if past else None
        ceiling = since_week is not None
        matching = [r for r in rows if r.manual.prescribed.template == key]
        successes = []
        for r in matching:
            if (
                (since_week and r.manual.week < since_week)
                or r.manual.prescribed.prescription != p
                or not _manageable_completion(r)
            ):
                break
            successes.append(r)
        now = current.get(sessions[key].occurrence)
        used = []
        action, reason, after = (
            "hold",
            "approved predecessor retained; no fresh comparable nominal success",
            before,
        )
        protected = any(
            g.task in (key, p.role, rule.movement if rule else key)
            for g in block.protections
            if g.sport == p.sport
        )
        if i := interrupted.get(key):
            if (
                not matching
                or matching[0].occurred_at.astimezone(zone).date() < i.since
                or matching[0].manual.prescribed.prescription != p
            ):
                raise ValueError(
                    f"defer {key}: no recent attributed work since interruption ({i.reason})"
                )
            used = matching[:1]
            after = _resume(rule, p, used[0])
            if after != before or since_week is None:
                since_week = request.number
            if protected and after != before:
                raise ValueError(f"defer {key}: re-entry conflicts with protected task")
            action, reason, ceiling = (
                "resume",
                f"temporary ceiling after interruption: {i.reason}",
                True,
            )
        elif request.choice == "hold":
            reason = "athlete selected the feasible hold"
        elif rule and rule.burden == "unclassified":
            reason = "clarify movement burden before progression"
        elif protected:
            reason = "retain the approved protected task and comparison protocol"
        elif not representative or interrupted:
            gaps = [
                key
                for key, s in sessions.items()
                if s.occurrence not in current or not _manageable_completion(current[s.occurrence])
            ]
            reason = "hold pending manageable predecessor exposure: " + ", ".join(
                sorted(set(gaps) | interrupted.keys())
            )
        elif now and successes and successes[0] == now:
            used = successes
            followup = rule.followup_template if rule else profile.easy_followup
            subsequent = next(
                (
                    r
                    for r in current.values()
                    if r.occurred_at > now.occurred_at
                    and r.manual.prescribed.template == followup
                    and _manageable_completion(r)
                ),
                None,
            )
            if ceiling and (len(successes) < 2 or not subsequent):
                reason = "re-entry ceiling retained pending two successes and subsequent tolerance"
            elif rule:
                action, reason, after = _strength_step(rule, p, initial[key], successes, ceiling)
            elif len(successes) < 2:
                reason = "two distinct comparable manageable easy outings required"
            else:
                step = easy_duration_step(nominal, running, baseline)
                if step > 0:
                    action, reason, after = (
                        "duration",
                        "easy duration within outing, weekly and cumulative ceilings",
                        _duration(p, p.duration.nominal + step),
                    )
                else:
                    reason = "weekly running duration ceiling reached"
            if ceiling and subsequent and action in ("reps", "load", "duration"):
                used = [*used, subsequent]
        fresh = bool(now and successes and successes[0] == now) or action == "resume"
        anchor_rows = used if action == "resume" else successes if fresh else []
        carry = past is not None and not fresh
        # An unperformed trial may retain its approved allowance only while the original
        # performances still support it. A correction never opens another review budget.
        if carry and (ceiling or before != (_group(initial[key], rule) if rule else initial[key])):
            current_tips = {
                (r.manual.prescribed.occurrence, r.manual.history[-1].id)
                for r in matching
                if _manageable_completion(r, reduced=(rule or "easy") if ceiling else None)
            }
            if (
                not past.anchor_occurrences
                or not set(zip(past.anchor_occurrences, past.anchor_assertions, strict=True))
                <= current_tips
            ):
                raise ValueError(
                    f"defer {key}: current evidence no longer supports the approved trial"
                )
        anchor_revision = past.anchor_revision if carry else predecessor
        anchor_dose = past.anchor_dose if carry else _describe(before)
        decision = e.CoreDecision(
            template=key,
            task=task,
            action=action,
            reason=reason,
            anchor_revision=anchor_revision,
            anchor_dose=anchor_dose,
            anchor_occurrences=past.anchor_occurrences
            if carry
            else tuple(r.manual.prescribed.occurrence for r in anchor_rows),
            anchor_assertions=past.anchor_assertions
            if carry
            else tuple(r.manual.history[-1].id for r in anchor_rows),
            before=_describe(before),
            after=_describe(after),
            performances=tuple(r.manual.prescribed.occurrence for r in used),
            assertions=tuple(r.manual.history[-1].id for r in used),
            ceiling_since_week=since_week,
        )
        options.append(Option(decision, rule, after))

    # A reported late occurrence can constrain spacing across the week boundary.
    actual_neighbors = tuple(
        r.manual.prescribed.model_copy(update={"start_utc": r.occurred_at})
        for r in rows
        if r.manual.history[-1].actual.performed and r.occurred_at != r.manual.prescribed.start_utc
    )

    days, decisions = _place_changes(
        cycle, block, ctx, request, adjacent + actual_neighbors, plan, options
    )
    return days, e.CoreReview(predecessor=predecessor, decisions=decisions)


def _place_changes(
    cycle: UUID,
    block: f.Block,
    ctx: f.Context,
    request: f.FamiliarWeek,
    adjacent: tuple[f.Session, ...],
    plan: dict[str, f.Prescription],
    options: list[Option],
) -> tuple[tuple[f.Day, ...], tuple[e.CoreDecision, ...]]:
    def place(vector: dict[str, f.Prescription]) -> tuple[f.Day, ...]:
        templates = tuple(
            f.Template(key=t.key, prescription=vector[t.key]) for t in block.templates
        )
        return place_week(cycle, block, ctx, request.number, adjacent, templates)

    def apply(vector: dict[str, f.Prescription], o: Option) -> dict[str, f.Prescription]:
        k = o.decision.template
        return vector | {k: _change_group(vector[k], o.rule, o.dose) if o.rule else o.dose}

    # Re-entry reductions and existing ceilings are binding even when the athlete requests a hold.
    for o in options:
        if o.decision.action == "resume":
            plan = apply(plan, o)
    positive = [o for o in options if o.decision.action in ("reps", "load", "duration")]

    def compose(
        first: str, allowed: list[Option]
    ) -> tuple[tuple[f.Day, ...], dict[tuple[str, str], e.CoreDecision]]:
        vector = plan
        days = place(vector)
        decisions = {(o.decision.template, o.decision.task): o.decision for o in options}
        lower = running_rise = False

        def rank(o: Option) -> tuple[int, bool]:
            sport = "strength" if o.rule else "running"
            return ctx.rank(sport), sport != first

        for o in sorted(allowed, key=rank):
            d = o.decision
            is_lower = o.rule is not None and o.rule.burden == "lower"
            if (is_lower and (lower or running_rise)) or (o.rule is None and lower):
                d = o.hold("J-DEFAULT: retain the selected feasible change")
            else:
                trial = apply(vector, o)
                try:
                    placed = place(trial)
                except PlacementFailure as exc:
                    d = o.hold(str(exc))
                else:
                    days, vector = placed, trial
                    lower |= is_lower
                    running_rise |= o.rule is None
                    if d.reentry:
                        d = d.model_copy(
                            update={
                                "ceiling_since_week": None,
                                "reason": "reviewed restoration from reduced predecessor; "
                                + d.reason,
                            }
                        )
            decisions[d.template, d.task] = d
        return days, decisions

    days, decisions = compose(request.choice or "strength", positive)
    if (
        ctx.emphasis == "balanced"
        and request.choice is None
        and any(o.rule is None for o in positive)
    ):
        _, other = compose("running", positive)
        disputed = {key for key, d in decisions.items() if d.action != other[key].action}
        if disputed:
            shared = [
                o
                for o in positive
                if (o.decision.template, o.decision.task) not in disputed
                and decisions[o.decision.template, o.decision.task].action != "hold"
            ]
            days, _ = compose("strength", shared)
            for o in positive:
                key = o.decision.template, o.decision.task
                if key in disputed:
                    decisions[key] = o.hold(
                        "J-DEFAULT: equal priorities; choose strength, running or hold"
                    )
    return days, tuple(decisions.values())

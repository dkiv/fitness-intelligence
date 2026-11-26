"""Reconcile exact current claims at a set or outing. Never group performances by similarity."""

from collections import Counter, defaultdict
from uuid import UUID
from zoneinfo import ZoneInfo

from ..analytics.exposure import Outing
from ..analytics.references import known_context
from ..analytics.strength import StrengthFact
from . import confirmation as c
from . import evidence as e
from . import familiar as f
from . import familiar_outcomes as actual


def identity(member: e.NativeMember) -> UUID | None:
    fact = member.fact
    return fact.row.set_id if isinstance(fact, StrengthFact) else fact.workout_id


def set_key(display: c.StrengthFact) -> tuple:
    return (
        display.movement,
        display.variation,
        display.equipment,
        display.group,
        display.kind,
        display.ordinal,
    )


def _strength_dimensions(
    task: c.StrengthFact | actual.SetExecution, convention: f.LoadConvention
) -> set[str]:
    labels = {
        "movement": task.movement,
        "variation": task.variation,
        "equipment": task.equipment,
        "load-convention": convention,
        "group": task.group,
    }
    # Both contracts require a positive ordinal.
    return {"ordinal"} | {name for name, value in labels.items() if known_context(value)}


def _task(
    sport: str,
    member: e.NativeMember | None,
    support: c.Support | None,
    manual: e.Manual | None,
    item: actual.SetExecution | None,
    blockers: tuple[str, ...],
) -> e.Task:
    claims: dict[str, list[e.Claim]] = defaultdict(list)

    def add(name: str, value: e.Scalar | None, tier: e.Tier, source: UUID) -> None:
        if value is not None:
            claims[name].append(e.Claim(name=name, value=value, tier=tier, support=source))

    mapped = member.display if member else None
    dimensions = set()
    if mapped:
        if known_context(mapped.comparison) and known_context(member.context.basis):
            dimensions.add("comparison-context")
        if isinstance(mapped, c.StrengthFact):
            dimensions.update(_strength_dimensions(mapped, mapped.load_convention))
        elif known_context(mapped.role):
            dimensions.add("running-role")
    interval = False
    interval_indices: tuple[int, ...] = ()
    if member:
        fact = member.fact
        ref = fact.reference_id
        if isinstance(fact, StrengthFact):
            row = fact.row
            if fact.execution in ("confirmed", "inferred"):
                add(
                    "status",
                    "completed",
                    "provider-inferred" if fact.execution == "inferred" else "provider-reported",
                    ref,
                )
            for name, value in (
                ("reps", row.repetitions),
                ("kg", row.weight_kg),
                ("set_rpe", row.rpe),
            ):
                add(name, value, "provider-reported", ref)
        else:
            # A retained activity establishes an outing summary, not completed instructions.
            add("outing", True, "provider-reported", ref)
            for name, value in (
                ("elapsed_seconds", fact.elapsed_s),
                ("moving_seconds", fact.moving_s),
                ("activity_seconds", fact.duration_s),
                ("distance_metres", fact.distance_m),
                ("average_speed_mps", fact.average_speed_mps),
            ):
                add(name, value, "provider-reported", ref)
            interval = (
                isinstance(member.context, e.RunContext) and member.context.structure == "intervals"
            )
            if fact.activity_issues:
                blockers += ("unresolved activity reconciliation",)
    if support and support.state == "confirmed" and mapped:
        tip = support.history[-1]
        for name, value in support.confirmed.items():
            if name == "completion":
                add("status", "completed", "confirmed-display", tip.command)
            else:
                add(name, value, "confirmed-display", tip.command)
        if support.independent_report:
            for name, value in support.independent_report:
                add(name, value, "athlete-actual", tip.command)
    if support and support.state in ("excluded", "uncertain", "withdrawn", "stale"):
        blockers += (f"confirmation {support.state}",)
    if support and support.ambiguous_set_link:
        blockers += ("ambiguous prescribed ordinal",)
    if manual:
        tip = manual.history[-1]
        report = tip.actual
        add("session_status", report.status, "manual-actual", tip.id)
        add("session_manageable", report.manageable, "manual-actual", tip.id)
        add("session_feedback", report.feedback, "manual-actual", tip.id)
        if item:
            dimensions.add("comparison-context")  # Explicit ordinal of the approved task.
            add("status", item.status, "manual-actual", tip.id)
            add("reps", item.reps, "manual-actual", tip.id)
            add("set_rpe", item.achieved_rpe, "manual-actual", tip.id)
            prescribed = manual.prescribed.prescription
            assert isinstance(prescribed, f.Strength)
            exercise = next(
                x for x in prescribed.exercises if (x.movement, x.variation) == item.key[:2]
            )
            dimensions.update(_strength_dimensions(item, exercise.load_convention))
            if item.kg is not None and item.load_convention != exercise.load_convention:
                blockers += ("reported load convention differs from prescription",)
                add(f"kg.{item.load_convention}", item.kg, "manual-actual", tip.id)
            else:
                add("kg", item.kg, "manual-actual", tip.id)
        elif isinstance(report, actual.RunExecution):
            dimensions.add("comparison-context")
            if known_context(report.role):
                dimensions.add("running-role")
            add("outing", report.confirmed_outing, "manual-actual", tip.id)
            for name in (
                "elapsed_seconds",
                "moving_seconds",
                "distance_metres",
                "completed_work_repetitions",
                "session_rpe",
            ):
                add(name, getattr(report, name), "manual-actual", tip.id)
            prescribed = manual.prescribed.prescription
            assert isinstance(prescribed, f.Running)
            interval_indices = tuple(
                i for i, s in enumerate(prescribed.steps, 1) if s.purpose == "work"
            )
            interval |= len(interval_indices) > 1 or any(
                s.purpose == "recovery" for s in prescribed.steps
            )
            for step in report.steps:
                for name in ("status", "elapsed_seconds", "achieved_rpe"):
                    add(f"step.{step.index}.{name}", getattr(step, name), "manual-actual", tip.id)

    strength = sport == "strength"
    execution_field = "status" if strength else "outing"
    dose = ("reps", "kg") if strength else ("elapsed_seconds",)
    effort = "set_rpe" if strength else "session_rpe"
    names = sorted(
        set(claims)
        | set(dose)
        | {execution_field, effort, "tolerance", "session_manageable"}
        | (set() if strength else {"completed_work_repetitions"})
    )
    fields = {name: e.resolve(name, tuple(claims[name])) for name in names}
    withheld = None
    if member and member.pending_deletion:
        withheld = "pending source deletion"
        blockers += (withheld,)
    elif member and isinstance(member.fact, Outing) and member.fact.activity_issues:
        withheld = "open activity reconciliation issue"
    if withheld:
        for name, value in tuple(fields.items()):
            if value.state == "source-only":
                fields[name] = value.model_copy(
                    update={
                        "state": "withheld",
                        "value": None,
                        "reason": withheld,
                    }
                )
    return e.Task(
        sport=sport,
        member=identity(member) if member else None,
        manual_set=item,
        fields=tuple(fields.values()),
        qualifications=_qualifications(
            sport,
            fields,
            blockers,
            dimensions,
            interval,
            interval_indices,
            manual,
            member,
            item is not None,
        ),
    )


def _qualifications(
    sport: str,
    fields: dict[str, e.FieldEvidence],
    blockers: tuple[str, ...],
    dimensions: set[str],
    interval: bool,
    interval_indices: tuple[int, ...],
    manual: e.Manual | None,
    member: e.NativeMember | None,
    manual_set: bool,
) -> tuple[e.Qualification, ...]:
    strength = sport == "strength"
    execution_field = "status" if strength else "outing"
    dose = ("reps", "kg") if strength else ("elapsed_seconds",)
    effort = "set_rpe" if strength else "session_rpe"
    available = {name for name, field in fields.items() if field.state == "actual"}
    observed = fields[execution_field]
    performed = observed.value in ("completed", "partial", True)
    if performed and (
        observed.state == "actual"
        or any(claim.tier == "provider-reported" for claim in observed.claims)
    ):
        # A provider completion timestamp or retained outing is source evidence of execution.
        available.add("execution")
    available.update(dimensions)
    if fields["session_manageable"].value is True:
        available.add("confirmed-manageable")
    if fields["session_manageable"].state == "actual" or fields["tolerance"].state == "actual":
        available.add("tolerance-report")
    if (strength and observed.value == "completed") or (
        not strength and performed and manual and manual.history[-1].actual.status == "completed"
    ):
        available.add("complete-task")
    if performed and manual_set:
        available.add("performed-set")
    if member or (manual and manual.history[-1].actual.performed):
        available.add("recorded")
    interval_required: tuple[str, ...] = ()
    if interval:
        interval_required = ("completed_work_repetitions", "aligned-work-durations")
        timed = sum(
            1
            for i in interval_indices
            if (status := fields.get(f"step.{i}.status"))
            and status.value == "completed"
            and f"step.{i}.elapsed_seconds" in available
        )
        count = fields["completed_work_repetitions"].value
        if interval_indices and timed == len(interval_indices) and timed == count:
            available.add("aligned-work-durations")
        if isinstance(count, int) and timed < count:
            blockers += (
                f"{timed} of {count} reported work repetitions have aligned achieved durations",
            )

    conflicts = tuple(
        f"contradictory {name}" for name, field in fields.items() if field.state == "conflict"
    )

    def qualification(
        purpose: str,
        required: tuple[str, ...],
        optional: tuple[str, ...],
        exclusions: tuple[str, ...],
    ) -> e.Qualification:
        return e.Qualification(
            purpose=purpose,
            required=required,
            optional=optional,
            missing=tuple(k for k in required if k not in available),
            exclusions=exclusions,
        )

    required_dimensions = (
        ("movement", "variation", "equipment", "load-convention", "group", "ordinal")
        if strength
        else ("running-role",)
    )
    base = ("execution", "comparison-context", *required_dimensions, *dose, *interval_required)
    # A disputed listing can undermine an import-only outing claim. Independently
    # supported execution stays available under its own receipt or manual assertion.
    disputed = member.activity_discrepancies if member and observed.state == "source-only" else ()
    scoped = tuple(dict.fromkeys(blockers + conflicts + disputed))
    return (
        qualification(
            "descriptive-exposure", ("performed-set",) if manual_set else ("recorded",), dose, ()
        ),
        qualification(
            "confirmed-execution",
            ("execution",),
            (effort,),
            tuple(
                b
                for b in scoped
                if b
                in (
                    "unresolved activity reconciliation",
                    "contradictory status",
                    "contradictory outing",
                )
                or b in disputed
                or "duplicate" in b
            ),
        ),
        qualification(
            "comparable-strength" if strength else "comparable-running", base, (effort,), scoped
        ),
        qualification(
            "familiar-dose-input",
            (*base, "complete-task", "confirmed-manageable"),
            (effort,),
            scoped,
        ),
        qualification(
            "progression-review-input",
            (*base, "tolerance-report"),
            (effort,),
            scoped,
        ),
    )


def reconcile(
    members: tuple[e.NativeMember, ...],
    supports: dict[tuple[UUID, UUID], c.Support],
    manuals: tuple[e.Manual, ...],
    zone: ZoneInfo,
) -> tuple[e.Performance, ...]:
    groups: dict[UUID, list[e.NativeMember]] = defaultdict(list)
    for member in members:
        fact = member.fact
        workout = fact.row.workout_id if isinstance(fact, StrengthFact) else fact.workout_id
        groups[workout].append(member)
    by_id = {m.history[-1].id: m for m in manuals}
    claims = {}
    for workout, rows in groups.items():
        targets = {
            s.effective_link.outcome
            for row in rows
            if (s := supports.get((row.fact.source.source_account_id, identity(row))))
            and s.effective_link
        }
        claims[workout] = targets
    multiplicity = Counter(target for targets in claims.values() for target in targets)
    linked = {
        w: by_id[target]
        for w, targets in claims.items()
        for target in targets
        if len(targets) == 1 and multiplicity[target] == 1
    }
    used = {m.history[-1].id for m in linked.values()}
    bundles = [(w, tuple(rows), linked.get(w)) for w, rows in groups.items()]
    bundles.extend((None, (), m) for m in manuals if m.history[-1].id not in used)
    # Flag an unlinked manual and candidate import on the same sport/day for review.
    # Keep both identities. No chronological heuristic merges them.
    pending: dict[tuple, list[tuple[UUID, bool]]] = defaultdict(list)
    specs = []
    for workout, rows, manual in bundles:
        if manual:
            tip = manual.history[-1]
            instant, sport = tip.occurred_at, tip.actual.sport
        else:
            fact = rows[0].fact
            instant, sport = (
                (fact.row.started_at, "strength")
                if isinstance(fact, StrengthFact)
                else (fact.started_at, fact.sport)
            )
        key = (instant.astimezone(zone).date(), sport)
        ident = workout or manual.history[-1].id
        if not (workout and manual) and (not manual or manual.history[-1].actual.performed):
            pending[key].append((ident, workout is not None))
        specs.append((workout, rows, manual, instant, sport, key))
    result = []
    for workout, rows, manual, instant, sport, key in specs:
        duplicates = (
            tuple(sorted(i for i, is_import in pending[key] if is_import != (workout is not None)))
            if not (manual and workout) and (not manual or manual.history[-1].actual.performed)
            else ()
        )
        blockers = ("unresolved potential duplicate",) if duplicates else ()
        if workout and claims[workout] and not manual:
            blockers += ("conflicting explicit attribution",)
        tasks = []
        report = manual.history[-1].actual if manual else None
        manual_sets = (
            {s.key: s for s in report.sets} if isinstance(report, actual.StrengthExecution) else {}
        )
        matched = set()
        for row in rows:
            support = supports.get((row.fact.source.source_account_id, identity(row)))
            link = support.effective_link if support else None
            ordinal = set_key(row.display) if isinstance(row.display, c.StrengthFact) else None
            item = manual_sets.get(ordinal) if link else None
            if item:
                matched.add(item.key)
            reasons = blockers
            if ordinal in manual_sets and not link:
                reasons += ("unresolved set attribution",)
            tasks.append(_task(sport, row, support, manual if link else None, item, reasons))
        for ordinal, item in manual_sets.items():
            if ordinal not in matched:
                ambiguous = any(
                    isinstance(row.display, c.StrengthFact) and set_key(row.display) == ordinal
                    for row in rows
                )
                tasks.append(
                    _task(
                        sport,
                        None,
                        None,
                        manual,
                        item,
                        blockers + (("unresolved set attribution",) if ambiguous else ()),
                    )
                )
        if not tasks:
            tasks.append(_task(sport, None, None, manual, None, blockers))
        if report:
            state = report.status
        elif sport == "strength":
            levels = {m.fact.execution for m in rows if not m.pending_deletion}
            state = (
                "recorded"
                if "confirmed" in levels
                else "inferred"
                if "inferred" in levels
                else "unknown"
            )
            if any(
                (support := supports.get((m.fact.source.source_account_id, identity(m))))
                and support.state == "confirmed"
                and support.confirmed.get("completion")
                for m in rows
            ):
                state = "recorded"
        else:
            state = "recorded" if not rows[0].fact.activity_issues else "unknown"
        result.append(
            e.Performance(
                execution_state=state,
                workout=workout,
                manual=manual,
                occurred_at=instant,
                sport=sport,
                members=rows,
                tasks=tuple(tasks),
                potential_duplicates=duplicates,
            )
        )
    return tuple(
        sorted(result, key=lambda p: (p.occurred_at, p.workout or p.manual.history[-1].id))
    )

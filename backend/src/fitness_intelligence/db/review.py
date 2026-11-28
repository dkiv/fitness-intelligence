"""Deterministic manual review of a sealed E1 prescription and E3 rationale."""

from zoneinfo import ZoneInfo

from fitness_intelligence.evidence.retrieval import Evidence
from fitness_intelligence.planning import evidence as pe
from fitness_intelligence.planning import familiar
from fitness_intelligence.planning.outcomes import WeeklyOutcomes
from fitness_intelligence.planning.planner import Session, Slot, WeekPlan
from fitness_intelligence.planning.prescriptions import Intervals, RunStep, StrengthSession, Target
from fitness_intelligence.planning.rationale import Rationale

from .plan_commands import FamiliarPreview, Preview


def _target(t: Target) -> str:
    return str(t.nominal) if t.low == t.high else f"{t.nominal} [{t.low}–{t.high}]"


def _step(step: RunStep) -> str:
    return f"{step.purpose} {_target(step.seconds)} s at RPE {_target(step.rpe)}"


def _session(s: Session) -> str:
    p = s.prescription
    if isinstance(p, StrengthSession):
        groups = [
            f"{e.equipment} {e.movement} {g.kind} {g.count} × {_target(g.reps)} at "
            f"{_target(g.external_kg)} kg, "
            + (f"RPE ≤ {g.max_rpe}" if g.max_rpe is not None else str(g.effort_cue))
            + (f", rest ≤ {g.max_rest_seconds} s" if g.max_rest_seconds is not None else "")
            for e in p.exercises
            for g in e.groups
        ]
        detail = ", ".join(groups)
    else:
        detail = ", ".join(
            (f"{seg.repeats} × (" + ", ".join(_step(step) for step in seg.steps) + ")")
            if isinstance(seg, Intervals)
            else _step(seg)
            for seg in p.segments
        )
    return f"{s.day} {s.start:%H:%M} {s.slot} · {detail}"


def _evidence(e: Evidence) -> list[str]:
    lines = [
        f"{e.claim.key} ({e.applicability}) · {e.claim.assertion}",
        f"Limits · {e.claim.limitations} {' '.join(e.reasons)}".rstrip(),
    ]
    for c in e.citations:
        lines.append(f"{c.support.source} · {c.citation} · {c.support.locator} · {c.record_url}")
    return lines


def _observations(prior: WeekPlan, outcomes: WeeklyOutcomes) -> list[str]:
    lines = []
    lines += [f"Week 1 prescription and athlete observations through {outcomes.as_of.isoformat()}"]
    for o in outcomes.slots:
        session = prior.session(o.slot)
        lines.append(_session(session))
        if not o.actual:
            lines.append("  Unknown · no attributed report" if o.elapsed else "  Upcoming")
            continue
        if o.prescribed is not None and o.prescribed != session:
            session = o.prescribed
            lines.append("  Prescription in force at execution · " + _session(session))
        a = o.actual
        lines.append(
            f"  Athlete report · {o.status} · "
            f"{'scheduled' if a.status in ('missed', 'unknown') else 'executed'} "
            f"{o.occurred_at.isoformat()} · "
            f"recorded {o.recorded_at.isoformat()} · prescription {o.revision_id}"
        )
        actual_start = o.occurred_at.astimezone(prior.inputs.availability.zone)
        if actual_start.date() != session.day or actual_start.time() != session.start:
            lines.append(f"  Timing deviation · athlete reported {actual_start.isoformat()}")
        if o.supersedes_id:
            lines.append(f"  Correction of observation {o.supersedes_id}")
        if not o.supported:
            lines.append("  Linked workout no longer supports this observation.")
        if isinstance(session.prescription, StrengthSession):
            lines.append(
                f"  Confirmed working sets {len(a.working_sets)}, inferred {a.inferred_sets}, "
                f"manageable {a.manageable if a.manageable is not None else 'unknown'}"
            )
            for s in a.working_sets:
                lines.append(
                    f"  Set {s.ordinal} · RPE {s.rpe if s.rpe is not None else 'unknown'}, "
                    f"reps {s.reps if s.reps is not None else 'unknown'}, "
                    f"kg {s.external_kg if s.external_kg is not None else 'unknown'}"
                )
        if a.run_seconds is not None or a.run_rpe is not None:
            lines.append(
                f"  Run · {a.run_seconds or 'unknown'} s, "
                f"RPE {a.run_rpe if a.run_rpe is not None else 'unknown'}"
            )
        if a.feedback:
            lines.append(f"  Feedback · {a.feedback}")
        lines.extend(f"  Deviation · {d}" for d in o.deviations(session))
    counts = outcomes.counts()
    known, total = outcomes.known_coverage
    completed, _ = outcomes.completion_among_known
    lines += [
        f"{len(outcomes.slots)} planned, {total} elapsed · "
        + ", ".join(f"{v} {k}" for k, v in counts.items()),
        f"Known coverage {known}/{total} · completion among known "
        + (f"{completed}/{known}" if known else "N/A (0 known)"),
    ]
    return lines


def _science(why: Rationale, alerts: tuple[str, ...]) -> list[str]:
    lines = []
    selection = why.selection
    lines += [
        f"Reviewed scientific evidence · {selection.release_id} · SHA-256 {selection.digest}",
        f"{why.eligible_claim_count} eligible reviewed claims in this release.",
        f"{selection.algorithm} · {selection.query.model_dump_json()}",
    ]
    for method in why.programming_options:
        lines.append(
            f"Programming option · {method.key} · {method.description} "
            f"{method.provenance}. {method.tradeoffs}"
        )
    for m in selection.matches:
        lines.extend(_evidence(m.evidence))
        for related in m.related:
            lines.append(f"{related.relation.kind} · {related.relation.reason}")
            lines.extend(_evidence(related.evidence))
    lines.extend(f"Evidence gap · {gap}" for gap in selection.gaps)
    lines.extend(f"Current evidence alert · {msg}" for msg in alerts)
    return lines


def _familiar_session(p: familiar.Prescription) -> list[str]:
    lines = [f"{p.role} · prepare {p.preparation_seconds}s · reserve {p.reserved_seconds}s"]
    if isinstance(p, familiar.Strength):
        for exercise in p.exercises:
            lines.append(
                f"{exercise.movement}/{exercise.variation} ({exercise.equipment}, "
                f"{exercise.load_convention}) · transition {exercise.transition_seconds}s"
            )
            for group in exercise.groups:
                lines.append(
                    f"{group.key} ({group.kind}) · set RPE {_target(group.effort.target)}, "
                    f"cap {group.effort.cap}"
                )
                for target in group.sets:
                    lines.append(
                        f"  {target.ordinal}. {_target(target.reps)} reps at "
                        f"{_target(target.load)} kg · allow {target.execution_seconds}s, "
                        f"rest after {target.rest_after_seconds}s"
                    )
            if exercise.notes:
                lines.append(exercise.notes)
    else:
        lines.append(f"Elapsed duration {_target(p.duration)}s")
        for index, step in enumerate(p.steps, 1):
            lines.append(
                f"  {index}. {step.purpose} {_target(step.seconds)}s · "
                f"step RPE {_target(step.effort.target)}, cap {step.effort.cap}"
            )
    if p.notes:
        lines.append(p.notes)
    return lines


def _familiar_review(preview: FamiliarPreview) -> str:
    ctx, block, candidate = preview.sealed_context, preview.block, preview.candidate
    state = preview.decision.choice if preview.decision else "proposed"
    lines = [
        f"Synthetic research preview · {state} · revision {preview.revision_id}",
        f"{ctx.emphasis} · {block.key} · {ctx.zone} · starts {block.start}",
        f"Rule {candidate.rules} · confirmed support {', '.join(candidate.supports)}",
    ]
    if isinstance(candidate, pe.ReviewedCandidate):
        inputs = candidate.decision_inputs
        scope = inputs.projection.scope
        lines.append(
            f"Evidence reviewed at {inputs.cutoff.isoformat()} · {inputs.policy} · "
            f"{scope.start} to {scope.stop} (exclusive), {scope.zone}"
        )
        lines.append(
            f"{len(inputs.projection.performances)} performance records · "
            f"{len(inputs.projection.confirmations)} member confirmations · "
            f"{sum(len(d.open_issues) for d in inputs.projection.days)} open issues"
        )
        for day in inputs.projection.days:
            running = day.activities.status if day.activities else "unselected"
            issues = ", ".join(i.issue.reason for i in day.open_issues) or "none"
            lines.append(f"{day.day} · activity acquisition {running} · open issues {issues}")
        for performance in inputs.projection.performances:
            lines.append(
                f"{performance.occurred_at.isoformat()} · {performance.sport} · "
                f"{performance.execution_state}"
            )
    if preview.current_context_id != preview.context_id:
        lines.append("The planning context has changed since this proposal.")
    for objective in sorted(ctx.objectives, key=lambda obj: obj.rank):
        lines.append(f"Priority {objective.rank} · {objective.sport} · {objective.outcome}")
    for goal in block.protections:
        lines.append(f"Protect {goal.task} · {goal.desired_direction} · {goal.protocol}")
    for floor in block.commitments:
        unit = "working sets" if floor.sport == "strength" else "elapsed seconds"
        lines.append(
            f"Preserve {floor.sessions} × {floor.role}, each ≥ {floor.minimum_per_session} {unit}"
        )
    if isinstance(candidate.request, familiar.ProposeBlock):
        for n, phase in enumerate(block.phases, 1):
            lines.append(f"Week {n} intent · {phase}")
        for template in block.templates:
            lines.append(f"Familiar template · {template.key}")
            lines.extend(_familiar_session(template.prescription))
    else:
        n = candidate.request.number
        lines.append(
            f"Week {n} · {block.phases[n - 1]} · approved block {candidate.block_revision}"
        )
        for day in candidate.days:
            lines.append(str(day.day) if day.sessions else f"{day.day} · no prescribed sessions")
            for session in day.sessions:
                local = session.start_utc.astimezone(ZoneInfo(ctx.zone))
                lines.append(f"{local:%H:%M %z} · {session.template} · {session.occurrence}")
                lines.extend(_familiar_session(session.prescription))
    return "\n".join(lines)


def render_review(preview: Preview | FamiliarPreview) -> str:
    if isinstance(preview, FamiliarPreview):
        return _familiar_review(preview)
    week = preview.candidate.week
    prior = week.inputs.previous
    block = week.inputs.block
    why = preview.rationale
    lines = [
        f"{block.version} · {block.objective}",
        f"Planning zone · {week.inputs.availability.zone}",
    ]
    if prior and why and why.outcomes:
        lines.extend(_observations(prior, why.outcomes))
    lines.append(
        f"Week {week.inputs.number} prescription · {week.press_sets} press working sets, "
        f"{week.running_seconds // 60} min running"
    )
    for day in week.days:
        lines.extend([_session(s) for s in day.sessions] or [f"{day.day} · rest"])
    if prior:
        lines.append(
            f"Week 1 → 2 · press {prior.press_sets} → {week.press_sets} sets, "
            f"runs {prior.running_seconds // 60} → {week.running_seconds // 60} min"
        )
        for slot in Slot:
            before, after = prior.session(slot), week.session(slot)
            if before.prescription != after.prescription:
                lines += ["  " + _session(before), "  → " + _session(after)]
    lines.append("Calendar changes against approved base")
    for change in preview.changes:
        before = _session(change.before) if change.before else "unscheduled"
        after = _session(change.after) if change.after else "unscheduled"
        lines.append(f"  {before} → {after}")
    lines += [
        f"Applied programming rules · {week.rule_version}",
        "Set increments, effort caps and recovery spacing are synthetic fixture parameters. "
        "Their numerical values have no scientific validation in this cycle.",
    ]
    for f in week.explanation:
        facts = ", ".join(f"{k}={v if v is not None else 'unknown'}" for k, v in f.facts)
        lines.append(f"  {f.rule} {' '.join(f.slots)} · {facts}")
    if prior and week.inputs.review:
        review = week.inputs.review
        for slot, exp in (
            (Slot.FIRST_PRESS, review.first_press),
            (Slot.SECOND_PRESS, review.second_press),
        ):
            required = prior.session(slot).prescription.working_sets
            if exp.completed is not True:
                lines.append(
                    f"{slot} · full prescribed exposure unconfirmed or a deviation reported."
                )
            if len(exp.confirmed_rpes) != required or None in exp.confirmed_rpes:
                lines.append(f"{slot} · missing confirmed sets or measured effort.")
            if exp.inferred_sets:
                lines.append(f"{slot} · inferred sets prevent progression.")
            if any(r is not None and r > block.max_rpe for r in exp.confirmed_rpes):
                lines.append(f"{slot} · measured effort exceeded the fixture cap.")
        if review.both_manageable is not True:
            lines.append("Positive manageability feedback is required for both press sessions.")
        if week.press_sets > prior.press_sets:
            lines.append(
                "Both prescribed press exposures were confirmed within the effort cap "
                "and reported manageable. The fixture adds one Thursday working set."
            )
        elif week.press_sets == prior.press_sets:
            lines.append("The proposal retains the prior weekly press set count.")
    if why:
        lines.extend(_science(why, preview.evidence_alerts))
    else:
        lines.append("Historical E2 proposal · no verified scientific selection recorded.")
    if preview.context_id != preview.current_context_id:
        a = preview.current_context.availability
        lines.append("Planning context changed. Review current restrictions and availability.")
        for d in week.days:
            for s in d.sessions:
                if isinstance(s.prescription, StrengthSession):
                    for ex in s.prescription.exercises:
                        if ex.movement in a.excluded_movements or ex.equipment not in a.equipment:
                            lines.append(
                                f"Current movement conflict · {s.slot} · "
                                f"{ex.movement} requires {ex.equipment}"
                            )
                window = a.window(d.day)
                if (
                    window is None
                    or window.start != s.start
                    or window.discipline
                    != ("strength" if isinstance(s.prescription, StrengthSession) else "running")
                    or window.minutes * 60 < s.prescription.reserved_seconds
                ):
                    lines.append(f"Current availability conflict · {s.slot} on {s.day}")
        lines.append(
            f"Excluded movements · {', '.join(sorted(a.excluded_movements)) or 'none'}. "
            f"Available equipment · {', '.join(sorted(a.equipment)) or 'none'}."
        )
    if preview.decision:
        lines.append(f"Athlete decision · {preview.decision.choice}")
    else:
        lines.append(
            f"Athlete decision pending · approve or decline revision {preview.revision_id} "
            f"against base {preview.base_id}."
        )
    return "\n".join(lines)

"""V2 wire contract and replay of synthetic block / familiar-week requests."""

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from ..planning import evidence as e
from ..planning import familiar as f
from ..planning.core_adaptation import review_week
from ..planning.familiar_calendar import SEARCH_LIMIT, generate_for_rule, validate_baseline
from .plan_snapshot import InvalidSnapshot, canonical

# Dedicated fixture principal. Trusted process owner binding is still required for every command.
PREVIEW_OWNER = UUID("c13399d0-4e41-50ef-b9e4-25fff100dadd")


def require_preview_owner(owner: UUID) -> None:
    if owner != PREVIEW_OWNER:
        raise PermissionError("generalized operational planning has no authorized rules")


def snapshot(value: f.Record) -> dict[str, Any]:
    return {"schema_version": 2, "data": value.model_dump(mode="json")}


def read[T: f.Record](model: type[T], raw: dict[str, Any]) -> T:
    try:
        value = model.model_validate_json(canonical(raw["data"]))
        if canonical(raw) != canonical(snapshot(value)):
            raise ValueError("noncanonical v2 payload")
    except (KeyError, ValueError, ArithmeticError, TypeError) as exc:
        raise InvalidSnapshot("invalid generalized planning snapshot") from exc
    return value


def read_candidate(raw: dict[str, Any]) -> f.Candidate:
    if isinstance(raw.get("data"), dict) and "decision_inputs" in raw["data"]:
        return read(e.ReviewedCandidate, raw)
    return read(f.Candidate, raw)


def with_inputs(candidate: f.Candidate, inputs: e.DecisionInputs) -> e.ReviewedCandidate:
    return e.ReviewedCandidate.model_validate_json(
        canonical(
            candidate.model_dump(mode="json") | {"decision_inputs": inputs.model_dump(mode="json")}
        )
    )


@dataclass(frozen=True)
class ApprovedWeek:
    ref: f.WeekRef
    days: tuple[f.Day, ...]
    review: e.CoreReview | None = None


def build(
    cycle: UUID,
    block: f.Block,
    ctx: f.Context,
    request: f.ProposeBlock | f.FamiliarWeek,
    block_revision: UUID | None,
    weeks: tuple[ApprovedWeek, ...],
    *,
    rule: f.FamiliarRule,
    inputs: e.DecisionInputs | None = None,
) -> f.Candidate:
    review = None
    if ctx.interruptions and not (block.adaptation and weeks):
        raise ValueError("defer interrupted baseline until reviewed re-entry is possible")
    if isinstance(request, f.ProposeBlock):
        if block_revision is not None or weeks:
            raise ValueError("block revisions and successor blocks are unsupported")
        generate_for_rule(
            cycle, block, ctx, 1, (), rule=rule
        )  # Do not propose an unusable initial contract.
        days = ()
    elif isinstance(request, f.FamiliarWeek):
        if block_revision is None or request.number != len(weeks) + 1:
            raise ValueError("approve the block, then detail consecutive new weeks")
        neighbors = tuple(s for week in weeks for day in week.days for s in day.sessions)
        if block.adaptation and weeks:
            validate_baseline(block, ctx, SEARCH_LIMIT, rule)
            if inputs is None:
                raise ValueError("adaptive week requires frozen planning evidence")
            days, review = review_week(
                cycle,
                block,
                ctx,
                request,
                weeks[-1].ref.revision,
                weeks[-1].days,
                weeks[-1].review,
                neighbors,
                inputs,
            )
        else:
            if request.choice:
                raise ValueError("review choice requires an adaptive predecessor week")
            days = generate_for_rule(cycle, block, ctx, request.number, neighbors, rule=rule)
    else:
        raise ValueError("unsupported generalized planning request")
    candidate = f.Candidate(
        rules=rule,
        request=request,
        cycle=cycle,
        block_key=block.key,
        block_revision=block_revision,
        prior_weeks=tuple(w.ref for w in weeks),
        days=days,
        supports=tuple(sorted(o.support for o in ctx.observations)),
    )
    if inputs is not None:
        return with_inputs(candidate, inputs).model_copy(update={"adaptation": review})
    return candidate


def check_dates(candidate: f.Candidate, block: f.Block, today: date) -> None:
    first = candidate.days[0].day if candidate.days else block.start
    if first <= today:
        raise ValueError("cannot approve or generate a block/week whose local day has started")

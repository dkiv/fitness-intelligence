"""V2 wire contract and replay of synthetic block / familiar-week requests."""

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from ..planning import familiar as f
from ..planning.familiar_calendar import generate
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


@dataclass(frozen=True)
class ApprovedWeek:
    ref: f.WeekRef
    days: tuple[f.Day, ...]


def build(
    cycle: UUID,
    block: f.Block,
    ctx: f.Context,
    request: f.ProposeBlock | f.FamiliarWeek,
    block_revision: UUID | None,
    weeks: tuple[ApprovedWeek, ...],
) -> f.Candidate:
    if isinstance(request, f.ProposeBlock):
        if block_revision is not None or weeks:
            raise ValueError("block revisions and successor blocks are unsupported")
        generate(cycle, block, ctx, 1)  # Do not propose an unusable initial contract.
        days = ()
    elif isinstance(request, f.FamiliarWeek):
        if block_revision is None or request.number != len(weeks) + 1:
            raise ValueError("approve the block, then detail consecutive new weeks")
        neighbors = tuple(s for week in weeks for day in week.days for s in day.sessions)
        days = generate(cycle, block, ctx, request.number, neighbors)
    else:
        raise ValueError("unsupported generalized planning request")
    return f.Candidate(
        request=request,
        cycle=cycle,
        block_key=block.key,
        block_revision=block_revision,
        prior_weeks=tuple(w.ref for w in weeks),
        days=days,
        supports=tuple(sorted(o.support for o in ctx.observations)),
    )


def check_dates(candidate: f.Candidate, block: f.Block, today: date) -> None:
    first = candidate.days[0].day if candidate.days else block.start
    if first <= today:
        raise ValueError("cannot approve or generate a block/week whose local day has started")

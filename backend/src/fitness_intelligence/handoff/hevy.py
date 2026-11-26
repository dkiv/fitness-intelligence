"""Pure translation to the advertised render_hevy_routine argument shape."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, ValidationError

from fitness_intelligence.planning import familiar as f

from .prescription import Handoff, PrescriptionExport, effort_text, target_text

MAX_PREVIEW_TEXT_LENGTH = 10_000
type PreviewText = Annotated[str, Field(max_length=MAX_PREVIEW_TEXT_LENGTH)]


class VerifiedTemplate(f.Record):
    """Caller attests the destination template and its weight-entry convention match."""

    movement: f.Key
    variation: f.Key
    equipment: f.Key
    load_convention: f.LoadConvention
    template_id: Annotated[str, Field(min_length=1, max_length=1024, pattern=r"^\S+$")]


class RepRange(f.Record):
    start: int
    end: int


class HevySet(f.Record):
    type: Literal["warmup", "normal"]
    reps: int | None
    rep_range: RepRange | None
    weight_kg: float | None


class HevyExercise(f.Record):
    exercise_template_id: str
    notes: PreviewText
    rest_seconds: int | None
    sets: tuple[HevySet, ...]


class Routine(f.Record):
    title: PreviewText
    notes: PreviewText
    exercises: tuple[HevyExercise, ...]


class PreviewArguments(f.Record):
    routine: Routine


class HevyManifest(Handoff):
    policy: Literal["hevy-routine-preview.v1"] = "hevy-routine-preview.v1"
    preview_arguments: PreviewArguments | None
    blockers: tuple[str, ...]


def hevy_manifest(
    source: PrescriptionExport, mappings: tuple[VerifiedTemplate, ...]
) -> HevyManifest:
    p = source.session.prescription
    if not isinstance(p, f.Strength):
        raise ValueError("Hevy routine requires a strength prescription")
    blockers: list[str] = []
    limits = ["Read exercise notes for group order, effort ranges, caps and time allowances."]
    exercises: list[dict[str, object]] = []
    used_ids: set[str] = set()
    for ex in p.exercises:
        key = (ex.movement, ex.variation, ex.equipment, ex.load_convention)
        label = "/".join(key)
        ids = {
            m.template_id
            for m in mappings
            if (m.movement, m.variation, m.equipment, m.load_convention) == key
        }
        if len(ids) != 1:
            reason = "missing" if not ids else "ambiguous"
            blockers.append(f"{label}: {reason} verified template mapping")
            continue
        template_id = ids.pop()
        if template_id in used_ids:
            blockers.append(f"{label}: template also mapped to a different exercise")
        used_ids.add(template_id)
        notes = [f"{label}. Transition allowance {ex.transition_seconds} s."]
        if ex.load_step_kg is not None:
            notes.append(f"Load increment {ex.load_step_kg} kg.")
        if ex.notes:
            notes.append(ex.notes)
        sets: list[HevySet] = []
        rests: set[int] = set()
        for group in ex.groups:
            notes.append(f"{group.key} ({group.kind}) · {effort_text(group.effort)}.")
            for item in group.sets:
                loc = f"{label}/{group.key}/{item.ordinal}"
                if item.load.low != item.load.high:
                    blockers.append(f"{loc}: Hevy has one weight field for a permitted load range")
                    continue
                weight = float(item.load.nominal)
                if Decimal(str(weight)) != item.load.nominal or item.reps.high > 2**53 - 1:
                    blockers.append(f"{loc}: target cannot round-trip through MCP JSON numbers")
                    continue
                fixed = item.reps.low == item.reps.high
                if not fixed:
                    limits.append(
                        f"{loc}: read notes for the preferred rep count within the range."
                    )
                notes.append(
                    f"Set {item.ordinal}: {target_text(item.reps)} reps, allow "
                    f"{item.execution_seconds} s, rest after {item.rest_after_seconds} s."
                )
                rests.add(item.rest_after_seconds)
                sets.append(
                    HevySet(
                        type="warmup" if group.kind == "warmup" else "normal",
                        reps=item.reps.nominal if fixed else None,
                        rep_range=None
                        if fixed
                        else RepRange(start=item.reps.low, end=item.reps.high),
                        weight_kg=None if ex.load_convention == "bodyweight" else weight,
                    )
                )
        if len(rests) > 1:
            limits.append(f"{label}: use the per-set rests in notes. Leave the shared timer unset.")
        exercises.append(
            {
                "exercise_template_id": template_id,
                "notes": "\n".join(notes),
                "rest_seconds": next(iter(rests)) if len(rests) == 1 else None,
                "sets": tuple(sets),
            }
        )
    routine_notes = (
        f"Fixture · {source.approval} · {source.local_start} ({source.zone}). "
        f"Prepare {p.preparation_seconds} s. Calendar reservation {p.reserved_seconds} s."
    )
    try:
        arguments = PreviewArguments.model_validate(
            {
                "routine": {
                    "title": f"{source.session.template} · {source.session.day}",
                    "notes": "\n".join(filter(None, (routine_notes, p.notes))),
                    "exercises": tuple(exercises),
                }
            }
        )
    except ValidationError as exc:
        for error in exc.errors(include_input=False, include_url=False):
            if error["type"] != "string_too_long":
                raise
            field = ".".join(map(str, error["loc"]))
            blockers.append(f"{field} exceeds Hevy's {MAX_PREVIEW_TEXT_LENGTH:,}-character limit")
        arguments = None

    return HevyManifest(
        source=source,
        classification="blocked" if blockers else "usable-with-disclosed-limitations",
        limitations=(*source.historical_limitations, *limits),
        blockers=tuple(blockers),
        preview_arguments=None if blockers else arguments,
    )

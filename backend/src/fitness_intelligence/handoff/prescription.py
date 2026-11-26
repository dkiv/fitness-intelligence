"""Versioned source shared by local handoffs. Only the fixture planner is supported."""

from hashlib import sha256
from typing import Literal, Self
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import model_validator

from fitness_intelligence.db.familiar_snapshot import PREVIEW_OWNER, require_preview_owner
from fitness_intelligence.db.plan_commands import FamiliarPreview, PlanCommands
from fitness_intelligence.db.plan_snapshot import canonical
from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning.prescriptions import Target


class PrescriptionExport(f.Record):
    schema_version: Literal["fi.prescription-export.v1"] = "fi.prescription-export.v1"
    owner_id: UUID
    cycle: UUID
    block_revision: UUID
    revision: UUID
    week: int
    rule: f.FamiliarRule
    approval: Literal["unapproved-preview", "synthetic-approved-fixture"]
    approval_command_id: UUID | None
    publication_authorized: Literal[False] = False
    zone: str
    session: f.Session
    local_start: str  # ISO 8601 wall time with its actual UTC offset, including at a fold.
    prescription_sha256: str

    @model_validator(mode="after")
    def check_source(self) -> Self:
        require_preview_owner(self.owner_id)
        local = self.session.start_utc.astimezone(ZoneInfo(self.zone))
        if local.date() != self.session.day or self.local_start != local.isoformat():
            raise ValueError("scheduled local start differs from the sealed instant or day")
        if self.prescription_sha256 != prescription_digest(self.session.prescription):
            raise ValueError("canonical prescription digest mismatch")
        has_receipt = self.approval_command_id is not None
        if (self.approval == "synthetic-approved-fixture") != has_receipt:
            raise ValueError("fixture approval requires the originating receipt")
        return self

    @property
    def historical_limitations(self) -> tuple[str, ...]:
        if self.rule == "synthetic.familiar.hold.v1":
            return ("Historical fixture rule v1 predates scoped effort-target and cap validation.",)
        return ()


def prescription_digest(prescription: f.Prescription) -> str:
    return sha256(canonical(prescription.model_dump(mode="json")).encode()).hexdigest()


def from_revision(
    commands: PlanCommands, cycle: UUID, revision: UUID, occurrence: UUID
) -> PrescriptionExport:
    """Read a specific fixture occurrence using the existing owner-scoped historical reader."""
    preview = commands.preview(cycle, revision)
    if not isinstance(preview, FamiliarPreview):
        raise ValueError("export requires a generalized familiar week")
    candidate = preview.candidate
    if (
        candidate.cycle != cycle
        or not isinstance(candidate.request, f.FamiliarWeek)
        or candidate.block_revision is None
    ):
        raise ValueError("export requires a dated familiar week in the requested cycle")
    receipt = preview.decision
    if receipt and (receipt.choice != "approve" or receipt.revision_id != revision):
        raise ValueError("revision has no applicable approving decision")
    matches = [s for d in candidate.days for s in d.sessions if s.occurrence == occurrence]
    if len(matches) != 1:
        raise ValueError("expected one matching occurrence in the originating revision")
    session = matches[0]
    zone = preview.sealed_context.zone
    return PrescriptionExport(
        owner_id=PREVIEW_OWNER,
        cycle=cycle,
        block_revision=candidate.block_revision,
        revision=revision,
        week=candidate.request.number,
        rule=candidate.rules,
        approval="synthetic-approved-fixture" if receipt else "unapproved-preview",
        approval_command_id=receipt.command_id if receipt else None,
        zone=zone,
        session=session,
        local_start=session.start_utc.astimezone(ZoneInfo(zone)).isoformat(),
        prescription_sha256=prescription_digest(session.prescription),
    )


class Handoff(f.Record):
    source: PrescriptionExport
    classification: Literal["exact", "usable-with-disclosed-limitations", "blocked"]
    limitations: tuple[str, ...]

    def canonical_json(self) -> str:
        """Stable UTF-8 JSON representation. The digest is external to its own input."""
        return canonical(self.model_dump(mode="json"))

    def digest(self) -> str:
        return sha256(self.canonical_json().encode()).hexdigest()


def target_text(target: Target) -> str:
    if target.low == target.high:
        return str(target.nominal)
    return f"{target.nominal} (permitted {target.low}–{target.high})"


def effort_text(effort: f.Effort) -> str:
    return f"{effort.scale} {target_text(effort.target)}, cap {effort.cap}"

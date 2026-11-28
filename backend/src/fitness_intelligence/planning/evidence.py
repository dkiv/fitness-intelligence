"""Current accepted training evidence for the dedicated planning rehearsal."""

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Self
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import (
    AwareDatetime,
    BeforeValidator,
    Field,
    TypeAdapter,
    ValidationInfo,
    model_validator,
)

from ..analytics.exposure import Outing, RecoveryExposure
from ..analytics.longitudinal import Coverage, OpenIssue
from ..analytics.strength import CATEGORIES, StrengthFact
from . import confirmation as c
from . import familiar as f
from . import familiar_outcomes as actual


class Comparison(f.Record):
    account: UUID
    member: UUID
    source_digest: c.Digest  # Includes owner, account, workout, child and external reference.
    version: f.Text
    comparison: f.Text
    basis: f.Text
    authority: Literal["reviewed-mapping", "athlete-context"]


class StrengthContext(Comparison):
    sport: Literal["strength"] = "strength"
    movement: f.Key
    variation: f.Key
    equipment: f.Key
    load_convention: f.LoadConvention
    group: f.Key
    kind: Literal["working", "warmup"]
    ordinal: f.Positive


class RunContext(Comparison):
    sport: Literal["running"] = "running"
    role: f.Key
    structure: Literal["continuous", "intervals"]


type Context = Annotated[StrengthContext | RunContext, Field(discriminator="sport")]
type Native = StrengthFact | Outing


class Scope(f.Record):
    start: date
    stop: date
    zone: str = "UTC"
    strength_account: UUID | None = None
    endurance_account: UUID | None = None
    recovery_account: UUID | None = None
    endurance_zone: str | None = None
    recovery_zone: str | None = None
    external_load_templates: tuple[str, ...] = ()
    lower_body_templates: tuple[str, ...] = ()
    non_lower_body_templates: tuple[str, ...] = ()
    contexts: tuple[Context, ...] = ()

    @model_validator(mode="after")
    def dates_and_sources(self) -> Self:
        if self.start >= self.stop:
            raise ValueError("empty planning period")
        for zone in (self.zone, self.endurance_zone, self.recovery_zone):
            if zone is not None:
                ZoneInfo(zone)
        if (
            self.endurance_account
            and self.endurance_account == self.recovery_account
            and (self.endurance_zone != self.recovery_zone)
        ):
            raise ValueError("one source account must use one verified calendar")
        f.unique(((m.account, m.member) for m in self.contexts), "member context")
        return self


class PendingDeletion(f.Record):
    id: UUID
    observed_at: datetime
    source_deleted_at: datetime | None


class NativeMember(f.Record):
    fact: Native
    digest: c.Digest
    context: Context | None
    display: c.Fact | None
    limitation: str | None
    activity_discrepancies: tuple[str, ...] = ()
    pending_deletion: PendingDeletion | None = None
    workout_created_at: datetime | None = None
    reference_first_imported_at: datetime | None = None
    recorded_at: datetime | None = None  # First availability of this exact member version.


_NATIVE = TypeAdapter(Native)


def bridge(
    fact: Native, context: Context | None, *, activity_discrepancies: tuple[str, ...] = ()
) -> NativeMember:
    # A later identical retrieval does not change content. Keep its clock on the raw fact.
    raw = _NATIVE.dump_python(fact, mode="json")
    raw.pop("report_date")
    raw.pop("retrieved_at")
    for field in raw.get("fields", ()):
        field.pop("retrieved_at")
    wire = json.dumps(raw, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(wire.encode()).hexdigest()
    display = None
    limitation = None
    if context is None:
        limitation = "explicit comparison context missing"
    elif context.account != fact.source.source_account_id or context.source_digest != digest:
        limitation = "comparison context refers to different source content"
    else:
        source = fact.source
        common = dict(
            owner=source.owner_id,
            account=source.source_account_id,
            reference=fact.reference_id,
            revision=digest,
            mapping=c.digest(context),
            comparison=context.comparison,
        )
        if isinstance(fact, StrengthFact) and isinstance(context, StrengthContext):
            row = fact.row
            category = CATEGORIES.get(row.kind)
            if row.set_id != context.member or row.exercise_id is None:
                limitation = "context does not identify a canonical set"
            elif category and category != context.kind:
                limitation = "mapped set kind conflicts with source"
            elif context.load_convention == "bodyweight" and row.weight_kg not in (0, None):
                limitation = "mapped convention conflicts with source load"
            else:
                display = c.StrengthFact(
                    **common,
                    workout=row.workout_id,
                    member=row.set_id,
                    exercise=row.exercise_id,
                    occurred_at=row.started_at,
                    movement=context.movement,
                    variation=context.variation,
                    equipment=context.equipment,
                    group=context.group,
                    kind=context.kind,
                    ordinal=context.ordinal,
                    load_convention=context.load_convention,
                    reps=row.repetitions,
                    kg=row.weight_kg,
                    provenance={
                        "confirmed": "provider-timestamp",
                        "inferred": "historically-inferred",
                        "unsupported": "unknown",
                    }[fact.execution],
                    completed_at=row.completed_at,
                )
        elif (
            isinstance(fact, Outing)
            and isinstance(context, RunContext)
            and fact.sport == "running"
            and fact.workout_id == context.member
        ):
            if fact.activity_issues:
                limitation = "activity reconciliation unresolved"
            else:

                def seconds(v: Decimal | None) -> int | None:
                    return int(v) if v is not None and v == v.to_integral_value() else None

                display = c.RunningFact(
                    **common,
                    workout=fact.workout_id,
                    role=context.role,
                    occurred_at=fact.started_at,
                    provenance="activity-summary",
                    elapsed_seconds=seconds(fact.elapsed_s),
                    moving_seconds=seconds(fact.moving_s),
                    distance_metres=fact.distance_m,
                )
        else:
            limitation = "context does not match source sport or identity"
    return NativeMember(
        fact=fact,
        digest=digest,
        context=context,
        display=display,
        limitation=limitation,
        activity_discrepancies=activity_discrepancies,
    )


class Day(f.Record):
    day: date
    strength_acquisition: str | None
    strength_account_status: str | None
    open_issues: tuple[OpenIssue, ...]
    activities: Coverage | None
    instructions: Coverage | None
    discrepancies: tuple[str, ...]
    scan_started_at: datetime | None
    full_day_zero_exclusion: str | None
    running_count_tier: Literal["derived"] = "derived"
    running_count: int | None
    running_count_status: str | None
    recovery: RecoveryExposure | None


class Confirmation(f.Record):
    account: UUID
    member: UUID
    state: str
    reason: str | None
    confirmed: tuple[tuple[c.Name, c.Value], ...]
    unconfirmed: tuple[c.Name, ...]
    history: tuple[c.Assertion, ...]
    ambiguous_set_link: bool
    effective_link: c.Attribution | None


class Manual(f.Record):
    block_key: str
    block_revision: UUID
    cycle: UUID
    week: int
    origin: UUID
    prescription_tier: Literal["instruction"] = "instruction"
    prescribed: f.Session
    history: tuple[actual.Assertion, ...]


type Tier = Literal[
    "provider-reported",
    "provider-inferred",
    "confirmed-display",
    "athlete-actual",
    "manual-actual",
    "instruction",
    "derived",
]


def _measurement(value: object, info: ValidationInfo) -> object:
    # Decimal quantities are serialized as exact strings. Keep free-text reports textual.
    name = info.data.get("name", "")
    if isinstance(value, str) and (
        name.split(".")[-1]
        in {
            "kg",
            "set_rpe",
            "session_rpe",
            "achieved_rpe",
            "elapsed_seconds",
            "moving_seconds",
            "activity_seconds",
            "distance_metres",
            "average_speed_mps",
        }
        or name.startswith("kg.")
    ):
        return Decimal(value)
    return value


type Scalar = Annotated[bool | int | Decimal | str, BeforeValidator(_measurement)]


class Claim(f.Record):
    name: str
    value: Scalar
    tier: Tier
    support: UUID


class FieldEvidence(f.Record):
    name: str
    claims: tuple[Claim, ...]
    state: Literal["unknown", "source-only", "actual", "conflict", "withheld"]
    value: Scalar | None
    reason: str


def resolve(name: str, claims: tuple[Claim, ...]) -> FieldEvidence:
    actuals = [
        c for c in claims if c.tier in ("athlete-actual", "manual-actual", "confirmed-display")
    ]
    if len({c.value for c in actuals}) > 1:
        state, value, reason = "conflict", None, "current independently supported values disagree"
    elif actuals:
        state, value, reason = "actual", actuals[0].value, "scoped current athlete evidence"
        if any(c.value != value for c in claims):
            reason = "scoped athlete actual takes precedence over the recorded source field"
    elif claims:
        state, value, reason = "source-only", claims[0].value, "no independent athlete assertion"
    else:
        state, value, reason = "unknown", None, "no measurement at this scope"
    return FieldEvidence(name=name, claims=claims, state=state, value=value, reason=reason)


class Qualification(f.Record):
    purpose: Literal[
        "descriptive-exposure",
        "confirmed-execution",
        "comparable-strength",
        "comparable-running",
        "familiar-dose-input",
        "progression-review-input",
    ]
    required: tuple[str, ...]
    optional: tuple[str, ...]
    missing: tuple[str, ...]
    exclusions: tuple[str, ...]

    @property
    def eligible(self) -> bool:
        return not (self.missing or self.exclusions)


class Task(f.Record):
    sport: str
    member: UUID | None
    # Identifies an actual reported set in the manual assertion when applicable.
    manual_set: actual.SetExecution | None
    fields: tuple[FieldEvidence, ...]
    qualifications: tuple[Qualification, ...]


class Performance(f.Record):
    execution_state: Literal["recorded", "inferred", "completed", "partial", "missed", "unknown"]
    workout: UUID | None
    manual: Manual | None
    occurred_at: datetime
    sport: str
    members: tuple[NativeMember, ...]
    tasks: tuple[Task, ...]
    potential_duplicates: tuple[UUID, ...]


class Projection(f.Record):
    contract: Literal["planning-evidence-v1"] = "planning-evidence-v1"
    d1_contract: Literal["d1d-v1"] = "d1d-v1"
    owner: UUID
    scope: Scope
    days: tuple[Day, ...]
    confirmations: tuple[Confirmation, ...]
    performances: tuple[Performance, ...]


class SelectedAccount(f.Record):
    id: UUID
    provider: str
    provider_account_id: str
    status: str


class CoverageReceipt(f.Record):
    account: UUID
    day: date
    category: str
    receipts_json: str  # Canonical JSON of the selected acquisition ledger entry.


class DecisionInputs(f.Record):
    version: Literal["decision-inputs-v1"] = "decision-inputs-v1"
    policy: str
    selection: Literal["explicit", "representative-week", "adaptation-window"]
    cutoff: AwareDatetime
    accounts: tuple[SelectedAccount, ...]
    coverage_receipts: tuple[CoverageReceipt, ...]
    projection: Projection


class CoreDecision(f.Record):
    template: str
    task: str
    action: Literal["hold", "reps", "load", "duration", "resume"]
    reason: str
    anchor_revision: UUID
    anchor_dose: str
    anchor_occurrences: tuple[UUID, ...]
    anchor_assertions: tuple[UUID, ...]
    before: str
    after: str
    considered: str | None = None
    # Stable occurrence identities and current assertion tips. Full claims live in the projection.
    performances: tuple[UUID, ...]
    assertions: tuple[UUID, ...]
    ceiling_since_week: f.Positive | None = None

    @property
    def reentry(self) -> bool:
        return self.ceiling_since_week is not None


class CoreReview(f.Record):
    version: Literal["synthetic.core.v1"] = "synthetic.core.v1"
    joint: Literal["J-DEFAULT"] = "J-DEFAULT"
    predecessor: UUID
    decisions: tuple[CoreDecision, ...]


class ReviewedCandidate(f.Candidate):
    adaptation: CoreReview | None = Field(default=None, exclude_if=lambda x: x is None)
    decision_inputs: DecisionInputs

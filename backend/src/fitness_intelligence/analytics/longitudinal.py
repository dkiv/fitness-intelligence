"""Daily analytical results on the source calendar. No display rounding or persistence."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, localcontext
from typing import Literal
from uuid import UUID

from fitness_intelligence.analytics.strength import Period
from fitness_intelligence.domain.endurance import Source


@dataclass(frozen=True)
class ObservationId:
    source: Source
    entity: Literal["daily_intake", "body_weight", "daily_recovery"]
    id: UUID


@dataclass(frozen=True)
class Observation:
    identity: ObservationId
    provider_date: date
    report_date: date | None
    occurred_at: datetime | None
    retrieved_at: datetime | None
    recorded_at: datetime | None
    value: Decimal
    unit: str
    method: str
    source_field: str | None
    mapping_version: str | None
    upstream_writer: str | None


@dataclass(frozen=True)
class IntakeObservation(Observation):
    retrieved_at: datetime
    source_field: str
    mapping_version: str
    source_data_present: bool | None
    logging_completeness: str
    exclusion_reason: str | None


@dataclass(frozen=True)
class WeighIn(Observation):
    retrieved_at: datetime
    source_field: str
    mapping_version: str
    source_value: Decimal
    interpreted_unit: str
    documented_unit: str | None
    time_resolution_us: int
    verification_basis: Literal["historical_segment", "bounded_operator_verified"]
    verification_scope: str | None


@dataclass(frozen=True)
class Issue:
    subject: str
    reason: str


@dataclass(frozen=True)
class Coverage:
    source: Source
    account_status: str
    category: str
    provider_date: date
    status: str
    attempted_at: datetime | None
    last_success: datetime | None
    last_success_count: int | None
    policy: str | None
    pass_key: str | None
    source_receipts: tuple[tuple[str, str], ...]
    acquisition_gap: str | None
    issues: tuple[Issue, ...]
    retained_count: int

    @property
    def reconciliation(self) -> str:
        return "unresolved" if self.issues else "no_open_issue"

    @property
    def observations_without_coverage(self) -> bool:
        return self.status == "never_queried" and self.retained_count > 0


@dataclass(frozen=True)
class Metric:
    """One provider-day value. report_date requires positive day alignment."""

    scope: Literal["owner_day", "account_day"]
    status: str
    value: Decimal | None
    unit: str
    report_date: date | None
    supporting: tuple[ObservationId, ...]
    retained_count: int
    reasons: tuple[str, ...]

    @property
    def eligible_count(self) -> int:
        return len(self.supporting)


@dataclass(frozen=True)
class DailyIntake:
    metric: Metric
    logging_completeness: str
    facts: tuple[IntakeObservation, ...]
    coverage: tuple[Coverage, ...]


@dataclass(frozen=True)
class WeightExclusion:
    identity: ObservationId
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class DailyWeight:
    metric: Metric
    measurements: tuple[WeighIn, ...]
    excluded: tuple[WeightExclusion, ...]
    coverage: Coverage


@dataclass(frozen=True)
class ExpenditureObservation(Observation):
    component: str
    window_start: datetime | None
    window_end: datetime | None


@dataclass(frozen=True)
class DailyExpenditure:
    total: Metric
    active: Metric
    basal: Metric
    facts: tuple[ExpenditureObservation, ...]
    coverage: Coverage


@dataclass(frozen=True)
class ReportDay:
    provider_date: date
    intake: DailyIntake
    weight: DailyWeight
    expenditure: DailyExpenditure | None = None


@dataclass(frozen=True)
class LongitudinalReport:
    owner_id: UUID
    weight_source: Source
    period: Period
    source_zones: tuple[tuple[UUID, str], ...]
    days: tuple[ReportDay, ...]
    contract_version: str = "d1c-v1"
    policy_version: str = "intake-weight-v2"
    date_basis: str = "provider_local"
    observation_state: str = "latest_accepted"
    expenditure_source: Source | None = None


def daily_median(values: tuple[Decimal, ...]) -> Decimal | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    # Canonical NUMERIC(22,9) needs one extra digit for an exact even median.
    with localcontext() as ctx:
        ctx.prec = 38
        return (ordered[mid - 1] + ordered[mid]) / 2

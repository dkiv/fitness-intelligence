"""Shared weight-series partitions for eligible readings from a single source account."""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from fitness_intelligence.analytics.longitudinal import WeighIn
from fitness_intelligence.domain.endurance import Source


@dataclass(frozen=True)
class WeightContinuity:
    """Caller-reviewed evidence of a common scale/protocol across named unit verifications."""

    source: Source
    start: date
    stop: date
    verification_scopes: frozenset[str | None]
    evidence_ref: str

    def __post_init__(self) -> None:
        if self.stop <= self.start or not self.evidence_ref.strip() or not self.verification_scopes:
            raise ValueError(
                "weight continuity requires a period, verification scopes and evidence"
            )
        if not isinstance(self.verification_scopes, frozenset):
            raise ValueError("verification scopes must be immutable")


@dataclass(frozen=True)
class SeriesKey:
    # Source is fixed by the request. A changing producer, unit or writer splits the series.
    field: str
    mapping: str
    method: str
    interpreted_unit: str
    documented_unit: str | None
    writer: str | None
    basis: str
    reference: str


def _weight_key(w: WeighIn, continuity: WeightContinuity | None) -> SeriesKey:
    if (
        continuity
        and continuity.source == w.identity.source
        and continuity.start <= w.provider_date < continuity.stop
        and w.verification_scope in continuity.verification_scopes
    ):
        basis, ref = "reviewed_continuity", continuity.evidence_ref
    elif w.verification_scope is not None:
        basis, ref = "verified_segment", w.verification_scope
    else:
        basis, ref = "bounded_day", w.provider_date.isoformat()
    # D1B only releases weigh-ins with a recognized field and mapping version.
    assert w.source_field is not None and w.mapping_version is not None
    return SeriesKey(
        w.source_field,
        w.mapping_version,
        w.method,
        w.interpreted_unit,
        w.documented_unit,
        w.upstream_writer,
        basis,
        ref,
    )


def partition_weigh_ins(
    readings: Iterable[WeighIn], continuity: WeightContinuity | None = None
) -> dict[SeriesKey, list[WeighIn]]:
    groups: dict[SeriesKey, list[WeighIn]] = defaultdict(list)
    for reading in readings:
        groups[_weight_key(reading, continuity)].append(reading)
    return groups

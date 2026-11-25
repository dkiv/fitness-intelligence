"""Apply the operator's bracketed weight interpretation to one all-entry day."""

from collections import Counter
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from fitness_intelligence.db.history_models import GarminIssue
from fitness_intelligence.db.nutrition_models import BodyWeightObservation

from .history_state import Category, WeightSegment, account_key, close_issues, day_key, issue
from .mapping import GarminBinding, MappingError, Row
from .nutrition import WeighIn, WeightUnit, map_weights, save_weight

MARKERS = ("device", "deviceId", "sourceType", "source", "writer", "measurementType")
REASONS = ("instant_collision", "ambiguous_correction", "unit_or_format")


def candidate(
    day: date, row: Row, segment: WeightSegment, collisions: set[int]
) -> tuple[str, WeighIn | str]:
    raw, stamp = row["weight"], row.get("timestampGMT")
    if stamp is None:
        return "day", "missing_instant"
    if type(stamp) is not int or not 10**12 <= stamp < 10**13:
        return "day", "unit_or_format"
    subject = str(stamp)
    if (
        not isinstance(raw, Decimal)
        or not segment.minimum <= raw <= segment.maximum
        or any(row.get(k) is not None for k in MARKERS)
    ):
        return subject, "unit_or_format"
    if stamp in collisions:
        return subject, "instant_collision"
    try:
        entries, _ = map_weights(day, [row], WeightUnit.GRAMS)
    except MappingError:
        return subject, "unit_or_format"
    return subject, entries[0]


def reconcile_weight(
    session: Session,
    binding: GarminBinding,
    day: date,
    series: list[Row],
    segment: WeightSegment,
    when: datetime,
    collisions: set[int],
) -> tuple[Counter[str], bool]:
    source = binding.source
    counts: Counter[str] = Counter()
    candidates: dict[str, WeighIn] = {}
    for row in series:
        if row.get("weight") is None:
            continue
        subject, outcome = candidate(day, row, segment, collisions)
        if isinstance(outcome, WeighIn):
            candidates[subject] = outcome
        else:
            issue(
                session,
                source,
                Category.WEIGHT,
                day,
                subject,
                outcome,
                [row.get("timestampGMT"), row["weight"], segment.fingerprint],
                when,
            )
            counts["unresolved"] += 1

    # A new or outstanding unit anomaly holds the day. An empty retry or an
    # unrelated good measurement cannot authorize continuing through this segment.
    unit_query = select(GarminIssue.subject).filter_by(
        **day_key(source, Category.WEIGHT, day), reason="unit_or_format", resolved_at=None
    )
    open_units = set(session.scalars(unit_query))
    if open_units - candidates.keys():
        return counts, True

    query = select(BodyWeightObservation).filter_by(**account_key(source), upstream_id=None)
    prior = {r.measured_at for r in session.scalars(query.filter_by(local_date=day))}
    seen = {entry.instant for entry in candidates.values()}
    for subject, entry in candidates.items():
        result = save_weight(session, binding, day, entry, when)
        record = session.scalars(query.filter_by(measured_at=entry.instant)).one()
        counts[result] += 1
        if result == "unresolved":
            evidence = [subject, entry.source_value, segment.fingerprint]
            for affected_day in {record.local_date, day}:
                issue(
                    session,
                    source,
                    Category.WEIGHT,
                    affected_day,
                    subject,
                    "ambiguous_correction",
                    evidence,
                    when,
                )
        else:
            record.verification_scope = segment.fingerprint
            close_issues(session, source, Category.WEIGHT, day, subject, REASONS, when)
    if prior - seen and seen - prior:
        issue(session, source, Category.WEIGHT, day, "day", "possible_retime", sorted(seen), when)
        counts["unresolved"] += 1
    elif prior and prior <= seen and not counts["unresolved"]:
        close_issues(session, source, Category.WEIGHT, day, "day", ("possible_retime",), when)
    return counts, bool(open_units and session.scalar(unit_query.limit(1)))

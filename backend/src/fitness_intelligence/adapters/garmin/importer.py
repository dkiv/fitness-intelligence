"""Bounded local operations. Stage all remote reads before the write transaction."""

from collections import Counter
from contextlib import nullcontext
from datetime import UTC, date, datetime
from enum import StrEnum

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from fitness_intelligence.adapters.local_account import locked_account

from .binding import (
    Evidence,
    EvidenceType,
    Feed,
    VerifiedSample,
    detail_for,
    feed_for,
    search_page,
    verify,
)
from .client import Endpoint, GarminClient, GarminError
from .mapping import DETAIL_STAMP, WorkoutResponse, map_activity, map_day, obj, stamp
from .nutrition import WeightUnit, map_weights, read_intake, save_intake, save_weight
from .persistence import Snapshot, save_activity, save_observation
from .projection import activity_inputs


class Mode(StrEnum):
    VERIFY = "verify-only"
    ENROLL = "enroll"
    ACTIVITIES = "activities"
    RECOVERY = "recovery"
    INTAKE = "intake"
    WEIGHT = "weight"

    @property
    def takes_day(self) -> bool:
        return self in (Mode.ACTIVITIES, Mode.RECOVERY, Mode.INTAKE, Mode.WEIGHT)


class Importer:
    def __init__(self, engine: Engine, evidence: Evidence, client: GarminClient) -> None:
        self.engine, self.evidence, self.client = engine, evidence, client

    def activities(self, day: date, sample: VerifiedSample, steps: bool) -> list[Snapshot]:
        binding = sample.binding
        anchor = day == self.evidence.day
        page = sample.page if anchor else search_page(self.client, binding, day)
        result = []
        for ident, summary in page.items():
            detail = (
                sample.detail
                if anchor and ident == self.evidence.activity_id
                else detail_for(self.client, binding, ident)
            )
            workouts = None
            if steps:
                workouts = WorkoutResponse(
                    binding.source, ident, self.client.read(Endpoint.WORKOUTS, activity_id=ident)
                )
            activity = map_activity(binding, summary, detail=detail, workouts=workouts)
            meta = detail.get("metadataDTO")
            updated = obj(meta).get("lastUpdateDate") if meta is not None else None
            split_source = None
            if activity.splits is not None:
                split_source = (
                    "ActivitySummaryDTO"
                    if detail.get("splitSummaries") is not None
                    else "SummarizedActivityDTO"
                ) + ".splitSummaries"
            result.append(
                Snapshot(
                    activity,
                    None if updated is None else stamp(updated, DETAIL_STAMP).replace(tzinfo=UTC),
                    split_source,
                    activity_inputs(activity, summary, detail, workouts),
                )
            )
        return result

    def run(
        self,
        mode: Mode,
        *,
        day: date | None = None,
        steps: bool = False,
        weight_unit: WeightUnit | None = None,
    ) -> dict[str, int | str]:
        mode = Mode(mode)
        evidence = self.evidence
        source = evidence.source
        writing_data = mode.takes_day
        if writing_data != (day is not None) or (steps and mode != Mode.ACTIVITIES):
            raise GarminError("invalid operation")
        if (mode == Mode.WEIGHT) != (weight_unit is not None) or (
            weight_unit is not None and not isinstance(weight_unit, WeightUnit)
        ):
            raise GarminError("weight operation requires a verified source unit")
        if mode == Mode.RECOVERY and not evidence.feeds:
            raise GarminError("no verified recovery feeds selected")
        if (
            mode != Mode.VERIFY
            and evidence.kind == EvidenceType.INDEPENDENT
            and not evidence.durability_confirmed
        ):
            raise GarminError("independent durability evidence required")
        if mode == Mode.VERIFY:
            with Session(self.engine) as session:
                expected = evidence.resolve(session, allow_new=True)
            sample = verify(self.client, evidence, expected)
            # A discovered profile may already belong to another account of this owner.
            with Session(self.engine) as session:
                current = evidence.resolve(
                    session, allow_new=expected is None, observed=sample.binding
                )
            result = self.comparisons()
            if evidence.kind == EvidenceType.WITNESSED and current is None:
                result["candidate_pin"] = evidence.receipt(sample.binding)
            return result

        with locked_account(self.engine, source.source_account_id) as session:
            with session.begin():
                expected = evidence.resolve(session, allow_new=mode == Mode.ENROLL)
            scoped_feeds = mode in (Mode.INTAKE, Mode.WEIGHT)
            counts: Counter[str] = Counter()
            intake = []
            weights = []
            with self.client.verified_session() if scoped_feeds else nullcontext():
                sample = verify(self.client, evidence, expected)
                if mode == Mode.INTAKE and day is not None:
                    intake = read_intake(self.client, sample, day, evidence.day)
                if mode == Mode.WEIGHT and day is not None and weight_unit is not None:
                    try:
                        payload = self.client.read(Endpoint.WEIGHT, day=day.isoformat())
                    except GarminError as exc:
                        if str(exc) not in ("no_content", "not_found"):
                            raise
                        counts["feeds_without_content"] += 1
                    else:
                        weights, unresolved = map_weights(day, payload, weight_unit)
                        if unresolved:
                            counts["unresolved"] += unresolved

            activities = []
            observations = ()
            if mode == Mode.ACTIVITIES and day is not None:
                activities = self.activities(day, sample, steps)
            if mode == Mode.RECOVERY and day is not None:
                feeds = dict(sample.feeds)
                if day != evidence.day:
                    feeds.clear()
                    for feed in evidence.feeds:
                        try:
                            feeds[feed] = feed_for(self.client, sample.binding, day, feed)
                        except GarminError as exc:
                            # Garmin documents 204 for the verified HRV feed.
                            if feed != Feed.HRV or str(exc) != "no_content":
                                raise
                            counts["feeds_without_content"] += 1
                observations = map_day(sample.binding, day, **feeds)

            retrieved = datetime.now(UTC)
            with session.begin():
                account = evidence.resolve(
                    session,
                    allow_new=mode == Mode.ENROLL and expected is None,
                    observed=sample.binding,
                    for_write=True,
                )
                if mode == Mode.ENROLL:
                    evidence.enroll(session, sample.binding, account)
                    return {"enrolled" if account is None else "already_enrolled": 1}
                for snapshot in activities:
                    counts[save_activity(session, snapshot, retrieved)] += 1
                for obs in observations:
                    counts[save_observation(session, obs, retrieved)] += 1
                if day is not None:
                    for total in intake:
                        counts[save_intake(session, sample.binding, day, total, retrieved)] += 1
                    for entry in weights:
                        counts[save_weight(session, sample.binding, day, entry, retrieved)] += 1
            return {
                "observed": sum(v for k, v in counts.items() if k != "feeds_without_content"),
                **counts,
            }

    def comparisons(self) -> dict[str, int | str]:
        return dict.fromkeys(
            (
                "search_owner_matched",
                "known_activity_matched",
                "detail_owner_matched",
                *(f"{feed.value}_matched" for feed in self.evidence.feeds),
            ),
            1,
        )

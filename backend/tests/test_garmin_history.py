"""Synthetic historical windows and the real PostgreSQL transaction boundaries."""

import json
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import delete, event, select
from sqlalchemy.orm import Session
from test_garmin_importer import DAY, IDENT, KEY, PRIVATE, PROFILE, Provider, enroll, evidence

from fitness_intelligence.adapters.garmin.binding import Evidence
from fitness_intelligence.adapters.garmin.client import Endpoint, GarminClient, GarminError
from fitness_intelligence.adapters.garmin.history import synchronize
from fitness_intelligence.adapters.garmin.history_state import (
    Category,
    Scope,
    WeightSegment,
    day_status,
)
from fitness_intelligence.adapters.garmin.importer import Importer, Mode
from fitness_intelligence.adapters.local_account import LocalAccountError, locked_account
from fitness_intelligence.db.endurance_models import (
    ActivitySplit,
    ActivityStep,
    DailyRecoveryObservation,
    EnduranceActivity,
)
from fitness_intelligence.db.history_models import GarminCoverage, GarminIssue
from fitness_intelligence.db.models import ExternalReference, SourceAccount, User, Workout
from fitness_intelligence.db.nutrition_models import BodyWeightObservation, DailyIntakeObservation
from fitness_intelligence.db.plan_models import AthleteContext
from fitness_intelligence.nutrition.intake import select_daily_intake
from fitness_intelligence.nutrition.weight import select_weight_day


class HistoricalProvider(Provider):
    def __init__(self) -> None:
        super().__init__()
        self.v2 = [
            dict(
                calendarDate=str(DAY),
                userProfilePk=PROFILE,
                source="GARMIN",
                calories={
                    "consumedValue": 1900,
                    "burnedTotal": 1700,
                    "burnedActive": 200,
                    "burnedResting": 1500,
                },
            )
        ]
        self.sleep_rows = [self.sleep]
        self.hrv_rows = [self.hrv["hrvSummary"]]
        self.activity_rows = deepcopy(self.summaries[DAY])
        self.pages = []
        self.mutation = None
        self.daily["consumedKilocalories"] = 1900

    def handle(self, req: httpx.Request) -> httpx.Response:
        path, params = req.url.path, req.url.params
        if path in self.errors:
            return httpx.Response(self.errors[path])
        if path == Endpoint.DAILY_RANGE:
            payload = {"data": self.v2}
        elif path.startswith("/weight-service/weight/all/"):
            payload = self.weights
        elif path == Endpoint.SLEEP_RANGE:
            payload = self.sleep_rows
        elif path.startswith("/hrv-service/hrv/daily/"):
            payload = {"userProfilePk": PROFILE, "hrvSummaries": self.hrv_rows}
        elif path == Endpoint.ACTIVITIES and "sortBy" in params:
            offset = int(params["start"])
            assert params["sortOrder"] == "asc" and params["excludeChildren"] == "true"
            self.pages.append(offset)
            payload = self.activity_rows[offset : offset + int(params["limit"])]
            if self.mutation:
                payload = self.mutation(offset, payload)
        else:
            return super().handle(req)
        return httpx.Response(200, content=json.dumps(payload).replace('"wire-decimal"', "1234.0"))

    def page_of_ten(self) -> None:
        self.activity_rows = []
        for k in range(10):
            row = deepcopy(self.summaries[DAY][0])
            self.details[IDENT + k] = deepcopy(self.details[IDENT]) | {"activityId": IDENT + k}
            row.update(
                activityId=IDENT + k,
                startTimeLocal=f"{DAY} 10:00:{k:02}",
                startTimeGMT=f"{DAY} 14:00:{k:02}",
                activityType={"typeKey": "cycling"},
            )
            row.pop("beginTimestamp")
            self.activity_rows.append(row)


@pytest.fixture
def bound(db: Session) -> tuple[Evidence, HistoricalProvider]:
    user = User()
    db.add(user)
    db.commit()
    ev = evidence(user)
    provider = HistoricalProvider()
    client = GarminClient(KEY, transport=httpx.MockTransport(provider.handle))
    try:
        enroll(Importer(db.bind, ev, client))
    finally:
        client.close()
    return ev, provider


def run(
    db: Session,
    bound: tuple,
    categories: tuple,
    *,
    mode="backfill",
    limit=40,
    start=DAY,
    end=DAY,
    segment=None,
    pass_id=None,
    overlap=7,
) -> dict:
    ev, provider = bound
    scope = Scope(
        mode,
        start,
        end,
        categories,
        pass_id or (UUID(int=0) if mode == "backfill" else uuid4()),
        overlap,
        segment,
    )
    client = GarminClient(KEY, request_limit=limit, transport=httpx.MockTransport(provider.handle))
    try:
        return synchronize(db.bind, ev, client, scope)
    finally:
        client.close()
        db.expire_all()


def test_range_replay_daily_provenance(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    cats = (Category.INTAKE, Category.RESTING, Category.EXPENDITURE, Category.SLEEP, Category.HRV)
    result = run(db, bound, cats)
    assert result["stopped"] is None
    assert result["observations"]["created"] == 12
    assert "food" not in result["requests"]
    records = db.scalars(select(DailyRecoveryObservation)).all()
    assert len(records) == 11
    overnight = next(r for r in records if r.metric == "overnight_hrv")
    assert overnight.window_start is None and overnight.unit == "source_unit_unverified"
    assert "hrvSummaries" in overnight.source_field
    intake = db.scalars(select(DailyIntakeObservation)).one()
    assert (
        intake.source_data_present is None
        and intake.completeness == "unknown"
        and intake.upstream_writer is None
    )
    ids = {r.id for r in records}
    assert all(v["remaining"] == 0 for v in result["categories"].values())
    assert run(db, bound, cats)["observations"]["unchanged"] == 0
    assert run(db, bound, cats, mode="incremental")["observations"]["unchanged"] == 12
    assert ids == {r.id for r in db.scalars(select(DailyRecoveryObservation))}
    assert day_status(db, ev.source, Category.WEIGHT, DAY)["acquisition"] == "never_queried"
    assert (
        day_status(db, replace(ev.source, source_account_id=uuid4()), Category.SLEEP, DAY)[
            "acquisition"
        ]
        == "never_queried"
    )


def test_sparse_categories_zero_and_explicit_empty(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    p.v2[0]["calories"] = {"consumedValue": 0}
    p.daily = {"calendarDate": str(DAY), "userProfileId": PROFILE}
    p.food = {"mealDate": str(DAY), "dailyNutritionContent": {"calories": 0}}
    result = run(db, bound, (Category.INTAKE, Category.RESTING, Category.EXPENDITURE))
    assert result["stopped"] is None and result["requests"]["daily"] == 2
    for c in (Category.INTAKE, Category.RESTING, Category.EXPENDITURE):
        assert day_status(db, ev.source, c, DAY)["acquisition"] == "empty"
    assert select_daily_intake(db, ev.source.owner_id, DAY).status == "missing"
    p.v2[0]["calories"] = {"consumedValue": 890}
    run(db, bound, (Category.INTAKE, Category.RESTING), mode="incremental")
    assert day_status(db, ev.source, Category.INTAKE, DAY)["acquisition"] == "observed"
    assert day_status(db, ev.source, Category.RESTING, DAY)["acquisition"] == "empty"


def test_stale_source_totals_targeted_repair(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    assert run(db, bound, (Category.INTAKE,), mode="repair")["observations"]["created"] == 3
    p.v2[0]["calories"]["consumedValue"] = 2050
    result = run(db, bound, (Category.INTAKE,), mode="incremental", limit=7)
    assert result["stopped"] == "budget_exhausted"
    assert day_status(db, ev.source, Category.INTAKE, DAY)["reconciliation"] == "unresolved"
    assert select_daily_intake(db, ev.source.owner_id, DAY).status == "conflict"
    result = run(db, bound, (Category.INTAKE,), mode="incremental")
    assert result["requests"]["food"] == 1 and result["observations"]["unresolved"] == 1
    p.daily["consumedKilocalories"] = p.food["dailyNutritionContent"]["calories"] = 2050
    result = run(db, bound, (Category.INTAKE,), mode="repair")
    assert result["categories"]["intake"]["open_issues"] == 0
    selected = select_daily_intake(db, ev.source.owner_id, DAY)
    assert selected.reported_kcal == 2050 and len(selected.observation_ids) == 3


def test_weight_segment_and_quarantine(
    db: Session, bound: tuple[Evidence, HistoricalProvider], tmp_path: Path
) -> None:
    ev, p = bound
    cfg = dict(
        approved=True,
        unit="g",
        start=str(DAY),
        end=str(DAY),
        user_id=str(ev.source.owner_id),
        source_account_id=str(ev.source.source_account_id),
        references=[
            dict(date=str(DAY), verified_grams="72000"),
            dict(date=str(DAY + timedelta(days=3)), verified_grams="73500"),
        ],
    )
    path = tmp_path / "segment"
    path.write_text(json.dumps(cfg))
    path.chmod(0o600)
    seg = WeightSegment.load(path, ev.source)
    with pytest.raises(GarminError, match="segment"):
        WeightSegment.load(path, replace(ev.source, owner_id=uuid4()))

    def get(mode="repair", **kw):
        return run(db, bound, (Category.WEIGHT,), mode=mode, segment=seg, **kw)

    with pytest.raises(GarminError, match="segment"):
        get(end=DAY + timedelta(days=1))
    original = deepcopy(p.weights[0])
    second = original | {"timestampGMT": original["timestampGMT"] + 100}
    p.weights.append(second)
    assert get()["observations"]["created"] == 2
    stored = db.scalars(
        select(BodyWeightObservation).order_by(BodyWeightObservation.measured_at)
    ).all()
    ids = [r.id for r in stored]
    assert stored[0].mass_kg == Decimal("72.125") and stored[0].source_value == 72125
    assert stored[0].source_unit == "g" and stored[0].documented_source_unit == "kg"
    assert stored[0].verification_scope == seg.fingerprint and stored[0].time_resolution_us == 1000
    p.weights = [original | {"weight": 73500.0}, second]
    assert get()["observations"]["unresolved"] == 1
    assert stored[0].mass_kg == Decimal("72.125")
    assert day_status(db, ev.source, Category.WEIGHT, DAY)["last_eligible_count"] == 1
    held = select_weight_day(db, ev.source, DAY)
    assert (
        held.reasons == ("ambiguous_correction",)
        and not held.measurements
        and list(held.retained_ids) == ids
    )
    p.weights = []
    assert get()["categories"]["weight"]["open_issues"] == 1
    assert day_status(db, ev.source, Category.WEIGHT, DAY)["acquisition"] == "empty"
    p.weights = [original, second]
    assert get()["categories"]["weight"]["open_issues"] == 0
    p.weights = [original, original, second]
    assert get()["observations"]["unresolved"] == 2
    assert day_status(db, ev.source, Category.WEIGHT, DAY)["last_eligible_count"] == 1
    assert not select_weight_day(db, ev.source, DAY).measurements
    last_success = day_status(db, ev.source, Category.WEIGHT, DAY)["last_success"]
    p.weights = [original | {"weight": 72.125}, second]
    result = get()
    assert result["stopped"] == "weight verification required"
    assert result["observations"]["unchanged"] == 0
    assert result["categories"]["weight"]["remaining"] == 1
    partial = day_status(db, ev.source, Category.WEIGHT, DAY)
    assert partial["last_success"] == last_success and partial["last_eligible_count"] == 1
    next_day = DAY + timedelta(days=1)
    cfg["end"] = str(next_day)
    path.write_text(json.dumps(cfg))
    wider = WeightSegment.load(path, ev.source)
    route = Endpoint.WEIGHT_RANGE.value.format(day=DAY, end_day=DAY)
    p.errors[route] = 404
    interrupted = run(db, bound, (Category.WEIGHT,), end=next_day, segment=wider)
    assert interrupted["stopped"] == "not_found" and interrupted["requests"]["weight_range"] == 1
    assert day_status(db, ev.source, Category.WEIGHT, next_day)["acquisition"] == "never_queried"
    del p.errors[route]
    assert not select_weight_day(db, ev.source, DAY).measurements
    p.weights = []
    assert get()["stopped"] == "weight verification required"
    p.weights = [original, second]
    assert get()["categories"]["weight"]["open_issues"] == 0
    assert ids == [
        r.id
        for r in db.scalars(
            select(BodyWeightObservation).order_by(BodyWeightObservation.measured_at)
        )
    ]
    p.weights = [second | {"timestampGMT": second["timestampGMT"] + 200}]
    assert get()["categories"]["weight"]["open_issues"] == 1
    assert len(list(db.scalars(select(BodyWeightObservation)))) == 3
    new_stamp = original["timestampGMT"] + 100000
    p.weights = [
        original | {"timestampGMT": new_stamp},
        original | {"timestampGMT": new_stamp, "calendarDate": str(next_day)},
    ]
    crossing = run(db, bound, (Category.WEIGHT,), mode="repair", end=next_day, segment=wider)
    assert crossing["observations"]["unresolved"] == 2 and crossing["observations"]["created"] == 0
    assert "instant_collision" in select_weight_day(db, ev.source, next_day).reasons
    status = day_status(db, ev.source, Category.WEIGHT, next_day)
    assert status["acquisition"] == "observed" and status["last_eligible_count"] == 0


def test_full_page_budget_resume_and_disappearance(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    p.page_of_ten()
    cats = (Category.ACTIVITIES, Category.STEPS)
    result = run(db, bound, cats, limit=12)
    assert result["stopped"] == "budget_exhausted" and result["observations"]["created"] == 5
    state = day_status(db, ev.source, Category.ACTIVITIES, DAY)
    assert state["acquisition"] == "partial" and state["last_success"] is None
    result = run(db, bound, cats)
    assert result["stopped"] is None and result["observations"]["created"] == 5
    assert p.pages == [0, 0, 10, 0, 10]
    assert "workouts" not in result["requests"]
    assert len(list(db.scalars(select(Workout)))) == 10
    p.activity_rows = []
    result = run(db, bound, cats, mode="repair")
    assert result["categories"]["activities"]["remaining"] == 0
    assert day_status(db, ev.source, Category.ACTIVITIES, DAY)["acquisition"] == "empty"
    assert len(list(db.scalars(select(Workout)))) == 10


@pytest.mark.parametrize("mutation", ["repeat", "overlap", "order", "edit"])
def test_unstable_pagination_retains_verified_details(
    db: Session, bound: tuple[Evidence, HistoricalProvider], mutation: str
) -> None:
    ev, p = bound
    p.page_of_ten()

    def mutate(offset, page):
        if mutation == "repeat" and offset:
            return p.activity_rows
        if mutation == "overlap" and offset:
            return p.activity_rows[-1:]
        if mutation == "order" and not offset and len(p.pages) > 1:
            return list(reversed(page))
        if mutation == "edit" and not offset and len(p.pages) > 1:
            return [page[0] | {"duration": 123}, *page[1:]]
        return page

    p.mutation = mutate
    result = run(db, bound, (Category.ACTIVITIES,))
    assert result["stopped"] == "activity listing did not converge"
    assert len(list(db.scalars(select(Workout)))) == 10
    assert day_status(db, ev.source, Category.ACTIVITIES, DAY)["acquisition"] == "partial"


def test_running_steps_sparse_revision_cleanup(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    cats = (Category.ACTIVITIES, Category.STEPS)
    assert run(db, bound, cats)["requests"]["workouts"] == 1
    p.details[IDENT]["summaryDTO"] = {}
    p.details[IDENT]["metadataDTO"]["lastUpdateDate"] = "2024-12-01T10:00:00.000"
    p.activity_rows[0]["distance"] = 5678
    assert run(db, bound, cats, mode="repair")["observations"]["updated"] == 1
    activity = db.scalars(select(EnduranceActivity)).one()
    assert activity.average_hr_bpm == 120 and activity.distance_m == 5678
    p.details[IDENT]["summaryDTO"]["averageHR"] = 125
    assert run(db, bound, cats, mode="repair")["observations"]["updated"] == 1
    p.details[IDENT]["summaryDTO"]["averageHR"] = 126
    result = run(db, bound, cats, mode="repair")
    assert result["categories"]["activities"]["open_issues"] == 1
    assert activity.average_hr_bpm == 125
    assert db.scalars(select(ActivityStep)).one().duration_value == 30


@pytest.mark.parametrize("scenario", ["date", "owner", "429", "401", "sparse404"])
def test_range_validation_and_failed_progress(
    db: Session, bound: tuple[Evidence, HistoricalProvider], scenario: str
) -> None:
    ev, p = bound
    if scenario == "date":
        p.sleep_rows[0] = p.sleep | {"calendarDate": str(DAY - timedelta(days=1))}
    if scenario == "owner":
        p.sleep_rows[0] = p.sleep | {"userProfilePK": PROFILE + 1}
    if scenario in ("429", "401"):
        p.errors[Endpoint.SLEEP_RANGE] = int(scenario)
    if scenario == "sparse404":
        p.sleep_rows = []
        # Anchor remains successful. Only the different target day lacks a daily response.
        p.sleep = p.sleep | {"calendarDate": str(DAY)}
    day = DAY + timedelta(days=1) if scenario == "sparse404" else DAY
    result = run(db, bound, (Category.SLEEP,), start=day, end=day)
    assert result["stopped"] and result["requests"]["exchange"] == 1
    assert day_status(db, ev.source, Category.SLEEP, day)["acquisition"] == "failed"
    assert not db.scalars(select(DailyRecoveryObservation)).all()


def test_atomic_rollback_and_lock(db: Session, bound: tuple[Evidence, HistoricalProvider]) -> None:
    ev, p = bound

    def fail(*args):
        raise RuntimeError("injected checkpoint failure")

    event.listen(GarminCoverage, "before_insert", fail)
    try:
        with pytest.raises(RuntimeError, match="checkpoint"):
            run(db, bound, (Category.SLEEP,))
    finally:
        event.remove(GarminCoverage, "before_insert", fail)
    assert not db.scalars(select(DailyRecoveryObservation)).all()
    assert not db.scalars(select(GarminCoverage)).all()
    with locked_account(db.bind, ev.source.source_account_id):
        with pytest.raises(LocalAccountError, match="already running"):
            run(db, bound, (Category.SLEEP,))
    run(db, bound, (Category.SLEEP,))
    db.rollback()
    with pytest.raises(RuntimeError, match="preserve historical"):
        command.downgrade(Config("alembic.ini"), "b320")


def test_incremental_overlap_outstanding_and_older_repair(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    start = DAY - timedelta(days=3)

    # Documented HRV 204 covers the inclusive request.
    def empty(first: date, last: date) -> None:
        p.errors[Endpoint.HRV_RANGE.value.format(day=first, end_day=last)] = 204

    empty(start, DAY)
    run(db, bound, (Category.HRV,), start=start)
    empty(DAY - timedelta(days=1), DAY)
    pid = uuid4()
    result = run(
        db, bound, (Category.HRV,), mode="incremental", start=start, overlap=2, pass_id=pid
    )
    assert result["requests"]["hrv_range"] == 1 and result["stopped"] is None
    assert (
        "hrv_range"
        not in run(
            db, bound, (Category.HRV,), mode="incremental", start=start, overlap=2, pass_id=pid
        )["requests"]
    )
    empty(start, start)
    assert (
        run(db, bound, (Category.HRV,), mode="repair", start=start, end=start)["requests"][
            "hrv_range"
        ]
        == 1
    )


def test_narrow_intake_preserves_existing_records_and_erasure_scope(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    source = ev.source
    owner = source.owner_id
    client = GarminClient(KEY, transport=httpx.MockTransport(p.handle))
    try:
        importer = Importer(db.bind, ev, client)
        importer.run(Mode.ACTIVITIES, day=DAY, steps=True)
        importer.run(Mode.RECOVERY, day=DAY)
    finally:
        client.close()
    hevy = SourceAccount(
        user_id=owner, provider="hevy", provider_account_id="synthetic", status="active"
    )
    workout = Workout(user_id=owner, title="Synthetic", started_at=datetime(2024, 1, 1, tzinfo=UTC))
    db.add_all(
        [hevy, workout, AthleteContext(user_id=owner, sequence=1, snapshot={"synthetic": True})]
    )
    db.flush()
    db.add(
        ExternalReference(
            user_id=owner,
            provider="hevy",
            source_account_id=hevy.id,
            entity_type="workout",
            external_id="fixture",
            workout_id=workout.id,
            raw_payload={},
        )
    )
    db.commit()

    def snapshot():
        tables = (
            Workout,
            ExternalReference,
            EnduranceActivity,
            ActivitySplit,
            ActivityStep,
            DailyRecoveryObservation,
            AthleteContext,
            SourceAccount,
        )
        return {
            model.__tablename__: sorted(
                str(tuple(row))
                for row in db.execute(select(model.__table__).where(model.user_id == owner))
            )
            for model in tables
        }

    before = snapshot()
    p.food["dailyNutritionContent"]["calories"] = 2200
    result = run(db, bound, (Category.INTAKE,), mode="repair")
    assert result["observations"]["unresolved"] == 1
    assert before == snapshot()
    for model in (GarminCoverage, GarminIssue, DailyIntakeObservation):
        rows = db.execute(select(model.__table__)).all()
        assert rows and all(PRIVATE not in str(r) and KEY not in str(r) for r in rows)
        assert (
            db.execute(
                delete(model).filter_by(user_id=uuid4(), source_account_id=source.source_account_id)
            ).rowcount
            == 0
        )
        assert (
            db.execute(
                delete(model).filter_by(
                    user_id=owner, provider="garmin", source_account_id=source.source_account_id
                )
            ).rowcount
            > 0
        )
    db.commit()
    assert before == snapshot()


def test_account_expiry_after_target_read(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    now = 1_700_000_000

    def handle(req):
        nonlocal now
        response = p.handle(req)
        if req.url.path == Endpoint.DAILY_RANGE:
            now = 10_000_000_000
        return response

    client = GarminClient(KEY, transport=httpx.MockTransport(handle), clock=lambda: now)
    try:
        out = synchronize(
            db.bind, ev, client, Scope("repair", DAY, DAY, (Category.INTAKE,), uuid4())
        )
    finally:
        client.close()
    assert out["stopped"] == "verified session expired"
    assert out["requests"]["exchange"] == 1
    assert not db.scalars(select(GarminCoverage)).all()
    assert not db.scalars(select(DailyIntakeObservation)).all()


def test_range_hrv_retains_supported_chart_bounds_only(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    client = GarminClient(KEY, transport=httpx.MockTransport(p.handle))
    try:
        Importer(db.bind, ev, client).run(Mode.RECOVERY, day=DAY)
    finally:
        client.close()
    query = select(DailyRecoveryObservation).filter_by(
        user_id=ev.source.owner_id, metric="overnight_hrv"
    )
    old = db.scalars(query).one()
    initial = (old.id, old.source_field, old.window_start, old.retrieved_at)
    assert run(db, bound, (Category.HRV,))["observations"]["unchanged"] >= 1
    assert initial == (old.id, old.source_field, old.window_start, old.retrieved_at)
    p.hrv_rows = [p.hrv_rows[0] | {"lastNightAvg": 32}]
    result = run(db, bound, (Category.HRV,), mode="repair")
    assert result["observations"]["updated"] == 1
    assert old.id == initial[0] and old.window_start is None and old.window_end is None


def test_partial_category_failure_allows_independent_progress(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    p.errors[Endpoint.SLEEP_RANGE] = 503
    result = run(db, bound, (Category.SLEEP, Category.HRV))
    assert result["stopped"] == "http_error_503"
    assert result["categories"]["hrv"]["completed"] == 1
    assert day_status(db, ev.source, Category.SLEEP, DAY)["acquisition"] == "failed"
    p.errors.clear()
    resumed = run(db, bound, (Category.SLEEP, Category.HRV))
    assert resumed["stopped"] is None and "hrv_range" not in resumed["requests"]


@pytest.mark.parametrize("shape", ["duplicate", "unknown_source"])
def test_ambiguous_v2_source_falls_back(
    db: Session, bound: tuple[Evidence, HistoricalProvider], shape: str
) -> None:
    ev, p = bound
    p.v2[0]["calories"]["consumedValue"] = 1000
    if shape == "duplicate":
        p.v2.append(p.v2[0])
    else:
        p.v2[0]["source"] = "unverified"
    result = run(db, bound, (Category.INTAKE,))
    selected = select_daily_intake(db, ev.source.owner_id, DAY)
    assert (
        result["stopped"] is None
        and selected.reported_kcal == 1900
        and len(selected.observation_ids) == 2
    )


def test_full_then_short_page_and_verified_anchor_failure(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    p.page_of_ten()
    row = deepcopy(p.activity_rows[-1])
    row.update(
        activityId=IDENT + 10, startTimeLocal=f"{DAY} 11:00:00", startTimeGMT=f"{DAY} 15:00:00"
    )
    p.details[IDENT + 10] = p.details[IDENT] | {"activityId": IDENT + 10}
    p.activity_rows.append(row)
    assert run(db, bound, (Category.ACTIVITIES,))["observations"]["created"] == 11
    assert p.pages == [0, 10, 0, 10]
    p.summaries[DAY][0]["ownerId"] += 1
    result = run(db, bound, (Category.SLEEP,))
    assert result["stopped"] and result["requests"] == {"exchange": 1, "activities": 1}
    assert day_status(db, ev.source, Category.SLEEP, DAY)["acquisition"] == "never_queried"


def test_short_refresh_fills_old_gap(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    end = DAY + timedelta(days=4)
    gap = DAY + timedelta(days=1)
    for a, b in ((DAY, DAY), (gap, gap), (gap + timedelta(days=1), end), (end, end)):
        p.errors[Endpoint.HRV_RANGE.value.format(day=a, end_day=b)] = 204
    assert run(db, bound, (Category.HRV,))["stopped"] is None
    assert (
        run(db, bound, (Category.HRV,), start=gap + timedelta(days=1), end=end)["stopped"] is None
    )
    result = run(db, bound, (Category.HRV,), mode="incremental", start=DAY, end=end, overlap=1)
    assert result["requests"]["hrv_range"] == 2
    assert result["categories"]["hrv"]["completed"] == 5


def test_unexpected_v2_presence_and_sparse_single_day_failure(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    p.v2[0]["calories"]["includesCalorieConsumedData"] = False
    result = run(db, bound, (Category.INTAKE,))
    assert result["stopped"] == "unreviewed v2 intake presence"
    assert not db.scalars(select(DailyIntakeObservation)).all()
    p.v2 = []
    # An absence on an unverified food route cannot prove a queried-empty intake day.
    p.errors[Endpoint.FOOD.value.format(day=DAY)] = 404
    result = run(db, bound, (Category.INTAKE,))
    assert result["stopped"] == "not_found"
    assert day_status(db, ev.source, Category.INTAKE, DAY)["acquisition"] == "partial"


def test_unavailable_day_allows_resume_and_repair(
    db: Session, bound: tuple[Evidence, HistoricalProvider], monkeypatch: pytest.MonkeyPatch
) -> None:
    ev, p = bound
    gap = DAY + timedelta(days=1)
    last = gap + timedelta(days=2)
    original = p.handle
    offline = True
    requests = []

    def by_date(req: httpx.Request) -> httpx.Response:
        if req.url.path == Endpoint.DAILY and req.url.params["calendarDate"] != str(DAY):
            d = req.url.params["calendarDate"]
            requests.append(d)
            if offline and d == str(gap):
                return httpx.Response(404)
            return httpx.Response(200, json=dict(p.daily, calendarDate=d))
        return original(req)

    monkeypatch.setattr(p, "handle", by_date)
    categories = (Category.RESTING,)
    result = run(db, bound, categories, start=gap, end=last, limit=8)
    assert requests == [str(gap), str(gap + timedelta(days=1))]
    assert result["categories"]["resting_hr"]["completed"] == 1
    requests.clear()
    resumed = run(db, bound, categories, start=gap, end=last, limit=7)
    assert requests == [str(last)]
    status = resumed["categories"]["resting_hr"]
    assert (status["completed"], status["remaining"], status["resume"]) == (2, 1, str(gap))
    assert day_status(db, ev.source, Category.RESTING, gap)["acquisition"] == "failed"
    assert status["completed_through"] is None
    assert status["gaps"] == [[str(gap), str(gap)]]
    assert run(db, bound, categories, start=gap, end=last)["stopped"] == "not_found"
    offline = False
    repaired = run(db, bound, categories, mode="repair", start=gap, end=gap)
    assert repaired["observations"]["created"] == 1
    final = run(db, bound, categories, start=gap, end=last)
    assert final["categories"]["resting_hr"]["completed_through"] == str(last)
    assert final["categories"]["resting_hr"]["gaps"] == []


def test_daily_total_survives_unavailable_food(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    p.v2 = []
    p.errors[Endpoint.FOOD.value.format(day=DAY)] = 404
    out = run(db, bound, (Category.INTAKE,))
    assert out["observations"]["created"] == 1
    selected = select_daily_intake(db, ev.source.owner_id, DAY)
    assert selected.reported_kcal == 1900 and selected.completeness == "unknown"
    assert day_status(db, ev.source, Category.INTAKE, DAY)["acquisition"] == "partial"
    row = db.scalars(select(DailyIntakeObservation)).one()
    assert row.upstream_writer is None


def test_conflict_waits_for_unavailable_corroboration(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    cats = (Category.INTAKE,)
    p.daily["consumedKilocalories"] = 2050
    assert run(db, bound, cats, mode="repair")["categories"]["intake"]["open_issues"] == 1
    p.daily["consumedKilocalories"] = 1900
    p.errors[Endpoint.FOOD.value.format(day=DAY)] = 404
    run(db, bound, cats, mode="repair")
    retained = db.scalars(select(DailyIntakeObservation.reported_kcal)).all()
    assert retained == [1900] * 3
    assert day_status(db, ev.source, Category.INTAKE, DAY)["reconciliation"] == "unresolved"
    assert select_daily_intake(db, ev.source.owner_id, DAY).status == "conflict"
    p.errors.clear()
    repaired = run(db, bound, cats)
    assert repaired["requests"]["food"] == 1
    assert repaired["categories"]["intake"]["open_issues"] == 0
    assert select_daily_intake(db, ev.source.owner_id, DAY).reported_kcal == 1900


@pytest.mark.parametrize("fallback_status", [404, 503])
def test_unavailable_daily_intake_preserves_other_sources_and_later_day(
    db: Session,
    bound: tuple[Evidence, HistoricalProvider],
    monkeypatch: pytest.MonkeyPatch,
    fallback_status: int,
) -> None:
    ev, p = bound
    first = DAY + timedelta(days=1)
    last = first + timedelta(days=1)
    original = p.handle

    def dated(req: httpx.Request) -> httpx.Response:
        path = req.url.path
        if path == Endpoint.DAILY_RANGE:
            return httpx.Response(
                200, json={"data": [dict(p.v2[0], calendarDate=str(d)) for d in (first, last)]}
            )
        if path == Endpoint.DAILY and req.url.params["calendarDate"] == str(first):
            return httpx.Response(fallback_status)
        if path == Endpoint.DAILY and req.url.params["calendarDate"] == str(last):
            return httpx.Response(200, json=dict(p.daily, calendarDate=str(last)))
        if path.startswith("/nutrition-service/food/logs/"):
            return httpx.Response(200, json=dict(p.food, mealDate=path.rsplit("/", 1)[-1]))
        return original(req)

    monkeypatch.setattr(p, "handle", dated)
    result = run(db, bound, (Category.INTAKE,), mode="repair", start=first, end=last)
    assert result["categories"]["intake"]["gaps"] == [[str(first), str(first)]]
    assert result["requests"]["food"] == 2 and result["requests"]["daily"] == 3
    status = day_status(db, ev.source, Category.INTAKE, first)
    assert status["acquisition"] == "partial" and status["sources"] == {
        "v2": "observed",
        "daily": "unavailable",
        "food": "observed",
    }
    assert day_status(db, ev.source, Category.INTAKE, last)["acquisition"] == "observed"
    selected = select_daily_intake(db, ev.source.owner_id, first)
    assert selected.reported_kcal == 1900 and len(selected.observation_ids) == 2


def test_unsupported_zero_with_missing_corroboration(
    db: Session, bound: tuple[Evidence, HistoricalProvider]
) -> None:
    ev, p = bound
    p.v2[0]["calories"]["consumedValue"] = 0
    p.daily["consumedKilocalories"] = 0
    p.errors[Endpoint.FOOD.value.format(day=DAY)] = 404
    result = run(db, bound, (Category.INTAKE,))
    assert result["observations"]["created"] == 0
    status = day_status(db, ev.source, Category.INTAKE, DAY)
    assert status["acquisition"] == "partial" and status["last_success"] is None
    assert status["sources"] == {"v2": "no_eligible", "daily": "no_eligible", "food": "unavailable"}
    p.food = {"mealDate": str(DAY)}
    p.errors.clear()
    run(db, bound, (Category.INTAKE,))
    status = day_status(db, ev.source, Category.INTAKE, DAY)
    assert status["acquisition"] == "empty" and set(status["sources"].values()) == {"no_eligible"}
    assert select_daily_intake(db, ev.source.owner_id, DAY).status == "missing"


@pytest.mark.parametrize(("code", "expected"), [(404, 2), (503, 2), (401, 1), (403, 1), (429, 1)])
def test_dated_outage_and_context_limits(
    db: Session,
    bound: tuple[Evidence, HistoricalProvider],
    monkeypatch: pytest.MonkeyPatch,
    code: int,
    expected: int,
) -> None:
    ev, p = bound
    first = DAY + timedelta(days=1)
    end = first + timedelta(days=5)
    attempts = []
    original = p.handle

    def outage(req: httpx.Request) -> httpx.Response:
        if req.url.path == Endpoint.DAILY and req.url.params["calendarDate"] != str(DAY):
            attempts.append(req.url.params["calendarDate"])
            return httpx.Response(code)
        return original(req)

    monkeypatch.setattr(p, "handle", outage)
    result = run(db, bound, (Category.RESTING,), start=first, end=end)
    assert len(attempts) == len(set(attempts)) == expected
    assert (
        result["requests"]["exchange"] == 1 and result["categories"]["resting_hr"]["completed"] == 0
    )
    assert day_status(db, ev.source, Category.RESTING, end)["acquisition"] == "never_queried"


def test_persistent_gap_leaves_budget_for_other_category(
    db: Session, bound: tuple[Evidence, HistoricalProvider], monkeypatch: pytest.MonkeyPatch
) -> None:
    ev, p = bound
    target = DAY + timedelta(days=1)
    original = p.handle

    def dated(req: httpx.Request) -> httpx.Response:
        if req.url.path == Endpoint.DAILY and req.url.params["calendarDate"] == str(target):
            return httpx.Response(404)
        return original(req)

    monkeypatch.setattr(p, "handle", dated)
    p.errors[Endpoint.HRV_RANGE.value.format(day=target, end_day=target)] = 204
    cats = (Category.RESTING, Category.HRV)
    run(db, bound, cats, start=target, end=target, limit=7)
    second = run(db, bound, cats, start=target, end=target, limit=7)
    assert second["requests"]["hrv_range"] == 1
    assert day_status(db, ev.source, Category.RESTING, target)["acquisition"] == "failed"
    assert day_status(db, ev.source, Category.HRV, target)["acquisition"] == "empty"

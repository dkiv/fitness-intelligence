"""Bounded operator workflow using invented DTOs, mock HTTP, and isolated PostgreSQL."""

import json
import logging
import sys
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event, select, text
from sqlalchemy.orm import Session
from test_garmin import jwt

from fitness_intelligence.adapters.garmin import cli
from fitness_intelligence.adapters.garmin.binding import ComparisonError, Evidence, Feed, verify
from fitness_intelligence.adapters.garmin.client import (
    TOKEN_PATH,
    Endpoint,
    GarminClient,
    GarminError,
)
from fitness_intelligence.adapters.garmin.importer import Importer, Mode
from fitness_intelligence.adapters.garmin.mapping import GarminBinding, MappingError
from fitness_intelligence.adapters.garmin.projection import replay_activity
from fitness_intelligence.adapters.local_account import LocalAccountError, locked_account
from fitness_intelligence.db.endurance_models import (
    ActivitySplit,
    ActivityStep,
    DailyRecoveryObservation,
    EnduranceActivity,
)
from fitness_intelligence.db.models import ExternalReference, SourceAccount, User, Workout
from fitness_intelligence.domain.endurance import Source

DAY = date(2024, 11, 3)
OTHER_DAY = DAY + timedelta(days=1)
UPDATE = "2024-11-05T01:00:00.123"
PRIVATE = "fictional-unrelated-private-field"
KEY = "fictional-credential"
PROFILE = 87321456
IDENT = 7432156


class Provider:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.summaries: dict[date, list[dict]] = {
            DAY: [
                dict(
                    activityId=IDENT,
                    ownerId=PROFILE,
                    activityType={"typeKey": "running"},
                    startTimeGMT="2024-11-04 03:30:00",
                    startTimeLocal="2024-11-03 22:30:00",
                    beginTimestamp=1730691000123,
                    activityName=PRIVATE,
                    startLatitude=45.12345,
                    duration=600,
                    distance="wire-decimal",
                )
            ]
        }
        self.details = {
            IDENT: dict(
                activityId=IDENT,
                userProfileId=PROFILE,
                metadataDTO={"lastUpdateDate": UPDATE},
                summaryDTO={"averageHR": 120},
                splitSummaries=[{"splitType": "RUN_ACTIVE", "noOfSplits": 2, "distance": 12.3}],
            )
        }
        self.steps: list[dict] = [
            {
                "index": 0,
                "sport": "RUNNING",
                "steps": [
                    {
                        "stepIndex": 1,
                        "durationType": "TIME",
                        "durationValue": 30,
                        "stepName": PRIVATE,
                    }
                ],
            }
        ]
        self.daily = dict(
            userProfileId=PROFILE,
            calendarDate=str(DAY),
            totalKilocalories=1700,
            activeKilocalories=200,
            bmrKilocalories=1500,
            restingHeartRate=52,
            calorieGoal=PRIVATE,
            wellnessStartTimeGmt="2024-11-03T04:00:00Z",
            wellnessEndTimeGmt="2024-11-04T05:00:00Z",
        )
        self.sleep = dict(
            userProfilePK=PROFILE,
            calendarDate=str(DAY),
            sleepTimeSeconds=20000,
            lightSleepSeconds=10000,
            deepSleepSeconds=5000,
            remSleepSeconds=5000,
            awakeSleepSeconds=0,
            sleepStartTimestampGMT="2024-11-02T23:00:00-04:00",
            sleepEndTimestampGMT="2024-11-03T05:00:00-05:00",
        )
        self.hrv = dict(
            userProfilePk=PROFILE,
            hrvSummary={"calendarDate": str(DAY), "weeklyAvg": 28, "lastNightAvg": 30},
            startTimestampGMT="2024-11-03T03:00:00.000",
            endTimestampGMT="2024-11-03T10:00:00.000",
            hrvReadings=[PRIVATE],
        )
        self.errors: dict[str, int] = {}

    def handle(self, req: httpx.Request) -> httpx.Response:
        path, params = req.url.path, req.url.params
        self.calls.append(path)
        if path == TOKEN_PATH:
            assert req.method == "POST"
            return httpx.Response(200, text=jwt(9999999999))
        assert req.method == "GET"
        if path in self.errors:
            return httpx.Response(self.errors[path], text=PRIVATE)
        payload: Any
        if path == Endpoint.ACTIVITIES:
            assert params["startDate"] == params["endDate"]
            assert params["limit"] == "3" and params["start"] == "0"
            payload = self.summaries.get(date.fromisoformat(params["endDate"]), [])
        elif path.endswith("/workouts"):
            assert int(path.split("/")[-2]) in self.details
            payload = self.steps
        elif path.startswith("/activity-service/"):
            payload = self.details[int(path.split("/")[-1])]
        elif path == Endpoint.DAILY:
            assert "calendarDate" in params
            payload = self.daily
        elif path == Endpoint.SLEEP:
            assert "date" in params
            payload = self.sleep
        elif path.startswith("/hrv-service/"):
            payload = self.hrv
        else:
            raise AssertionError("unrequested endpoint")
        body = json.dumps(payload).replace('"wire-decimal"', "987654321098.1234567894")
        return httpx.Response(200, content=body)


def evidence(user: User) -> Evidence:
    return Evidence(
        GarminBinding(Source(user.id, "garmin", uuid4()), PROFILE), IDENT, DAY, tuple(Feed), True
    )


@pytest.fixture
def setup(db: Session) -> Iterator[tuple[Importer, Provider]]:
    user = User()
    db.add(user)
    db.commit()
    provider = Provider()
    client = GarminClient(KEY, transport=httpx.MockTransport(provider.handle))
    try:
        yield Importer(db.bind, evidence(user), client), provider
    finally:
        client.close()


def enroll(importer: Importer) -> None:
    assert importer.run(Mode.ENROLL) == {"enrolled": 1}


def test_verify_enroll_and_replacement(db: Session, setup: tuple[Importer, Provider]) -> None:
    importer, provider = setup
    writes = []

    def audit(conn: Any, cur: Any, sql: str, params: Any, ctx: Any, many: bool) -> None:
        if not sql.lstrip().upper().startswith("SELECT"):
            writes.append(sql.split()[0])

    event.listen(db.bind, "before_cursor_execute", audit)
    try:
        assert importer.run(Mode.VERIFY)["hrv_matched"] == 1
    finally:
        event.remove(db.bind, "before_cursor_execute", audit)
    assert not writes and db.scalar(select(SourceAccount)) is None
    assert len(provider.calls) == 6
    assert Endpoint.WORKOUTS not in provider.calls
    unconfirmed = Importer(
        db.bind, replace(importer.evidence, durability_confirmed=False), importer.client
    )
    with pytest.raises(GarminError, match="durability"):
        unconfirmed.run(Mode.ENROLL)
    enroll(importer)
    assert importer.run(Mode.ENROLL) == {"already_enrolled": 1}

    replacement = GarminClient("synthetic-new-key", transport=httpx.MockTransport(provider.handle))
    try:
        rotated = Importer(db.bind, importer.evidence, replacement)
        assert rotated.run(Mode.RECOVERY, day=DAY)["created"] == 11
        provider.hrv["userProfilePk"] += 1
        with pytest.raises(ComparisonError, match="hrv: mismatch"):
            rotated.run(Mode.ACTIVITIES, day=DAY)
        assert db.scalar(select(Workout.id)) is None
    finally:
        replacement.close()


def test_activity_replay_edit_sparse_and_privacy(
    db: Session, setup: tuple[Importer, Provider]
) -> None:
    importer, provider = setup
    enroll(importer)

    def run(steps: bool = True) -> dict[str, int]:
        client = GarminClient(KEY, transport=httpx.MockTransport(provider.handle))
        try:
            result = Importer(db.bind, importer.evidence, client).run(
                Mode.ACTIVITIES, day=DAY, steps=steps
            )
        finally:
            client.close()
        db.expire_all()
        return result

    assert run()["created"] == 1
    ref = db.scalars(select(ExternalReference)).one()
    activity = db.scalars(select(EnduranceActivity)).one()
    workout = db.scalars(select(Workout)).one()
    identity = (workout.id, ref.id, ref.first_imported_at)
    assert workout.started_at == datetime(2024, 11, 4, 3, 30, 0, 123000, tzinfo=UTC)
    assert activity.local_date == DAY
    assert ref.source_updated_at == datetime.fromisoformat(UPDATE).replace(tzinfo=UTC)
    assert ref.last_synced_at != ref.source_updated_at
    assert activity.distance_m == Decimal("987654321098.123456789")
    assert (
        ref.sync_metadata["fields"]["average_hr_bpm"]["source"]
        == "ActivitySummaryDTO.summaryDTO.averageHR"
    )
    stored = json.dumps([ref.raw_payload, ref.sync_metadata, workout.title])
    for forbidden in (
        PRIVATE,
        KEY,
        str(PROFILE),
        "startLatitude",
        "activityName",
        "45.12345",
        "userProfileId",
    ):
        assert forbidden not in stored
    replayed = replay_activity(importer.evidence.binding, ref)
    with pytest.raises(MappingError, match="invalid replay reference"):
        replay_activity(
            replace(
                importer.evidence.binding,
                source=replace(importer.evidence.binding.source, source_account_id=uuid4()),
            ),
            ref,
        )
    assert replayed.distance_m == activity.distance_m
    assert replayed.started_at == workout.started_at and replayed.splits[0].count == 2
    assert replayed.steps[0].duration_value == 30
    assert ref.raw_payload["source"]["search"]["distance"] == {"decimal": "987654321098.1234567894"}
    assert run()["unchanged"] == 1
    assert db.scalars(select(ActivityStep.duration_value)).one() == 30
    assert db.scalars(select(ActivitySplit.count)).one() == 2

    summary = provider.summaries[DAY][0]
    detail = provider.details[IDENT]
    original_splits = detail.pop("splitSummaries")
    for key in ("activityType", "duration", "beginTimestamp"):
        del summary[key]
    summary["distance"] = 0
    detail["metadataDTO"]["lastUpdateDate"] = "2024-11-06T01:00:00.000"
    provider.steps = [{"index": 0}]
    assert run()["updated"] == 1
    assert activity.sport == "running" and activity.duration_s == 600 and activity.distance_m == 0
    assert workout.started_at.microsecond == 123000
    assert db.scalars(select(ActivityStep.duration_value)).one() == 30
    assert db.scalars(select(ActivitySplit.count)).one() == 2

    detail["splitSummaries"] = [{"splitType": "RUN_ACTIVE", "distance": 5}]
    assert run(steps=False)["partial"] == 1
    assert db.scalars(select(ActivitySplit.distance_m)).one() == Decimal("12.3")
    detail["splitSummaries"] = []
    detail["metadataDTO"]["lastUpdateDate"] = "2024-11-07T01:00:00.000"
    provider.steps = []
    assert run()["updated"] == 1
    assert ref.raw_payload["canonical"]["splits"] == ref.raw_payload["canonical"]["steps"] == []
    assert db.scalar(select(ActivitySplit)) is None and db.scalar(select(ActivityStep)) is None
    detail["splitSummaries"] = original_splits
    detail["metadataDTO"]["lastUpdateDate"] = UPDATE
    assert run()["older"] == 1
    detail["metadataDTO"] = {}
    assert run()["unresolved"] == 1
    assert (workout.id, ref.id, ref.first_imported_at) == identity
    assert db.scalars(select(Workout.id)).all() == [workout.id]
    assert importer.run(Mode.ACTIVITIES, day=OTHER_DAY) == {"observed": 0}
    assert db.scalar(select(Workout.deleted_at)) is None


def test_recovery_replay_edit_sparse_and_rollback(
    db: Session, setup: tuple[Importer, Provider]
) -> None:
    importer, provider = setup
    enroll(importer)
    assert importer.run(Mode.RECOVERY, day=DAY) == {"observed": 11, "created": 11}
    records = {row.metric: row for row in db.scalars(select(DailyRecoveryObservation))}
    ids = {k: row.id for k, row in records.items()}
    assert records["sleep_duration"].window_start == datetime(2024, 11, 3, 3, tzinfo=UTC)
    assert records["sleep_duration"].window_end == datetime(2024, 11, 3, 10, tzinfo=UTC)
    assert records["awake_during_sleep"].value == 0
    assert records["seven_day_hrv"].window_start is None
    assert records["overnight_hrv"].unit == "source_unit_unverified"
    assert records["overnight_hrv"].source_field == "HrvChartDTO.hrvSummary.lastNightAvg"
    assert records["overnight_hrv"].retrieved_at != records["overnight_hrv"].window_end
    assert importer.run(Mode.RECOVERY, day=DAY)["unchanged"] == 11
    provider.daily = dict(userProfileId=PROFILE, calendarDate=str(DAY), totalKilocalories=0)
    provider.sleep.pop("sleepTimeSeconds")
    provider.hrv["hrvSummary"]["lastNightAvg"] = None
    assert importer.run(Mode.RECOVERY, day=DAY)["updated"] == 1
    db.expire_all()
    assert records["total_expenditure"].value == 0 and records["resting_hr"].value == 52
    assert records["sleep_duration"].value == 20000 and records["overnight_hrv"].value == 30
    assert {row.metric: row.id for row in db.scalars(select(DailyRecoveryObservation))} == ids
    provider.errors[Endpoint.SLEEP] = 503
    provider.daily["totalKilocalories"] = 999
    with pytest.raises(GarminError):
        importer.run(Mode.RECOVERY, day=DAY)
    assert records["total_expenditure"].value == 0


def test_atomic_page_failures(db: Session, setup: tuple[Importer, Provider]) -> None:
    importer, provider = setup
    enroll(importer)
    importer.run(Mode.ACTIVITIES, day=DAY)
    before = db.scalars(select(ExternalReference)).one()
    original_sync = before.last_synced_at
    known = provider.summaries[DAY][0]
    second = IDENT + 1
    provider.details[second] = dict(provider.details[IDENT], activityId=second)
    provider.summaries[DAY] = [dict(known, activityId=second), known]
    provider.errors[Endpoint.DETAIL.value.format(activity_id=second)] = 404
    with pytest.raises(GarminError, match="not_found"):
        importer.run(Mode.ACTIVITIES, day=DAY)
    assert db.scalars(select(ExternalReference.id)).all() == [before.id]
    provider.errors.clear()
    # The new first activity has flushed before the second conflicts. Both must roll back.
    known["distance"] = 250
    with pytest.raises(GarminError, match="conflicting activity version"):
        importer.run(Mode.ACTIVITIES, day=DAY)
    db.expire_all()
    assert db.scalars(select(ExternalReference.id)).all() == [before.id]
    assert db.scalars(select(Workout.id)).all() == [before.workout_id]
    assert before.last_synced_at == original_sync
    assert db.scalar(select(EnduranceActivity.distance_m)) == Decimal("987654321098.123456789")
    assert db.scalars(select(ActivitySplit.distance_m)).all() == [Decimal("12.3")]


@pytest.mark.parametrize(
    "failure",
    [
        "search_owner",
        "detail_owner",
        "detail_id",
        "daily",
        "sleep",
        "hrv",
        "date",
        "missing_date",
        "no_content",
        "duplicate",
        "over_limit",
        "off_day",
        "missing_anchor",
    ],
)
def test_reject_inconclusive_evidence(failure: str) -> None:
    provider = Provider()
    page = provider.summaries[DAY]
    if failure == "search_owner":
        page[0]["ownerId"] += 1
    elif failure == "detail_owner":
        provider.details[IDENT].pop("userProfileId")
    elif failure == "detail_id":
        provider.details[IDENT]["activityId"] += 1
    elif failure == "daily":
        provider.daily["userProfileId"] = True
    elif failure == "sleep":
        provider.sleep["userProfilePK"] += 1
    elif failure == "hrv":
        provider.hrv["userProfilePk"] = str(PROFILE)
    elif failure == "date":
        provider.hrv["hrvSummary"]["calendarDate"] = str(OTHER_DAY)
    elif failure == "missing_date":
        provider.hrv.pop("hrvSummary")
    elif failure == "no_content":
        provider.errors[Endpoint.HRV.value.format(day=DAY)] = 204
    elif failure == "duplicate":
        page.append(page[0])
    elif failure == "over_limit":
        page.extend([page[0]] * 3)
    elif failure == "off_day":
        page[0]["startTimeLocal"] = "2024-11-04 00:00:00"
    else:
        page.clear()
    client = GarminClient(KEY, transport=httpx.MockTransport(provider.handle))
    try:
        with pytest.raises((MappingError, GarminError)):
            verify(client, evidence(User(id=uuid4())))
        assert client.requests <= 6
    finally:
        client.close()


def test_lock_and_owner_isolation(db: Session, setup: tuple[Importer, Provider]) -> None:
    importer, provider = setup
    enroll(importer)
    original = importer.evidence.binding.source
    with locked_account(db.bind, original.source_account_id):
        calls = len(provider.calls)
        with pytest.raises(LocalAccountError, match="already running"):
            importer.run(Mode.RECOVERY, day=DAY)
        assert len(provider.calls) == calls
    importer.run(Mode.ACTIVITIES, day=DAY)
    importer.run(Mode.RECOVERY, day=DAY)
    first_id = db.scalar(select(Workout.id))
    other_user = User()
    db.add(other_user)
    db.commit()
    for same_owner in (True, False):
        owner = original.owner_id if same_owner else other_user.id
        account_id = uuid4()
        source = Source(owner, "garmin", account_id)
        profile = PROFILE + (1 if same_owner else 2)
        second = replace(importer.evidence, binding=GarminBinding(source, profile))
        p = Provider()
        p.summaries[DAY][0]["ownerId"] = p.details[IDENT]["userProfileId"] = profile
        p.summaries[DAY][0]["distance"] = 123
        p.daily["userProfileId"] = p.hrv["userProfilePk"] = p.sleep["userProfilePK"] = profile
        p.daily["restingHeartRate"] = 40
        client = GarminClient(KEY, transport=httpx.MockTransport(p.handle))
        try:
            local = Importer(db.bind, second, client)
            enroll(local)
            local.run(Mode.ACTIVITIES, day=DAY)
            local.run(Mode.RECOVERY, day=DAY)
        finally:
            client.close()
        ref = db.scalars(
            select(ExternalReference).filter_by(
                user_id=owner, source_account_id=account_id, external_id=str(IDENT)
            )
        ).one()
        assert ref.workout_id != first_id
        assert (
            db.scalar(
                select(DailyRecoveryObservation.value).filter_by(
                    user_id=owner, source_account_id=account_id, metric="resting_hr"
                )
            )
            == 40
        )
    assert db.scalar(
        select(EnduranceActivity.distance_m).filter_by(workout_id=first_id)
    ) == Decimal("987654321098.123456789")
    assert (
        db.scalar(
            select(DailyRecoveryObservation.value).filter_by(
                source_account_id=original.source_account_id, metric="resting_hr"
            )
        )
        == 52
    )
    for wrong in (
        replace(original, owner_id=other_user.id),
        replace(original, source_account_id=uuid4()),
    ):
        local = Importer(
            db.bind,
            replace(importer.evidence, binding=GarminBinding(wrong, PROFILE)),
            importer.client,
        )
        with pytest.raises((MappingError, GarminError)):
            local.run(Mode.ACTIVITIES, day=DAY)

    acc = db.get(SourceAccount, original.source_account_id)
    acc.status = "disconnected"
    db.commit()
    calls = len(provider.calls)
    for mode in Mode:
        with pytest.raises((MappingError, GarminError)):
            importer.run(mode, day=DAY if mode in (Mode.ACTIVITIES, Mode.RECOVERY) else None)
    assert calls == len(provider.calls)


def test_disconnect_during_network_reads(db: Session, setup: tuple[Importer, Provider]) -> None:
    importer, provider = setup
    enroll(importer)

    def disconnect(req: httpx.Request) -> httpx.Response:
        if req.url.path == Endpoint.SLEEP:
            account = db.get(SourceAccount, importer.evidence.binding.source.source_account_id)
            account.status = "disconnected"
            db.commit()
        return provider.handle(req)

    client = GarminClient(KEY, transport=httpx.MockTransport(disconnect))
    try:
        with pytest.raises((MappingError, GarminError)):
            Importer(db.bind, importer.evidence, client).run(Mode.RECOVERY, day=DAY)
    finally:
        client.close()
    assert db.scalar(select(DailyRecoveryObservation)) is None


@pytest.mark.parametrize("bad_json", [b'{"ownerId":1,"ownerId":2}', b"[NaN]", b"[Infinity]"])
def test_ambiguous_json(bad_json: bytes) -> None:
    def handle(req: httpx.Request) -> httpx.Response:
        return (
            httpx.Response(200, text=jwt(9999999999))
            if req.method == "POST"
            else httpx.Response(200, content=bad_json)
        )

    client = GarminClient(KEY, transport=httpx.MockTransport(handle))
    try:
        with pytest.raises(GarminError, match="invalid_json"):
            client.read(Endpoint.ACTIVITIES)
    finally:
        client.close()


def test_cli_rehearsal_and_privacy(
    db: Session,
    setup: tuple[Importer, Provider],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    importer, provider = setup
    file = tmp_path / "operator.json"
    src = importer.evidence.binding.source
    config = dict(
        user_id=str(src.owner_id),
        source_account_id=str(src.source_account_id),
        profile_id=PROFILE,
        known_activity_id=IDENT,
        known_day=str(DAY),
        independent_profile_confirmed=True,
        durability_confirmed=True,
        feeds=["daily"],
    )
    file.write_text(json.dumps(config))
    file.chmod(0o600)
    monkeypatch.delenv("SSLKEYLOGFILE", raising=False)
    monkeypatch.setattr(cli, "keychain_key", lambda: KEY)
    monkeypatch.setattr(
        cli,
        "GarminClient",
        lambda key: GarminClient(key, transport=httpx.MockTransport(provider.handle)),
    )
    caplog.set_level(logging.DEBUG)

    def run(*args: str) -> int:
        monkeypatch.setattr(sys, "argv", ["fi-garmin", "--binding", str(file), *args])
        return cli.main()

    for mode in (Mode.VERIFY, Mode.ENROLL):
        assert run(mode) == 0
    assert run("activities", "--day", str(DAY), "--steps") == 0
    assert run("recovery", "--day", str(DAY)) == 0
    assert Endpoint.SLEEP not in provider.calls
    provider.daily["userProfileId"] += 1
    assert run("recovery", "--day", str(DAY)) == 1
    output = capsys.readouterr()
    assert "daily: mismatch" in output.err
    for secret in (KEY, PRIVATE, str(PROFILE), str(IDENT), str(DAY), "987654321098"):
        assert secret not in caplog.text + output.out + output.err
    count = len(provider.calls)
    file.chmod(0o644)
    assert run("verify-only") == 1
    file.chmod(0o600)
    file.write_text(json.dumps(config | {"independent_profile_confirmed": False}))
    assert run("enroll") == 1
    file.write_text(json.dumps(config))
    monkeypatch.setenv("SSLKEYLOGFILE", str(tmp_path / "tls"))
    assert run("verify-only") == 1
    assert count == len(provider.calls)


def test_recovery_provenance_downgrade_guard(db: Session, setup: tuple[Importer, Provider]) -> None:
    importer, _ = setup
    enroll(importer)
    importer.run(Mode.RECOVERY, day=DAY)
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    with pytest.raises(RuntimeError, match="preserve recovery provenance"):
        command.downgrade(config, "b201")
    assert db.scalar(text("SELECT version_num FROM alembic_version")) == "b301"
    assert db.scalar(select(DailyRecoveryObservation.source_field).limit(1))


def test_separate_import_day_and_hrv_no_content(
    db: Session, setup: tuple[Importer, Provider]
) -> None:
    importer, provider = setup
    enroll(importer)
    other = Provider()
    other.summaries[OTHER_DAY] = [
        dict(
            other.summaries[DAY][0],
            activityId=IDENT + 1,
            startTimeLocal="2024-11-04 22:30:00",
            startTimeGMT="2024-11-05 03:30:00",
            beginTimestamp=None,
        )
    ]
    other.details[IDENT + 1] = dict(other.details[IDENT], activityId=IDENT + 1)
    other.daily["calendarDate"] = other.sleep["calendarDate"] = str(OTHER_DAY)
    other.hrv["hrvSummary"]["calendarDate"] = str(OTHER_DAY)

    def handle(req: httpx.Request) -> httpx.Response:
        if str(OTHER_DAY) in str(req.url) or str(IDENT + 1) in req.url.path:
            return other.handle(req)
        return provider.handle(req)

    client = GarminClient(KEY, transport=httpx.MockTransport(handle))
    try:
        local = Importer(db.bind, importer.evidence, client)
        result = local.run(Mode.ACTIVITIES, day=OTHER_DAY, steps=True)
        assert result == {"observed": 1, "created": 1}
        assert db.scalar(select(ExternalReference.external_id)) == str(IDENT + 1)
        assert other.calls.count(Endpoint.ACTIVITIES) == 1
        assert db.scalar(select(EnduranceActivity.local_date)) == OTHER_DAY
        local.run(Mode.RECOVERY, day=OTHER_DAY)
        other.errors[Endpoint.HRV.value.format(day=OTHER_DAY)] = 204
        result = local.run(Mode.RECOVERY, day=OTHER_DAY)
        assert result == {"observed": 9, "feeds_without_content": 1, "unchanged": 9}
        assert (
            len(db.scalars(select(DailyRecoveryObservation).filter_by(local_date=OTHER_DAY)).all())
            == 11
        )
        other.daily["userProfileId"] += 1
        with pytest.raises(ComparisonError, match="mismatch"):
            local.run(Mode.RECOVERY, day=OTHER_DAY)
    finally:
        client.close()


def test_same_start_in_hevy_keeps_separate_workout(
    db: Session, setup: tuple[Importer, Provider]
) -> None:
    importer, _ = setup
    owner = importer.evidence.binding.source.owner_id
    started = datetime(2024, 11, 4, 3, 30, 0, 123000, tzinfo=UTC)
    hevy = SourceAccount(
        user_id=owner, provider="hevy", provider_account_id="synthetic", status="active"
    )
    workout = Workout(user_id=owner, started_at=started, title="Synthetic strength session")
    db.add_all([hevy, workout])
    db.flush()
    ref = ExternalReference(
        user_id=owner,
        source_account_id=hevy.id,
        provider="hevy",
        entity_type="workout",
        workout_id=workout.id,
        external_id=str(IDENT),
        raw_payload={},
    )
    db.add(ref)
    db.commit()
    enroll(importer)
    importer.run(Mode.ACTIVITIES, day=DAY)
    assert (
        len(db.scalars(select(Workout.id).filter_by(user_id=owner, started_at=started)).all()) == 2
    )
    assert db.scalar(select(EnduranceActivity.workout_id)) != workout.id

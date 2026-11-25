from dataclasses import asdict
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fitness_intelligence.adapters.garmin.mapping import (
    GarminBinding,
    WorkoutResponse,
    map_activity,
    map_day,
)
from fitness_intelligence.analytics.strength import Period
from fitness_intelligence.db.endurance_models import (
    ActivitySplit,
    ActivityStep,
    DailyRecoveryObservation,
    EnduranceActivity,
)
from fitness_intelligence.db.models import (
    ExternalReference,
    SourceAccount,
    User,
    Workout,
    WorkoutExercise,
)
from fitness_intelligence.db.strength_analytics import strength_observations

pytestmark = pytest.mark.postgres


def rejects(db: Session, row: object) -> None:
    with pytest.raises(IntegrityError), db.begin_nested():
        db.add(row)
        db.flush()


def test_activity_identity_and_child_ownership(db: Session) -> None:
    owner, other = User(), User()
    db.add_all([owner, other])
    db.flush()
    workouts, references = [], []
    for profile in (31, 32):
        account = SourceAccount(
            user_id=owner.id, provider="garmin", provider_account_id=str(profile), status="active"
        )
        db.add(account)
        db.flush()
        binding = GarminBinding.from_account(owner_id=owner.id, account=account)
        listing = {
            "activityId": 1,
            "ownerId": profile,
            "activityType": {"typeKey": "running"},
            "startTimeLocal": "2024-11-02 23:01:02",
            "startTimeGMT": "2024-11-03 03:01:02",
            "distance": Decimal("400.123456789"),
            "averageSpeed": 0,
            "splitSummaries": [{"splitType": "RUN_ACTIVE", "noOfSplits": 2}],
        }
        activity = map_activity(
            binding,
            listing,
            workouts=WorkoutResponse(
                binding.source,
                1,
                [
                    {
                        "index": 0,
                        "steps": [
                            {
                                "stepIndex": 0,
                                "intensity": "ACTIVE",
                                "durationType": "TIME",
                                "durationValue": 10,
                                "targetType": "SPEED",
                                "targetValue": 2,
                            }
                        ],
                    }
                ],
            ),
        )
        workout = Workout(user_id=owner.id, title=activity.sport, started_at=activity.started_at)
        db.add(workout)
        db.flush()
        attrs = dict(
            user_id=owner.id,
            source_account_id=account.id,
            provider="garmin",
            entity_type="workout",
            workout_id=workout.id,
            external_id=activity.external_id,
            raw_payload={},
        )
        reference = ExternalReference(**attrs)
        db.add(reference)
        db.flush()
        rejects(db, ExternalReference(**attrs))
        parent = dict(user_id=owner.id, workout_id=workout.id)
        db.add(
            EnduranceActivity(
                **parent,
                reference_id=reference.id,
                sport=activity.sport,
                subtype=activity.subtype,
                local_date=activity.local_date,
                distance_m=activity.distance_m,
                average_speed_mps=activity.average_speed_mps,
            )
        )
        db.flush()
        db.add(ActivitySplit(**parent, position=0, **asdict(activity.splits[0])))
        db.add(ActivityStep(**parent, **asdict(activity.steps[0])))
        db.flush()
        rejects(
            db,
            ActivitySplit(user_id=other.id, workout_id=workout.id, position=1, kind="RUN_ACTIVE"),
        )
        rejects(
            db, ActivityStep(user_id=other.id, workout_id=workout.id, workout_index=0, step_index=1)
        )
        rejects(
            db, ActivitySplit(**parent, position=1, kind="RUN_ACTIVE", duration_s=Decimal("NaN"))
        )
        workouts.append(workout)
        references.append(reference)
    db.commit()
    assert workouts[0].id != workouts[1].id
    first = db.get(EnduranceActivity, workouts[0].id)
    assert first.distance_m == Decimal("400.123456789")
    assert first.average_speed_mps == 0 and first.duration_s is None
    assert first.local_date == date(2024, 11, 2)
    with pytest.raises(IntegrityError), db.begin_nested():
        first.reference_id = references[1].id
        db.flush()
    with pytest.raises(IntegrityError), db.begin_nested():
        first.user_id = other.id
        db.flush()
    period = Period(date(2024, 11, 1), date(2024, 11, 5))
    assert list(strength_observations(db, owner_id=owner.id, period=period)) == []
    db.add(
        WorkoutExercise(
            user_id=owner.id, workout_id=workouts[0].id, position=0, name="Synthetic press"
        )
    )
    db.flush()
    (mixed,) = strength_observations(db, owner_id=owner.id, period=period)
    assert mixed.workout_id == workouts[0].id


def test_daily_identity_and_constraints(db: Session) -> None:
    owner, other = User(), User()
    db.add_all([owner, other])
    db.flush()
    for profile in (31, 32):
        account = SourceAccount(
            user_id=owner.id, provider="garmin", provider_account_id=str(profile), status="active"
        )
        db.add(account)
        db.flush()
        binding = GarminBinding.from_account(owner_id=owner.id, account=account)
        day = date(2024, 3, 10)
        mapped = map_day(
            binding,
            day,
            daily={
                "calendarDate": day.isoformat(),
                "userProfileId": profile,
                "activeKilocalories": Decimal("10.123456789"),
            },
        )
        (observation,) = mapped
        fields = asdict(observation)
        fields.pop("source")
        attrs = dict(user_id=owner.id, provider="garmin", source_account_id=account.id, **fields)
        item = DailyRecoveryObservation(**attrs)
        db.add(item)
        db.flush()
        rejects(db, DailyRecoveryObservation(**attrs))
        rejects(db, DailyRecoveryObservation(**(attrs | {"user_id": other.id})))
        rejects(db, DailyRecoveryObservation(**(attrs | {"provider": "hevy"})))
        # A fresh day ensures these fail on their own constraints, not uniqueness.
        fresh = attrs | {"local_date": day + timedelta(days=1)}
        for changes in (
            {"value": -1},
            {"value": Decimal("NaN")},
            {"unit": "kJ"},
            {"method": "reported"},
            {"metric": "calorie_intake"},
            {
                "window_start": datetime(2024, 3, 11, tzinfo=UTC),
                "window_end": datetime(2024, 3, 10, tzinfo=UTC),
            },
        ):
            rejects(db, DailyRecoveryObservation(**(fresh | changes)))
        db.refresh(item)
        assert item.value == Decimal("10.123456789")
    assert (
        db.scalar(
            select(func.count())
            .select_from(DailyRecoveryObservation)
            .where(DailyRecoveryObservation.user_id == owner.id)
        )
        == 2
    )

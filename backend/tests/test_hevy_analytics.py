from copy import deepcopy
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_hevy_importer import FakeClient, setup
from test_hevy_mapping import snapshot

from fitness_intelligence.adapters.hevy.analytics import HevyHistoryProfile, query_hevy_history
from fitness_intelligence.adapters.hevy.importer import Importer, LocalBinding
from fitness_intelligence.adapters.hevy.schemas import HevyWorkout, UpdatedEvent
from fitness_intelligence.analytics.strength import Period
from fitness_intelligence.db.models import ExternalReference, SourceAccount
from fitness_intelligence.db.strength_analytics import query_strength

pytestmark = pytest.mark.postgres
PERIOD = Period(date(2026, 1, 1), date(2026, 1, 15))


def session_data(day: int, weight: int) -> dict:
    data = snapshot()
    data.update(
        id=f"session-{day}",
        start_time=f"2026-01-{day:02}T10:00:00Z",
        end_time=f"2026-01-{day:02}T11:00:00Z",
        created_at=f"2026-01-{day:02}T11:00:00Z",
        updated_at=f"2026-01-{day:02}T11:01:00Z",
    )
    press = data["exercises"][0]
    press["sets"][0].update(type="normal", weight_kg=weight, reps=6, custom_metric=None)
    assisted = deepcopy(press)
    assisted.update(index=1, exercise_template_id="assistance")
    assisted["sets"][0].update(weight_kg=25)
    bodyweight = deepcopy(assisted)
    bodyweight.update(index=9, exercise_template_id="bodyweight")
    bodyweight["sets"][0].update(weight_kg=None)
    data["exercises"] = [press, bodyweight, assisted]
    return data


def test_imported_history_strict_and_account_scoped_profiles(db: Session) -> None:
    importer, client = setup(db)
    client.data = session_data(1, 50)
    importer.sync()
    later = session_data(8, 55)
    unfinished = session_data(9, 70)
    unfinished["end_time"] = None
    client.feed = [
        UpdatedEvent(type="updated", workout=HevyWorkout.model_validate(w))
        for w in (later, unfinished)
    ]
    importer.sync()
    owner = importer.binding.user_id
    second = SourceAccount(
        user_id=owner, provider="hevy", provider_account_id="second", status="active"
    )
    db.add(second)
    db.commit()
    second_client = FakeClient()
    second_client.data = session_data(1, 90)
    second_client.identity_value = "second"
    Importer(db.bind, LocalBinding(owner, second.id, "second"), second_client).sync()

    strict = query_strength(db, owner_id=owner, period=PERIOD)
    assert strict.weekly_activity["workouts"].sum() == 4
    assert strict.weekly_activity["completed_sets"].sum() == 0
    assert strict.weekly_volume.is_empty() and strict.progression.is_empty()

    profile = HevyHistoryProfile(importer.binding.source_account_id, frozenset({"T1"}))
    report = query_hevy_history(db, owner_id=owner, period=PERIOD, profile=profile)
    assert report.weekly_activity.select("workouts", "completed_sets", "inferred_sets").rows() == [
        (1, 3, 3),
        (2, 3, 3),
        (0, 0, 0),
    ]
    assert report.weekly_volume["inferred_sets"].to_list() == [1] * 6
    assert report.weekly_volume["volume_load_kg"].drop_nulls().to_list() == [300, 330]
    assert report.progression["estimated_1rm_kg"].to_list() == [Decimal(60), Decimal(66)]
    assert report.progression["completion_inferred"].to_list() == [True, True]
    assert report.progression["exercise_key"].n_unique() == 1
    assert report.weekly_volume["exercise_key"].n_unique() == 3

    counts_only = query_hevy_history(
        db, owner_id=owner, period=PERIOD, profile=HevyHistoryProfile(second.id)
    )
    assert (
        counts_only.progression.is_empty()
        and counts_only.weekly_volume["sets_with_load"].sum() == 0
    )
    assert set(counts_only.weekly_volume["exercise_key"]).isdisjoint(
        report.weekly_volume["exercise_key"]
    )
    foreign = query_hevy_history(db, owner_id=uuid4(), period=PERIOD, profile=profile)
    assert foreign.weekly_activity["workouts"].sum() == 0


@pytest.mark.parametrize("damage", ["order", "count", "legacy", "shared", "deleted"])
def test_unsafe_reference_never_supplies_comparison(db: Session, damage: str) -> None:
    importer, client = setup(db)
    client.data = session_data(1, 50)
    importer.sync()
    owner = importer.binding.user_id
    ref = db.scalars(select(ExternalReference).where(ExternalReference.user_id == owner)).one()
    projection = deepcopy(ref.raw_payload)
    if damage == "order":
        projection["exercises"].reverse()
    elif damage == "count":
        projection["exercises"].pop()
    elif damage == "legacy":
        ref.sync_metadata = {}
    elif damage == "shared":
        db.add(
            ExternalReference(
                user_id=owner,
                workout_id=ref.workout_id,
                entity_type="workout",
                provider="hevy",
                source_account_id=ref.source_account_id,
                external_id="ambiguous",
                raw_payload={},
            )
        )
    else:
        ref.source_deleted_at = ref.source_updated_at
    ref.raw_payload = projection
    db.flush()
    profile = HevyHistoryProfile(ref.source_account_id, frozenset({"T1"}))
    report = query_hevy_history(db, owner_id=owner, period=PERIOD, profile=profile)
    assert report.progression.is_empty()
    assert report.weekly_volume["inferred_sets"].sum() == (
        0 if damage in ("shared", "deleted") else 3
    )
    assert all(key.startswith("occurrence:") for key in report.weekly_volume["exercise_key"])


def test_profile_rejects_substring_allowlist() -> None:
    with pytest.raises(ValueError, match="frozenset"):
        HevyHistoryProfile(uuid4(), external_load_templates="T10")

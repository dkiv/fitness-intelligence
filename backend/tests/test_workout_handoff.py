"""G1B local handoff regression tests. All template IDs and prescriptions are synthetic."""

import json
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from fitness_intelligence.db import familiar_snapshot as wire
from fitness_intelligence.db.models import User
from fitness_intelligence.db.plan_commands import PlanCommands
from fitness_intelligence.db.plan_models import (
    AthleteContext,
    PlanDecision,
    PlanRevision,
    SessionOutcome,
    TrainingPlan,
)
from fitness_intelligence.handoff.garmin import garmin_worksheet
from fitness_intelligence.handoff.hevy import (
    HevyManifest,
    PreviewArguments,
    VerifiedTemplate,
    hevy_manifest,
)
from fitness_intelligence.handoff.prescription import (
    PrescriptionExport,
    from_revision,
    prescription_digest,
)
from fitness_intelligence.planning import familiar as f
from fitness_intelligence.planning.familiar_examples import Emphasis, example
from fitness_intelligence.planning.prescriptions import Target, fixed

ZONE = "America/Toronto"
START = datetime(2027, 1, 4, 23, tzinfo=UTC)


def source(p: f.Prescription, start: datetime = START) -> PrescriptionExport:
    local = start.astimezone(ZoneInfo(ZONE))
    return PrescriptionExport(
        cycle=UUID(int=1),
        owner_id=wire.PREVIEW_OWNER,
        revision=UUID(int=2),
        block_revision=UUID(int=3),
        week=1,
        rule=f.RULE,
        approval="unapproved-preview",
        approval_command_id=None,
        zone=ZONE,
        session=f.Session(
            occurrence=UUID(int=4),
            template="fixture",
            day=local.date(),
            start_utc=start,
            prescription=p,
        ),
        local_start=local.isoformat(),
        prescription_sha256=prescription_digest(p),
    )


def mapping(ex: f.Exercise) -> VerifiedTemplate:
    return VerifiedTemplate(
        movement=ex.movement,
        variation=ex.variation,
        equipment=ex.equipment,
        load_convention=ex.load_convention,
        template_id="synthetic-" + ex.movement,
    )


@pytest.fixture
def gym() -> f.Strength:
    p = example("strength")[0].templates[0].prescription
    assert isinstance(p, f.Strength)
    return p


def test_hevy_order_receipt_free_and_serialization(gym: f.Strength) -> None:
    origin = source(gym)
    ids = tuple(map(mapping, gym.exercises))
    result = hevy_manifest(origin, ids)
    assert result.classification == "usable-with-disclosed-limitations"
    args = json.loads(result.canonical_json())["preview_arguments"]
    assert set(args) == {"routine"}
    exercises = args["routine"]["exercises"]
    assert [e["exercise_template_id"] for e in exercises] == ["synthetic-press", "synthetic-squat"]
    for exercise, weights in zip(exercises, [[20, 40, 40, 35], [20, 50, 50, 45]], strict=True):
        assert [s["weight_kg"] for s in exercise["sets"]] == weights
        assert [s["type"] for s in exercise["sets"]] == ["warmup", "normal", "normal", "normal"]
        assert [s["reps"] for s in exercise["sets"]] == [5] * 4
        assert exercise["rest_seconds"] is None
        notes = exercise["notes"]
        assert (
            notes.index("prepare (warmup)")
            < notes.index("primary (working)")
            < notes.index("backoff (working)")
        )
        assert notes.count("rest after 90 s") == 3 and "rest after 0 s" in notes
        assert "set-rpe-0-10 7 (permitted 6–8), cap 8" in notes
    assert result.canonical_json() == hevy_manifest(origin, ids[::-1]).canonical_json()
    assert HevyManifest.model_validate_json(result.canonical_json()) == result
    assert result.digest() == sha256(result.canonical_json().encode()).hexdigest()
    changed = ids[0].model_copy(update={"template_id": "another-id"})
    assert hevy_manifest(origin, (changed, ids[1])).digest() != result.digest()
    assert result.source.publication_authorized is False
    with pytest.raises(ValidationError):
        result.source.approval = "synthetic-approved-fixture"


@pytest.mark.parametrize(
    ("routine_length", "exercise_length"),
    [
        (10_000, 10_000),
        (10_001, 10_000),
        (10_000, 10_001),
        (10_001, 10_001),
    ],
)
def test_generated_hevy_note_limits(
    gym: f.Strength, routine_length: int, exercise_length: int
) -> None:
    mappings = tuple(map(mapping, gym.exercises))
    baseline = hevy_manifest(source(gym), mappings).preview_arguments.routine
    # Both renderers add one newline when a free-text note is present.
    routine_note = "é" * (routine_length - len(baseline.notes) - 1)
    exercise_note = "é" * (exercise_length - len(baseline.exercises[1].notes) - 1)
    press, squat = gym.exercises
    prescription = gym.model_copy(
        update={
            "notes": routine_note,
            "exercises": (press, squat.model_copy(update={"notes": exercise_note})),
        }
    )
    origin = source(prescription)
    result = hevy_manifest(origin, mappings)
    assert result.source == origin
    assert result.source.session.prescription == prescription
    expected = tuple(
        f"{field} exceeds Hevy's 10,000-character limit"
        for field, length in (
            ("routine.notes", routine_length),
            ("routine.exercises.1.notes", exercise_length),
        )
        if length > 10_000
    )
    assert result.blockers == expected
    if expected:
        assert result.classification == "blocked" and result.preview_arguments is None
    else:
        assert result.classification == "usable-with-disclosed-limitations"
        routine = result.preview_arguments.routine
        assert routine.notes == baseline.notes + "\n" + routine_note
        notes = routine.exercises[1].notes
        assert len(notes) == exercise_length and exercise_note in notes
        assert notes.replace(exercise_note + "\n", "", 1) == baseline.exercises[1].notes


def test_hevy_preview_title_limit(gym: f.Strength) -> None:
    # Canonical template keys are bounded to 64 characters. Exercise the provider boundary directly.
    args = hevy_manifest(source(gym), tuple(map(mapping, gym.exercises))).preview_arguments
    raw = args.model_dump()
    raw["routine"]["title"] = "a" * 10_000
    assert PreviewArguments.model_validate(raw).routine.title == raw["routine"]["title"]
    raw["routine"]["title"] += "a"
    with pytest.raises(ValidationError) as exc:
        PreviewArguments.model_validate(raw)
    assert exc.value.errors()[0]["loc"] == ("routine", "title")


def test_missing_ambiguous_and_wrong_convention_block_whole_routine(gym: f.Strength) -> None:
    first, second = map(mapping, gym.exercises)
    for mappings, reason in (
        ((first,), "squat/standing/barbell/total-external-kg: missing"),
        ((first, second, second.model_copy(update={"template_id": "other"})), "ambiguous"),
        ((first, second.model_copy(update={"load_convention": "per-hand-kg"})), "missing"),
        (
            (first, second.model_copy(update={"template_id": first.template_id})),
            "different exercise",
        ),
    ):
        result = hevy_manifest(source(gym), mappings)
        assert result.classification == "blocked" and result.preview_arguments is None
        assert any(reason in message for message in result.blockers)


def test_per_hand_reps_rest_notes_and_load_range(gym: f.Strength) -> None:
    ex = gym.exercises[0]
    group = ex.groups[-1]
    item = group.sets[0].model_copy(update={"reps": Target(4, 5, 7)})
    ex = ex.model_copy(
        update={
            "variation": "seated",
            "equipment": "dumbbell",
            "load_convention": "per-hand-kg",
            "groups": (group.model_copy(update={"sets": (item,)}),),
            "notes": "Pause each rep.",
        }
    )
    gym = gym.model_copy(update={"exercises": (ex,), "notes": "Use the marked bench."})
    result = hevy_manifest(source(gym), (mapping(ex),))
    routine = result.preview_arguments.routine
    row = routine.exercises[0]
    assert row.rest_seconds == 0 and "Pause each rep." in row.notes
    assert "per-hand-kg" in row.notes and "5 (permitted 4–7) reps" in row.notes
    assert row.sets[0].reps is None and row.sets[0].rep_range.model_dump() == {"start": 4, "end": 7}
    assert row.sets[0].weight_kg == 35 and "Use the marked bench." in routine.notes
    varied = item.model_copy(update={"load": Target(Decimal(30), Decimal(35), Decimal(40))})
    ex = ex.model_copy(update={"groups": (group.model_copy(update={"sets": (varied,)}),)})
    result = hevy_manifest(source(gym.model_copy(update={"exercises": (ex,)})), (mapping(ex),))
    assert result.preview_arguments is None and "permitted load range" in result.blockers[0]
    assert result.source.session.prescription.exercises[0].groups[0].sets[0].load == varied.load


@pytest.mark.parametrize("final", [False, True])
def test_expanded_run_and_range(final: bool) -> None:
    run = example("running")[0].templates[-1].prescription
    warm, reps, cool = run.segments
    warm = warm.model_copy(update={"seconds": Target(500, 600, 620)})
    if final:
        reps = reps.model_copy(
            update={"final_recovery": reps.between.model_copy(update={"seconds": fixed(75)})}
        )
    run = run.model_copy(update={"segments": (warm, reps, cool), "notes": "Use the level route."})
    sheet = garmin_worksheet(source(run))
    expected = [warm, reps.work, reps.between, reps.work, reps.between, reps.work]
    if final:
        expected.append(reps.final_recovery)
    expected.append(cool)
    assert sheet.steps == tuple(expected)
    extra = 75 if final else 0
    assert sheet.workout_seconds == Target(1760 + extra, 1860 + extra, 1880 + extra)
    assert sheet.preparation_seconds == 180 and sheet.reservation_seconds == 2060 + extra
    output = sheet.render()
    for cue in (
        "600 (permitted 500–620)",
        "lap-button",
        "cap 7",
        "Use the level route.",
        "2 between-bout recoveries",
        "Add to Calendar",
        "watch calendar",
        "one explicit final recovery" if final else "no final recovery",
    ):
        assert cue in output
    assert "No pace or heart-rate target" in output
    assert sheet.model_validate_json(sheet.canonical_json()) == sheet


@pytest.mark.parametrize(
    "start,expected",
    [
        (datetime(2027, 3, 14, 7, 10, tzinfo=UTC), "2027-03-14T03:10:00-04:00"),
        (datetime(2027, 11, 7, 5, 30, tzinfo=UTC), "2027-11-07T01:30:00-04:00"),
        (datetime(2027, 11, 7, 6, 30, tzinfo=UTC), "2027-11-07T01:30:00-05:00"),
        (datetime(2027, 1, 5, 2, tzinfo=UTC), "2027-01-04T21:00:00-05:00"),
    ],
)
def test_local_offset_and_date(start: datetime, expected: str) -> None:
    run = example("running")[0].templates[1].prescription
    assert expected in garmin_worksheet(source(run, start)).render()


@pytest.mark.parametrize("emphasis", ["strength", "running", "balanced"])
def test_sealed_week_export_is_read_only_and_historical(
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    emphasis: Emphasis,
) -> None:
    db.add(User(id=wire.PREVIEW_OWNER))
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(wire.PREVIEW_OWNER))
    monkeypatch.setattr(PlanCommands, "_now", lambda self: datetime(2027, 1, 2, tzinfo=UTC))
    block, ctx = example(emphasis)
    cmd = PlanCommands(db)
    context = cmd.capture_context(ctx, expected_context=None)
    cycle = cmd.create_cycle(block)

    def approve(rev: UUID, head: UUID | None) -> None:
        cmd.decide(cycle, rev, expected_head=head, choice="approve", command_id=uuid4())

    opening = cmd.submit(cycle, None, f.ProposeBlock())
    approve(opening, None)
    declined = cmd.submit(cycle, opening, f.FamiliarWeek(number=1))
    cmd.decide(cycle, declined, expected_head=opening, choice="decline", command_id=uuid4())
    with pytest.raises(ValueError, match="approving decision"):
        from_revision(cmd, cycle, declined, uuid4())
    week = cmd.submit(cycle, opening, f.FamiliarWeek(number=1))
    sessions = [s for d in cmd.preview(cycle, week).candidate.days for s in d.sessions]
    first = sessions[0].occurrence
    with pytest.raises(ValueError, match="dated"):
        from_revision(cmd, cycle, opening, first)
    with pytest.raises(ValueError, match="matching occurrence"):
        from_revision(cmd, cycle, week, uuid4())
    draft = from_revision(cmd, cycle, week, first)
    assert draft.approval == "unapproved-preview" and draft.approval_command_id is None
    approve(week, opening)
    next_week = cmd.submit(cycle, week, f.FamiliarWeek(number=2))
    approve(next_week, week)
    cmd.capture_context(ctx.model_copy(update={"zone": "UTC"}), expected_context=context)
    db.commit()

    def rows() -> list:
        return [
            db.execute(select(table.__table__).order_by(table.id)).all()
            for table in (TrainingPlan, PlanRevision, PlanDecision, AthleteContext, SessionOutcome)
        ]

    before = rows()

    def forbid_replay(*args: object, **kwargs: object) -> None:
        pytest.fail("export regenerated the prescription")

    monkeypatch.setattr(wire, "generate_for_rule", forbid_replay)
    for session in sessions:
        saved = from_revision(cmd, cycle, week, session.occurrence)
        assert saved.approval == "synthetic-approved-fixture" and saved.approval_command_id
        assert saved.revision == week and saved.zone == ZONE and not saved.publication_authorized
        assert saved.session == session and saved.prescription_sha256 == prescription_digest(
            session.prescription
        )
        if isinstance(session.prescription, f.Strength):
            m = hevy_manifest(saved, tuple(map(mapping, session.prescription.exercises)))
            assert m.preview_arguments.routine.exercises
        else:
            w = garmin_worksheet(saved)
            if session.prescription.role in ("easy", "long"):
                seconds = 1200 if session.prescription.role == "easy" else 1800
                assert len(w.steps) == 1 and w.workout_seconds == fixed(seconds)
                assert w.reservation_seconds == seconds + 180
    assert from_revision(cmd, cycle, week, first).prescription_sha256 == draft.prescription_sha256
    assert before == rows() and not db.new and not db.dirty and not db.deleted
    foreign = User()
    db.add(foreign)
    db.flush()
    monkeypatch.setenv("FITNESS_PLANNING_OWNER_ID", str(foreign.id))
    with pytest.raises(NoResultFound):
        from_revision(PlanCommands(db), cycle, week, first)


def test_export_rejects_operational_labels_and_tampering(gym: f.Strength) -> None:
    raw = source(gym).model_dump(mode="json")
    for field, value in (
        ("approval", "operationally-approved"),
        ("approval", "synthetic-approved-fixture"),
        ("publication_authorized", True),
        ("prescription_sha256", "unrelated"),
        ("local_start", "2027-01-04T18:00:00-04:00"),
    ):
        with pytest.raises(ValidationError):
            PrescriptionExport.model_validate_json(json.dumps(raw | {field: value}))


def test_historical_effort_and_bodyweight(gym: f.Strength) -> None:
    exercise = gym.exercises[0]
    group = exercise.groups[1]
    sets = tuple(s.model_copy(update={"load": fixed(Decimal(0))}) for s in group.sets)
    exercise = exercise.model_copy(
        update={
            "movement": "pullup",
            "variation": "strict",
            "equipment": "bar",
            "load_convention": "bodyweight",
            "groups": (group.model_copy(update={"sets": sets}),),
            "load_step_kg": None,
        }
    )
    original = source(gym.model_copy(update={"exercises": (exercise,)}))
    historical = original.model_copy(update={"rule": "synthetic.familiar.hold.v1"})
    manifest = hevy_manifest(historical, (mapping(exercise),))
    assert manifest.source.session == original.session
    assert any("predates scoped effort" in msg for msg in manifest.limitations)
    assert all(
        row.weight_kg is None for row in manifest.preview_arguments.routine.exercises[0].sets
    )

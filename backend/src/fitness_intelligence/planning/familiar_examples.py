"""Three invented E4.1 histories. Run as a module for a database-free manual preview."""

import argparse
from datetime import date, timedelta
from decimal import Decimal
from itertools import combinations
from typing import Literal
from uuid import UUID

from . import familiar as f
from .familiar_calendar import generate
from .prescriptions import Target, fixed

type Emphasis = Literal["strength", "running", "balanced"]


def _effort(strength: bool, nominal: int) -> f.Effort:
    return f.Effort(
        scale="set-rpe-0-10" if strength else "run-step-rpe-0-10",
        target=Target(Decimal(nominal - 1), Decimal(nominal), Decimal(nominal + 1)),
        cap=Decimal(nominal + 1),
    )


def _exercise(movement: str, working_kg: int) -> f.Exercise:
    def group(key: str, warm: bool, kg: int, count: int) -> f.Group:
        return f.Group(
            key=key,
            kind="warmup" if warm else "working",
            effort=_effort(True, 5 if warm else 7),
            sets=tuple(
                f.SetTarget(
                    ordinal=i + 1,
                    reps=fixed(5),
                    load=fixed(Decimal(kg)),
                    execution_seconds=60,
                    rest_after_seconds=90 if key != "backoff" or i + 1 < count else 0,
                )
                for i in range(count)
            ),
        )

    return f.Exercise(
        movement=movement,
        variation="standing",
        equipment="barbell",
        load_convention="total-external-kg",
        load_step_kg=Decimal("2.5"),
        transition_seconds=120,
        groups=(
            group("prepare", True, 20, 1),
            group("primary", False, working_kg, 2),
            group("backoff", False, working_kg - 5, 1),
        ),
    )


def _step(purpose: str, seconds: int, effort: int) -> f.Step:
    return f.Step(purpose=purpose, seconds=fixed(seconds), effort=_effort(False, effort))


def example(emphasis: Emphasis, start: date = date(2027, 1, 4)) -> tuple[f.Block, f.Context]:
    if emphasis not in {"strength", "running", "balanced"}:
        raise ValueError("unknown emphasis")
    gym = f.Strength(
        role="gym",
        preparation_seconds=300,
        exercises=(_exercise("press", 40), _exercise("squat", 50)),
    )
    easy = f.Running(role="easy", preparation_seconds=180, segments=(_step("work", 1200, 3),))
    long = f.Running(role="long", preparation_seconds=180, segments=(_step("work", 1800, 3),))
    repeats = f.Repeat(count=3, work=_step("work", 240, 6), between=_step("recovery", 120, 2))
    controlled = f.Running(
        role="controlled",
        preparation_seconds=180,
        segments=(_step("warmup", 600, 3), repeats, _step("cooldown", 300, 3)),
    )
    templates = [
        f.Template(key="gym-a", prescription=gym),
        f.Template(key="easy", prescription=easy),
        f.Template(key="long", prescription=long),
    ]
    if emphasis != "running":
        templates.append(f.Template(key="gym-b", prescription=gym))
    if emphasis != "strength":
        templates.append(f.Template(key="cruise", prescription=controlled))
    protects = []
    if emphasis != "strength":
        protects.append(
            f.Protection(
                sport="strength",
                task="squat",
                protocol="same load and depth",
                desired_direction="maintain",
            )
        )
    if emphasis != "running":
        protects.append(
            f.Protection(
                sport="running",
                task="long",
                protocol="same course and effort",
                desired_direction="maintain",
            )
        )
    block = f.Block(
        key="familiar-block",
        start=start,
        phases=("establish", "repeat", "review", "repeat", "consolidate", "review"),
        templates=tuple(templates),
        protections=tuple(protects),
        commitments=(
            f.Commitment(sport="running", role="long", sessions=1, minimum_per_session=1800),
            f.Commitment(sport="strength", role="gym", sessions=1, minimum_per_session=6),
        ),
        spacing=tuple(
            f.Spacing(first=a.key, second=b.key, elapsed_seconds=20 * 3600)
            for a, b in combinations(templates, 2)
        ),
    )
    history = start - timedelta(days=14)
    observations = []

    # Invented actual work, specified independently of the prescription objects.
    # The athlete confirms the familiar instructions, including the stated stop caps.
    # No achieved set or step RPE was recorded in these histories.
    def reported_effort(low: int, nominal: int, high: int, cap: int) -> f.EffortEvidence:
        return f.EffortEvidence(
            confirmed_target=Target(Decimal(low), Decimal(nominal), Decimal(high)),
            confirmed_cap=Decimal(cap),
        )

    group_cues = {
        "prepare": reported_effort(4, 5, 6, 6),
        "primary": reported_effort(6, 7, 8, 8),
        "backoff": reported_effort(6, 7, 8, 8),
    }
    easy_cue = reported_effort(2, 3, 4, 4)
    cruise_cue = reported_effort(5, 6, 7, 7)
    recovery_cue = reported_effort(1, 2, 3, 3)
    reported_sets = tuple(
        f.ActualSet(
            movement=movement,
            variation="standing",
            equipment="barbell",
            convention="total-external-kg",
            group=group,
            kind="warmup" if group == "prepare" else "working",
            ordinal=ordinal,
            reps=5,
            kg=Decimal(kg),
            effort=group_cues[group],
        )
        for movement, work in (("press", 40), ("squat", 50))
        for group, ordinal, kg in (
            ("prepare", 1, 20),
            ("primary", 1, work),
            ("primary", 2, work),
            ("backoff", 1, work - 5),
        )
    )
    runs = {
        "easy": (("work", 1200, easy_cue),),
        "long": (("work", 1800, easy_cue),),
        "cruise": (
            ("warmup", 600, easy_cue),
            ("work", 240, cruise_cue),
            ("recovery", 120, recovery_cue),
            ("work", 240, cruise_cue),
            ("recovery", 120, recovery_cue),
            ("work", 240, cruise_cue),
            ("cooldown", 300, easy_cue),
        ),
    }
    usual_days = {
        "gym-a": 0,
        "gym-b": 3,
        "easy": 1,
        "cruise": 4 if emphasis == "running" else 2,
        "long": 6,
    }
    for t in templates:
        observations.append(
            f.Observation(
                support="report-" + t.key,
                provenance="synthetic-athlete-report",
                template=t.key,
                role=t.prescription.role,
                day=history + timedelta(days=usual_days[t.key]),
                confirmed=True,
                manageable=True,
                sets=reported_sets if t.key.startswith("gym") else (),
                steps=tuple(
                    f.ActualStep(purpose=purpose, elapsed_seconds=seconds, effort=cue)
                    for purpose, seconds, cue in runs.get(t.key, ())
                ),
            )
        )
    ctx = f.Context(
        zone="America/Toronto",
        objectives=(
            f.Objective(
                sport="strength", rank=2 if emphasis == "running" else 1, outcome="repeatable squat"
            ),
            f.Objective(
                sport="running",
                rank=2 if emphasis == "strength" else 1,
                outcome="course performance",
            ),
        ),
        history_start=history,
        observations=tuple(observations),
        windows=tuple(
            f.Window(
                weekday=i,
                start_minute=18 * 60,
                end_minute=18 * 60 + 40,
                equipment=("barbell",) if i in (0, 3) else (),
            )
            for i in range(7)
        ),
    )
    return block, ctx


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("emphasis", choices=("strength", "running", "balanced"))
    args = parser.parse_args()
    block, ctx = example(args.emphasis)
    for day in generate(UUID(int=1), block, ctx, 1):
        print(day.model_dump_json(indent=2))

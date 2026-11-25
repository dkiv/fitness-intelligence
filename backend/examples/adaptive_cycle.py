"""Run the January 2027 fixture in a migrated disposable E3 database."""

import argparse
import os
from datetime import UTC, datetime
from typing import Literal
from unittest.mock import patch
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from fitness_intelligence.db.models import User
from fitness_intelligence.db.plan_commands import PlanCommands
from fitness_intelligence.db.plan_snapshot import Generate, PlanningContext
from fitness_intelligence.db.review import render_review
from fitness_intelligence.planning.outcomes import Actual, WorkingSet
from fitness_intelligence.planning.planner import Slot
from fitness_intelligence.planning.press_block import Availability, PressBlock


class FixtureCommands(PlanCommands):
    instant = datetime(2027, 1, 2, 15, tzinfo=UTC)

    def _now(self) -> datetime:
        return self.instant


def demonstrate(choice: Literal["approve", "decline"], hold: bool) -> None:
    url = make_url(os.environ["TEST_DATABASE_URL"])
    if url.get_backend_name() != "postgresql" or url.database != "fi_e3_disposable":
        raise ValueError("the demonstration requires the fi_e3_disposable PostgreSQL database")
    engine = create_engine(url)
    owner_id = uuid4()
    with Session(engine) as db, patch.dict(os.environ, FITNESS_PLANNING_OWNER_ID=str(owner_id)):
        cmd = FixtureCommands(db)
        with db.begin():
            db.add(User(id=owner_id))
            db.flush()
            cmd.capture_context(PlanningContext(Availability()), expected_context=None)
            plan = cmd.create_cycle(PressBlock())
            first = cmd.submit(plan, None, Generate(1))
            print(render_review(cmd.preview(plan, first)))
            cmd.decide(plan, first, expected_head=None, choice="approve", command_id=uuid4())
        cmd.instant = datetime(2027, 1, 10, 17, tzinfo=UTC)
        with db.begin():
            for day, slot, size, reps in (
                (4, Slot.FIRST_PRESS, 3, 5),
                (7, Slot.SECOND_PRESS, 2, 6),
            ):
                actual = Actual(
                    status="completed",
                    confirmed_barbell_press=True,
                    working_sets=tuple(
                        WorkingSet(ordinal=i + 1, rpe=7, external_kg=30, reps=reps)
                        for i in range(size)
                    ),
                    manageable=None if hold and day == 7 else True,
                )
                cmd.record_outcome(
                    plan,
                    first,
                    1,
                    slot,
                    actual,
                    occurred_at=datetime(2027, 1, day, 14, tzinfo=UTC),
                    command_id=uuid4(),
                )
            cmd.record_outcome(
                plan,
                first,
                1,
                Slot.SHORT_RUN,
                Actual(
                    status="partial",
                    run_seconds=900,
                    run_rpe=3,
                    feedback="Stopped early for a scheduling conflict.",
                ),
                occurred_at=datetime(2027, 1, 5, 14, tzinfo=UTC),
                command_id=uuid4(),
            )
            second = cmd.submit(plan, first, Generate(2))
        with db.begin():
            print(render_review(cmd.preview(plan, second)))
            receipt = cmd.decide(
                plan, second, expected_head=first, choice=choice, command_id=uuid4()
            )
        with db.begin():
            head = cmd.current(plan)
            assert head and head.revision_id == (second if choice == "approve" else first)
            print(f"Decision {receipt.choice} · approved week {head.candidate.week.inputs.number}")
    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", choices=("approve", "decline"), required=True)
    parser.add_argument("--hold", action="store_true", help="omit second press feedback")
    args = parser.parse_args()
    demonstrate(args.decision, args.hold)

"""Trusted macOS operator entry point for one bounded Garmin operation."""

import argparse
import json
import logging
import os
import sys
from contextlib import ExitStack
from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import create_engine

from fitness_intelligence.adapters.local_account import LocalAccountError

from .binding import Evidence
from .client import GarminClient, GarminError
from .history import synchronize
from .history_state import Category, Scope, WeightSegment
from .importer import Importer, Mode
from .mapping import MappingError
from .nutrition import WeightUnit
from .verify import keychain_key


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", required=True, type=Path)
    commands = parser.add_subparsers(dest="mode", required=True)
    for mode in Mode:
        command = commands.add_parser(mode.value)
        if mode.takes_day:
            command.add_argument("--day", required=True, type=date.fromisoformat)
        if mode == Mode.WEIGHT:
            command.add_argument(
                "--weight-unit",
                required=True,
                type=WeightUnit,
                choices=list(WeightUnit),
                help="Source unit checked against the displayed weigh-in",
            )
        if mode == Mode.ACTIVITIES:
            command.add_argument("--steps", action="store_true")
    historical = ("backfill", "incremental", "repair")
    for name in historical:
        command = commands.add_parser(name)
        command.add_argument("--start", required=True, type=date.fromisoformat)
        command.add_argument("--end", required=True, type=date.fromisoformat)
        command.add_argument(
            "--categories", nargs="+", required=True, type=Category, choices=list(Category)
        )
        command.add_argument("--request-limit", type=int, default=40)
        command.add_argument("--pass-id", type=UUID, help="Reuse to resume an interrupted refresh")
        command.add_argument("--weight-segment", type=Path)
        if name == "incremental":
            command.add_argument("--overlap", type=int, default=7)
    args = parser.parse_args()
    previous = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        if os.environ.get("SSLKEYLOGFILE"):
            raise GarminError("TLS key logging enabled")
        with ExitStack() as stack:
            evidence = Evidence.load(args.binding)
            engine = create_engine(os.environ["DATABASE_URL"], echo=False, hide_parameters=True)
            stack.callback(engine.dispose)
            if args.mode in historical:
                weight = (
                    WeightSegment.load(args.weight_segment, evidence.source)
                    if args.weight_segment
                    else None
                )
                pass_id = args.pass_id or (UUID(int=0) if args.mode == "backfill" else uuid4())
                scope = Scope(
                    args.mode,
                    args.start,
                    args.end,
                    tuple(args.categories),
                    pass_id,
                    getattr(args, "overlap", 7),
                    weight,
                )
                scope.validate()
                client = GarminClient(keychain_key(), request_limit=args.request_limit)
                stack.callback(client.close)
                counts = synchronize(engine, evidence, client, scope)
            else:
                client = GarminClient(keychain_key())
                stack.callback(client.close)
                counts = Importer(engine, evidence, client).run(
                    Mode(args.mode),
                    day=getattr(args, "day", None),
                    steps=getattr(args, "steps", False),
                    weight_unit=getattr(args, "weight_unit", None),
                )
    except (GarminError, MappingError, LocalAccountError) as exc:
        # These adapter errors carry fixed categories or comparison labels only.
        print(str(exc), file=sys.stderr)
        return 1
    except Exception:
        print(
            "Garmin operation failed. Check local binding evidence, access and provider response.",
            file=sys.stderr,
        )
        return 1
    finally:
        logging.disable(previous)
    print(json.dumps(counts, sort_keys=True))
    return 1 if counts.get("stopped") else 0


if __name__ == "__main__":
    raise SystemExit(main())

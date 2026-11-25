"""Trusted macOS operator entry point for one bounded Garmin operation."""

import argparse
import json
import logging
import os
import sys
from contextlib import ExitStack
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine

from fitness_intelligence.adapters.local_account import LocalAccountError

from .binding import Evidence
from .client import GarminClient, GarminError
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

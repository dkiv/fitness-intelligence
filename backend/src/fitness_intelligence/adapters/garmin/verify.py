"""Local operator entry point. Read a single named Keychain item into memory."""

import argparse
import json
import logging
import subprocess
from datetime import date, timedelta

from .client import GarminClient, GarminError
from .probe import Probe


def keychain_key() -> str:
    try:
        proc = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-s",
                "fitness-intelligence.garmin",
                "-a",
                "personal",
                "-w",
            ],
            capture_output=True,
            timeout=30,
            check=True,
        )
        return proc.stdout.decode("ascii").rstrip("\r\n")
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise GarminError("keychain_unavailable") from None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check two local-calendar Garmin samples")
    yesterday = date.today() - timedelta(days=1)
    parser.add_argument("--recent", type=date.fromisoformat, default=yesterday)
    parser.add_argument("--older", type=date.fromisoformat, default=None)
    args = parser.parse_args()
    if args.recent < date.min + timedelta(days=372) or args.recent > date.today():
        parser.error("recent date must allow a past sample and must be no later than today")
    older = args.older or args.recent - timedelta(days=365)
    if older < date.min + timedelta(days=6) or older > args.recent - timedelta(days=7):
        parser.error("choose non-overlapping weeks at least seven days apart")
    # The HTTP libraries can log URLs (including dates/IDs) when a parent enables debug logging.
    previous_logging_level = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        client = GarminClient(keychain_key())
        try:
            report = Probe(client).run(args.recent, older)
        finally:
            client.close()
    except GarminError as exc:
        report = {"status": "partial", "stopped": str(exc)}
    finally:
        logging.disable(previous_logging_level)
    print(json.dumps(report, sort_keys=True, indent=2))
    return int(report["status"] != "complete")


if __name__ == "__main__":
    raise SystemExit(main())

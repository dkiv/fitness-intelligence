"""Private OS-operator entry point; no server route or credential persistence."""

import argparse
import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fitness_intelligence.adapters.local_account import LocalAccountError, private_config

from .client import HevyClient, HevyError
from .importer import Importer, LocalBinding, check_active_binding


def load_binding(path: Path) -> LocalBinding:
    try:
        data = private_config(path)
    except LocalAccountError as exc:
        raise HevyError(str(exc)) from None
    return LocalBinding(
        UUID(data["user_id"]), UUID(data["source_account_id"]), data["provider_account_id"]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Private local Hevy synchronization")
    parser.add_argument("--binding", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--reconcile", action="store_true")
    mode.add_argument("--verify-only", action="store_true", help="check identity and one sample")
    args = parser.parse_args()
    client = None
    engine = None
    try:
        binding = load_binding(args.binding)
        if args.verify_only and os.environ.get("SSLKEYLOGFILE"):
            raise HevyError("TLS key logging enabled")
        client = HevyClient(os.environ["HEVY_API_KEY"])
        engine = create_engine(os.environ["DATABASE_URL"], echo=False, hide_parameters=True)
        if args.verify_only:
            with Session(engine) as session:
                check_active_binding(session, binding)
            sampled = client.verify_sample(binding.provider_account_id)
            print(
                "Identity matched. Workout schema and mapping passed."
                if sampled
                else "Identity matched. Page schema passed. No workout available to validate."
            )
            return
        Importer(engine, binding, client).sync(reconcile=args.reconcile)
    except Exception:
        # No traceback, SQL parameters, provider bodies or credential-bearing exceptions.
        if args.verify_only:
            parser.exit(1, "Hevy verification failed. Check binding, credentials and contract.\n")
        parser.exit(
            1,
            "Hevy synchronization failed; inspect checkpoint before retrying. Check local binding, "
            "credentials, provider availability and unresolved source conflicts.\n",
        )
    finally:
        if client is not None:
            client.close()
        if engine is not None:
            engine.dispose()
    print("Hevy synchronization completed.")


if __name__ == "__main__":
    main()

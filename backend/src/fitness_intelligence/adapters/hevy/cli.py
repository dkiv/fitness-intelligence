"""Private OS-operator entry point; no server route or credential persistence."""

import argparse
import json
import os
import stat
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine

from .client import HevyClient, HevyError
from .importer import Importer, LocalBinding


def load_binding(path: Path) -> LocalBinding:
    # Open without following symlinks, then check the opened file to avoid TOCTOU races.
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor) as stream:
        info = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_size > 4096
        ):
            raise HevyError("binding must be an operator-owned mode 0600 regular file")
        data = json.load(stream)
    return LocalBinding(
        UUID(data["user_id"]), UUID(data["source_account_id"]), data["provider_account_id"]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Private local Hevy synchronization")
    parser.add_argument("--binding", required=True, type=Path)
    parser.add_argument("--reconcile", action="store_true")
    args = parser.parse_args()
    client = None
    engine = None
    try:
        binding = load_binding(args.binding)
        client = HevyClient(os.environ["HEVY_API_KEY"])
        engine = create_engine(os.environ["DATABASE_URL"], echo=False, hide_parameters=True)
        Importer(engine, binding, client).sync(reconcile=args.reconcile)
    except Exception:
        # No traceback, SQL parameters, provider bodies or credential-bearing exceptions.
        parser.exit(
            1,
            "Hevy synchronization failed; checkpoint not advanced. Check local binding, "
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

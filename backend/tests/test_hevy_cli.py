import json
import os
from pathlib import Path
from uuid import uuid4

import pytest

from fitness_intelligence.adapters.hevy.cli import load_binding
from fitness_intelligence.adapters.hevy.client import HevyError


def test_private_binding_and_permissions(tmp_path: Path) -> None:
    path = tmp_path / "binding.json"
    user, account = uuid4(), uuid4()
    path.write_text(
        json.dumps(
            dict(user_id=str(user), source_account_id=str(account), provider_account_id="synthetic")
        )
    )
    path.chmod(0o600)
    assert load_binding(path).user_id == user
    path.chmod(0o644)
    with pytest.raises(HevyError):
        load_binding(path)
    path.chmod(0o600)
    link = tmp_path / "link"
    link.symlink_to(path)
    with pytest.raises(OSError):
        load_binding(link)


def test_wrong_os_owner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "binding.json"
    path.write_text("{}")
    path.chmod(0o600)
    owner = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: owner + 1)
    with pytest.raises(HevyError):
        load_binding(path)

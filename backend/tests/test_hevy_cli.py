import json
import os
import sys
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_hevy_mapping import snapshot

from fitness_intelligence.adapters.hevy import cli
from fitness_intelligence.adapters.hevy.cli import load_binding
from fitness_intelligence.adapters.hevy.client import HevyClient, HevyError
from fitness_intelligence.db.models import (
    AccountSyncState,
    ExternalReference,
    SourceAccount,
    User,
    Workout,
    WorkoutTombstone,
)


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


@pytest.mark.postgres
@pytest.mark.parametrize("scenario", ["valid", "wrong owner", "invalid sample", "TLS key logging"])
def test_verify_only(
    db: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    scenario: str,
) -> None:
    user = User()
    db.add(user)
    db.flush()
    account = SourceAccount(
        user_id=user.id, provider="hevy", provider_account_id="private-id", status="active"
    )
    db.add(account)
    db.commit()
    binding = tmp_path / "binding.json"
    binding.write_text(
        json.dumps(
            dict(
                user_id=str(uuid4() if scenario == "wrong owner" else user.id),
                source_account_id=str(account.id),
                provider_account_id="private-id",
            )
        )
    )
    binding.chmod(0o600)
    monkeypatch.setattr(sys, "argv", ["cli", "--binding", str(binding), "--verify-only"])
    monkeypatch.setenv("HEVY_API_KEY", "private-key")
    monkeypatch.delenv("SSLKEYLOGFILE", raising=False)
    if scenario == "TLS key logging":
        monkeypatch.setenv("SSLKEYLOGFILE", str(tmp_path / "keys"))
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path == "/v1/user/info":
            return httpx.Response(200, json={"data": {"id": "private-id"}})
        item = {"title": "private-title"} if scenario == "invalid sample" else snapshot()
        return httpx.Response(200, json=dict(page=1, page_count=1, workouts=[item]))

    monkeypatch.setattr(
        cli, "HevyClient", lambda key: HevyClient(key, transport=httpx.MockTransport(handler))
    )
    if scenario == "valid":
        cli.main()
    else:
        with pytest.raises(SystemExit) as failure:
            cli.main()
        assert failure.value.code == 1
    output = capsys.readouterr()
    assert bool(calls) == (scenario in {"valid", "invalid sample"})
    for sensitive in ("private-id", "private-key", "private-title", snapshot()["title"]):
        assert sensitive not in output.out + output.err + caplog.text
    for table in (Workout, ExternalReference, AccountSyncState, WorkoutTombstone):
        assert db.scalars(select(table)).first() is None

from __future__ import annotations

import json
from click.testing import CliRunner
from pydantic import BaseModel

from chi_sdk import chi_command, build_cli, emit_progress


class _SnapOut(BaseModel):
    ok: bool


@chi_command(
    name="snap-progress", output_model=_SnapOut, description="Snapshot progress stream"
)
def _snap_progress() -> _SnapOut:
    emit_progress(message="tick", percent=1, stage="start", command="snap-progress")
    emit_progress(message="tock", percent=50, stage="mid", command="snap-progress")
    return _SnapOut(ok=True)


def _norm(line: str) -> dict:
    d = json.loads(line)
    d.pop("request_id", None)
    d.pop("ts", None)
    return d


def test_progress_snapshot():
    cli = build_cli("snap-prog-app")
    r = CliRunner()
    res = r.invoke(cli, ["--json", "snap-progress"])  # NDJSON
    assert res.exit_code == 0, res.output
    lines = [ln for ln in res.output.splitlines() if ln.strip()]
    assert len(lines) == 3

    env1 = _norm(lines[0])
    env2 = _norm(lines[1])
    env3 = _norm(lines[2])

    assert env1 == {
        "version": "1.0",
        "ok": True,
        "type": "progress",
        "command": "snap-progress",
        "data": {"message": "tick", "percent": 1.0, "stage": "start"},
        "meta": {},
    }
    assert env2 == {
        "version": "1.0",
        "ok": True,
        "type": "progress",
        "command": "snap-progress",
        "data": {"message": "tock", "percent": 50.0, "stage": "mid"},
        "meta": {},
    }
    assert env3 == {
        "version": "1.0",
        "ok": True,
        "type": "result",
        "command": "snap-progress",
        "data": {"ok": True},
        "meta": {},
    }

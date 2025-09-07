from __future__ import annotations

import json
from click.testing import CliRunner
from pydantic import BaseModel

from chi_sdk import chi_command, build_cli


class _In(BaseModel):
    name: str


class _Out(BaseModel):
    greeting: str


@chi_command(
    name="snap-hello", input_model=_In, output_model=_Out, description="Snapshot test"
)
def _snap_hello(inp: _In) -> _Out:
    return _Out(greeting=f"Hello, {inp.name}!")


def normalize_envelope(s: str) -> dict:
    env = json.loads(s)
    # Drop volatile fields
    env.pop("request_id", None)
    env.pop("ts", None)
    return env


def test_schema_snapshot_stability():
    cli = build_cli("snapshot-app")
    r = CliRunner()
    res = r.invoke(cli, ["--json", "schema"])  # envelope
    assert res.exit_code == 0, res.output
    env = normalize_envelope(res.output)
    # Expected snapshot (stable structure for pydantic v2 schemas)
    # Snapshot only the snap-hello command schema to avoid global registry noise
    cmds = env["data"]["commands"]
    snap = next(c for c in cmds if c["name"] == "snap-hello")
    expected_cmd = {
        "name": "snap-hello",
        "description": "Snapshot test",
        "input_schema": {
            "title": "_In",
            "type": "object",
            "properties": {"name": {"title": "Name", "type": "string"}},
            "required": ["name"],
        },
        "output_schema": {
            "title": "_Out",
            "type": "object",
            "properties": {"greeting": {"title": "Greeting", "type": "string"}},
            "required": ["greeting"],
        },
    }
    assert snap == expected_cmd

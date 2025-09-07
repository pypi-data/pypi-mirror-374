from __future__ import annotations

import json

from click.testing import CliRunner
from pydantic import BaseModel, Field

from chi_sdk import chi_command, build_cli, emit_progress


class THelloIn(BaseModel):
    name: str = Field(..., description="Name")
    shout: bool = Field(False, description="Uppercase")


class THelloOut(BaseModel):
    greeting: str


class TProgressOut(BaseModel):
    ok: bool


@chi_command(
    name="t-hello",
    input_model=THelloIn,
    output_model=THelloOut,
    description="Test hello",
)
def t_hello(inp: THelloIn) -> THelloOut:
    text = f"Hello, {inp.name}!"
    if inp.shout:
        text = text.upper()
    return THelloOut(greeting=text)


@chi_command(
    name="t-progress", output_model=TProgressOut, description="Test progress stream"
)
def t_progress() -> TProgressOut:
    emit_progress(message="Step 1", percent=10, stage="start", command="t-progress")
    return TProgressOut(ok=True)


def test_schema_and_envelopes_roundtrip():
    cli = build_cli("test-app")
    r = CliRunner()

    # Schema should include both test commands
    res = r.invoke(cli, ["--json", "schema"])  # force JSON envelope
    assert res.exit_code == 0, res.output
    env = json.loads(res.output)
    assert env["ok"] is True
    cmds = {c["name"] for c in env["data"]["commands"]}
    assert {"t-hello", "t-progress"}.issubset(cmds)

    # t-hello should emit JSON envelope with data.greeting
    res2 = r.invoke(cli, ["--json", "t-hello", "--name", "Ada"])
    assert res2.exit_code == 0, res2.output
    env2 = json.loads(res2.output)
    assert env2["ok"] is True
    assert env2["data"]["greeting"] == "Hello, Ada!"

    # t-progress should emit a progress event followed by a result envelope
    res3 = r.invoke(cli, ["--json", "t-progress"])
    assert res3.exit_code == 0, res3.output
    lines = [ln for ln in res3.output.splitlines() if ln.strip()]
    assert len(lines) >= 2
    first = json.loads(lines[0])
    last = json.loads(lines[-1])
    assert first["type"] == "progress"
    assert last["type"] == "result"
    assert last["ok"] is True

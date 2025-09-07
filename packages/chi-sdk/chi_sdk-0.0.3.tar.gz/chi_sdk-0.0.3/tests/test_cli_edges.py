from typing import List

from pydantic import BaseModel
from click.testing import CliRunner

from chi_sdk import chi_command, build_cli


class _ArrIn(BaseModel):
    numbers: List[int]


class _ArrOut(BaseModel):
    total: int


@chi_command(
    name="t-array", input_model=_ArrIn, output_model=_ArrOut, description="Sum integers"
)
def _t_array(inp: _ArrIn) -> _ArrOut:
    return _ArrOut(total=sum(inp.numbers))


cli = build_cli("test-app")


def test_schema_includes_array_integer_items():
    r = CliRunner()
    res = r.invoke(cli, ["--json", "schema"])
    assert res.exit_code == 0
    env = res.output
    import json

    doc = json.loads(env)
    cmds = {c["name"]: c for c in doc["data"]["commands"]}
    arr = cmds["t-array"]
    props = arr["input_schema"]["properties"]
    assert props["numbers"]["type"] == "array"
    assert props["numbers"]["items"]["type"] == "integer"


def test_invalid_array_item_emits_click_error():
    r = CliRunner()
    # Click option type is INT, pass a non-int to trigger error
    res = r.invoke(cli, ["--json", "t-array", "--numbers", "x"])  # one invalid value
    assert res.exit_code != 0
    # Click handles option parsing before callback; expect default click error text
    assert "Invalid value for '--numbers'" in res.output

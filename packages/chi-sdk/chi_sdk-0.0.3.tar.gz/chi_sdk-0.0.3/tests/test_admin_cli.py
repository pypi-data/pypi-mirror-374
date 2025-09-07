from __future__ import annotations

import json
import os
from click.testing import CliRunner

from chi_sdk.admin import cli


def test_admin_doctor_json_basic(tmp_path):
    # Ensure predictable environment: no chi-tui on PATH, no CHI_APP_BIN
    env = os.environ.copy()
    env.pop("CHI_APP_BIN", None)
    env.pop("PATH", None)  # drop PATH so chi-tui cannot be found
    env["CHI_TUI_JSON"] = "1"

    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"], env=env)
    # In JSON mode, command exits 0 with envelope ok=true; payload ok indicates result
    data = json.loads(result.output)
    assert data["ok"] is True
    payload = data["data"]
    assert payload["ok"] is False
    problems = payload["problems"]
    # Expect both: chi-tui missing and backend not set
    assert any("chi-tui not found" in p for p in problems)
    assert any("Backend app_bin not set" in p for p in problems)

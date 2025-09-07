from __future__ import annotations

import json
import os
from click.testing import CliRunner

from chi_sdk.admin import cli


def test_admin_init_scaffolds_wrapper_and_config(tmp_path):
    env = os.environ.copy()
    runner = CliRunner()
    proj = tmp_path

    # Run init
    res = runner.invoke(
        cli,
        [
            "init",
            str(proj),
            "--binary-name",
            "demo",
            "--config",
            ".tui",
        ],
        env=env,
    )
    assert res.exit_code == 0

    cfg_dir = proj / ".tui"
    assert (cfg_dir / "config.yaml").exists()
    assert (cfg_dir / "README.md").exists()

    # Wrapper scripts (POSIX + Windows)
    assert (cfg_dir / "bin" / "demo-ui").exists()
    assert (cfg_dir / "bin" / "demo-ui.bat").exists()

    # Doctor in JSON mode should report chi-tui missing but see app_bin from config
    env2 = env.copy()
    env2["CHI_TUI_JSON"] = "1"
    # Clear PATH to avoid picking any chi-tui
    env2.pop("PATH", None)
    res2 = runner.invoke(cli, ["doctor", "--config", str(cfg_dir)], env=env2)
    assert res2.exit_code == 0
    payload = json.loads(res2.output)["data"]
    assert payload["ok"] is False
    assert payload["info"].get("app_bin") == "demo"
    problems = payload["problems"]
    assert any("chi-tui not found" in p for p in problems)
    assert any("Backend 'demo' not found" in p for p in problems)

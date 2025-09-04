from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_cli(args, env_extra: dict[str, str] | None = None):
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "pmcc", "--config-dir", str(CONFIG_DIR), *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def extract_last_json(stdout: str):
    for line in reversed(stdout.strip().splitlines()):
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            import json

            return json.loads(s)
    raise AssertionError("未找到 JSON")


def test_cli_approval_required_and_approved_by_default():
    r = run_cli(["--summary-json", "--require-approval"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    data = extract_last_json(r.stdout)
    appr = data.get("approval", {})
    assert appr.get("required") is True and appr.get("approved") is True


def test_cli_approval_rejected_when_kill_switch():
    r = run_cli(["--summary-json", "--require-approval"], env_extra={"PMCC_KILL_SWITCH": "1"})
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    data = extract_last_json(r.stdout)
    appr = data.get("approval", {})
    assert appr.get("required") is True and appr.get("approved") is False

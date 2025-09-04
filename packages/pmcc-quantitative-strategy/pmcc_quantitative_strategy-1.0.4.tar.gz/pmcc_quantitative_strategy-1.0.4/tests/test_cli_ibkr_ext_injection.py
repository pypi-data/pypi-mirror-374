from __future__ import annotations

import json
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
            return json.loads(s)
    raise AssertionError("未找到 JSON")


def test_summary_json_ibkr_ext_env_injection():
    env_extra = {
        "PMCC_IBKR_COUNTERS": json.dumps({"success": 7, "error": 1}),
        "PMCC_IBKR_HEALTH": "blocked",
        "PMCC_KILL_SWITCH": "0",
    }
    r = run_cli(["--summary-json"], env_extra=env_extra)
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    data = extract_last_json(r.stdout)
    ext = data.get("ibkr", {}).get("ext", {})
    assert ext.get("health") == "blocked"
    assert ext.get("counters") == {"success": 7, "error": 1}


def test_summary_json_ibkr_ext_kill_switch_blocks():
    env_extra = {
        "PMCC_KILL_SWITCH": "1",
    }
    r = run_cli(["--summary-json"], env_extra=env_extra)
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    data = extract_last_json(r.stdout)
    ext = data.get("ibkr", {}).get("ext", {})
    assert ext.get("health") == "blocked"

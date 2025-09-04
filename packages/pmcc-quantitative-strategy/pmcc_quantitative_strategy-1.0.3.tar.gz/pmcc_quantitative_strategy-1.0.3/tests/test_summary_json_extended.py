from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_cli(args):
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
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


def test_summary_json_includes_exec_and_monitor_blocks():
    r = run_cli(["--summary-json"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    data = extract_last_json(r.stdout)
    # 附加字段为非破坏性（schema 允许 additionalProperties）
    assert "exec_plan" in data and isinstance(data["exec_plan"], dict)
    assert "monitor" in data and isinstance(data["monitor"], dict)

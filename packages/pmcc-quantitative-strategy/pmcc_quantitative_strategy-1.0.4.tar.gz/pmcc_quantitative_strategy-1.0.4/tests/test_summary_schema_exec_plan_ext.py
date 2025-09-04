from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "summary.json"


def run_pmcc(args):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pmcc", "--config-dir", str(CONFIG_DIR), *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def extract_last_json(stdout: str):
    payload = None
    for line in stdout.splitlines():
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                payload = json.loads(s)
            except Exception:
                continue
    return payload


def test_summary_json_exec_plan_ibkr_ext_validates_against_schema():
    r = run_pmcc(["--summary-json"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    payload = extract_last_json(r.stdout)
    assert isinstance(payload, dict)
    # ensure exec_plan and ibkr_ext exists
    assert "exec_plan" in payload and isinstance(payload["exec_plan"], dict)
    assert "ibkr_ext" in payload["exec_plan"]

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=payload, schema=schema)

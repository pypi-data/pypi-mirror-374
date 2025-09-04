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
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
    return payload


def test_summary_json_matches_schema():
    r = run_pmcc(["--summary-json"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    payload = extract_last_json(r.stdout)
    assert isinstance(payload, dict), "未能在 stdout 中解析到有效 JSON 摘要"

    # schema 存在且可读
    assert SCHEMA_PATH.exists(), f"缺少 schema: {SCHEMA_PATH}"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    # 校验
    jsonschema.validate(instance=payload, schema=schema)

    # 关键字段存在
    assert "universe" in payload
    assert "risk" in payload
    assert "events" in payload
    assert "modes" in payload
    assert "data_sources" in payload
    assert "system" in payload

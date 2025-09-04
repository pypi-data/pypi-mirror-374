import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_cli(args):
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
    # 取最后一行完整的 JSON（dumps 默认单行），避免 rfind("{") 命中内部嵌套对象
    for line in reversed(stdout.strip().splitlines()):
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            return json.loads(s)
    raise AssertionError(f"未找到 JSON：\n{stdout}")


def test_summary_json_structure_and_keys():
    r = run_cli(["--summary-json"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    data = extract_last_json(r.stdout)

    # 基本结构断言
    assert "universe" in data and "count" in data["universe"]
    assert "risk" in data and "cushion" in data["risk"]
    assert "events" in data and "macro" in data["events"]
    assert "modes" in data and "active_mode" in data["modes"]
    assert "data_sources" in data and "primary" in data["data_sources"]
    assert "system" in data and "cpu_cap" in data["system"]

    # 关键值与现有配置一致性
    assert data["universe"]["count"] == 20
    assert abs(data["risk"]["cushion"]["hard_floor"] - 0.15) < 1e-9
    assert data["modes"]["active_mode"] == "aggressive"
    assert data["events"]["macro"]["default_action"] == "throttle"
    assert data["data_sources"]["primary"]["market_data"] == "IBKR"
    assert abs(data["system"]["cpu_cap"] - 0.30) < 1e-9

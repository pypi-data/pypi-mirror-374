import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
PORTFOLIO_CFG = CONFIG_DIR / "portfolio_allocation.json"


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
    for line in reversed(stdout.strip().splitlines()):
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            return json.loads(s)
    raise AssertionError(f"未找到 JSON：\n{stdout}")


def test_portfolio_defaults_reflected_in_summary():
    # 从配置文件读取期望默认值，避免写死常量
    cfg = json.loads(PORTFOLIO_CFG.read_text(encoding="utf-8"))
    expected_redistribute = cfg.get("redistribute_leftover", False)
    expected_min_weight = cfg.get("min_total_weight", 0.95)

    r = run_cli(["--summary-json"])  # 仅打印到 stdout
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    data = extract_last_json(r.stdout)
    assert "portfolio" in data
    assert data["portfolio"]["redistribute_leftover"] == expected_redistribute
    assert data["portfolio"]["min_total_weight"] == expected_min_weight


def test_flag_redistribute_leftover_overrides_runtime():
    r = run_cli(["--summary-json", "--redistribute-leftover"])  # 打开开关
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    data = extract_last_json(r.stdout)
    assert data["portfolio"]["redistribute_leftover"] is True


def test_flag_min_total_weight_overrides_runtime():
    r = run_cli(["--summary-json", "--min-total-weight", "0.90"])  # 覆盖为 0.90
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    data = extract_last_json(r.stdout)
    assert data["portfolio"]["min_total_weight"] == 0.90

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


PMCC_ENV_VARS = [
    "PMCC_LIVE",
    "PMCC_CONFIG_DIR",
    "PMCC_IBKR_HOST",
    "PMCC_IBKR_CLIENT_ID",
    "PMCC_IBKR_USE_GATEWAY",
    "PMCC_IBKR_GATEWAY_PORT_LIVE",
    "PMCC_IBKR_GATEWAY_PORT_PAPER",
    "PMCC_IBKR_TWS_PORT_LIVE",
    "PMCC_IBKR_TWS_PORT_PAPER",
]


def run_cli(args, extra_env: dict | None = None):
    env = os.environ.copy()
    # Ensure isolation for PMCC_* affecting IBKR gating
    for k in PMCC_ENV_VARS:
        env.pop(k, None)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if extra_env:
        env.update(extra_env)
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


def ensure_no_keys_json_or_skip():
    keys_path = CONFIG_DIR / "keys.json"
    if keys_path.exists():
        pytest.skip("检测到 config/keys.json，可能干扰 ENV/默认值测试，跳过。")


def test_summary_json_ibkr_defaults_paper_tws():
    ensure_no_keys_json_or_skip()
    r = run_cli(["--summary-json"])  # 默认：paper 模式 + TWS 端口族
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    data = extract_last_json(r.stdout)
    assert "ibkr" in data

    ib = data["ibkr"]
    assert ib["mode"] == "paper"
    assert ib["use_gateway"] is False  # paper 默认 False
    assert ib["host"] == "127.0.0.1"
    assert ib["client_id"] == 1001
    assert ib["port"] == 7497  # TWS paper 默认端口


def test_summary_json_ibkr_live_flag_gateway_default():
    ensure_no_keys_json_or_skip()
    r = run_cli(["--summary-json", "--live"])  # --live 打开实盘 gating
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    data = extract_last_json(r.stdout)
    ib = data["ibkr"]
    assert ib["mode"] == "live"
    assert ib["use_gateway"] is True  # live 默认 True
    assert ib["host"] == "127.0.0.1"
    assert ib["client_id"] == 1001
    assert ib["port"] == 4001  # Gateway live 默认端口


def test_summary_json_ibkr_live_env_overrides_tws():
    ensure_no_keys_json_or_skip()
    env = {
        "PMCC_LIVE": "1",  # 环境驱动 live
        "PMCC_IBKR_HOST": "10.0.0.8",
        "PMCC_IBKR_CLIENT_ID": "777",
        "PMCC_IBKR_USE_GATEWAY": "false",  # 强制切到 TWS 族
        "PMCC_IBKR_TWS_PORT_LIVE": "17976",  # 自定义 TWS live 端口
    }
    r = run_cli(["--summary-json"], extra_env=env)
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    data = extract_last_json(r.stdout)
    ib = data["ibkr"]
    assert ib["mode"] == "live"
    assert ib["use_gateway"] is False
    assert ib["host"] == "10.0.0.8"
    assert ib["client_id"] == 777
    assert ib["port"] == 17976


def test_summary_json_ibkr_paper_gateway_env_port_override():
    ensure_no_keys_json_or_skip()
    env = {
        "PMCC_IBKR_USE_GATEWAY": "true",  # 在 paper 模式下强制 Gateway 族
        "PMCC_IBKR_GATEWAY_PORT_PAPER": "3999",  # 自定义 Gateway paper 端口
    }
    r = run_cli(["--summary-json"], extra_env=env)
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    data = extract_last_json(r.stdout)
    ib = data["ibkr"]
    assert ib["mode"] == "paper"
    assert ib["use_gateway"] is True
    assert ib["host"] == "127.0.0.1"
    assert ib["client_id"] == 1001
    assert ib["port"] == 3999

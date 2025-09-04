import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_cli(args):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "pmcc", "--config-dir", str(CONFIG_DIR), *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )


def test_cli_dry_risk():
    r = run_cli(["--dry-risk"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    assert "[RISK]" in r.stdout


def test_cli_dry_exec():
    r = run_cli(["--dry-exec"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    assert "[EXEC]" in r.stdout
    assert "当前滚动模式" in r.stdout  # 关键输出字段


def test_cli_dry_monitor():
    r = run_cli(["--dry-monitor"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    assert "[MON]" in r.stdout


def test_cli_bad_config_dir(tmp_path):
    bad_dir = tmp_path / "nope"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    r = subprocess.run(
        [sys.executable, "-m", "pmcc", "--config-dir", str(bad_dir)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 2
    assert "配置目录不存在" in r.stdout

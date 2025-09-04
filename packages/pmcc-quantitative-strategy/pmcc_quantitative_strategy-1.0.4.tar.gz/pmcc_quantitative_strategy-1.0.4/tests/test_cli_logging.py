import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


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


def test_log_level_warning_hides_info():
    r = run_pmcc(["--validate-schema", "--dry-risk", "--log-level", "WARNING"])
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 0
    assert "[RISK] 开始干跑风险检查" not in out


def test_log_level_info_shows_info():
    r = run_pmcc(["--validate-schema", "--dry-risk", "--log-level", "INFO"])
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 0
    assert "[RISK] 开始干跑风险检查" in out


def test_log_level_debug_shows_debug():
    r = run_pmcc(["--validate-schema", "--dry-risk", "--log-level", "DEBUG"])
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 0
    assert "[RISK][DEBUG]" in out


def test_log_level_propagates_to_all_modules():
    r = run_pmcc(["--validate-schema", "--dry-risk", "--dry-exec", "--dry-monitor", "--log-level", "ERROR"])
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 0
    assert "[RISK] 开始干跑执行" not in out  # 任何 INFO 级别不应出现
    assert "[EXEC] 开始干跑执行规划" not in out
    assert "[MON] 启动监控循环干跑" not in out

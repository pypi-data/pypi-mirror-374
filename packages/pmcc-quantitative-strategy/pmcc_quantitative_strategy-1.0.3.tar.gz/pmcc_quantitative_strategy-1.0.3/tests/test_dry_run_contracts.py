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


def test_dry_risk_contract():
    r = run_cli(["--dry-risk"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    out = r.stdout
    # 稳定前缀与关键字段
    assert "[RISK] 开始干跑风险检查" in out
    assert "Cushion: 硬下限=0.15" in out
    assert "目标=[0.2, 0.3]" in out
    assert "持仓上限: 单标权重≤0.2, 最大持仓数=10" in out
    assert "相关性控制: 成对相关≤0.8, 罚项权重=0.5" in out
    assert "回撤守护: 阈值=0.1, 动作=reduce" in out
    assert "风险检查干跑完成" in out


def test_dry_exec_contract():
    r = run_cli(["--dry-exec"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    out = r.stdout
    assert "[EXEC] 开始干跑执行规划" in out
    assert "数据源（主）：market=IBKR, options=IBKR" in out
    assert "当前滚动模式：aggressive" in out
    assert "事件窗口策略（宏观）：默认动作=throttle, 窗口±1天" in out
    assert "执行规划干跑完成" in out


def test_dry_monitor_contract():
    r = run_cli(["--dry-monitor"])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr
    out = r.stdout
    assert "[MON] 启动监控循环干跑" in out
    assert "CPU上限：0.3" in out
    assert "事件窗口（宏观）：默认动作=throttle，窗口±1天" in out
    assert "滚动模式：aggressive" in out
    assert "监控循环干跑完成" in out

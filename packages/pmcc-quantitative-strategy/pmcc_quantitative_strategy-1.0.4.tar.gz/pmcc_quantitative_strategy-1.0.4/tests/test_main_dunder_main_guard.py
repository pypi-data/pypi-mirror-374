from __future__ import annotations

import runpy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def test_main_module_dunder_main_guard_executes(monkeypatch):
    # 准备最小参数，确保主流程成功退出
    argv = [
        "pmcc.main",
        "--config-dir",
        str(CONFIG_DIR),
        "--summary-json",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    try:
        # 若已被其他用例导入，先移除以避免 runpy 的重复导入告警
        sys.modules.pop("pmcc.main", None)
        # 将 pmcc.main 作为 __main__ 运行，触发文件末尾哨兵行
        runpy.run_module("pmcc.main", run_name="__main__")
    except SystemExit as e:  # 正常退出
        assert e.code == 0

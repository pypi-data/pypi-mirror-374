import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def have_ruff():
    try:
        import ruff  # noqa: F401

        return True
    except Exception:
        return False


@pytest.mark.skipif(not have_ruff(), reason="ruff 未安装，跳过格式化检查测试")
class TestRuffFormat:
    def test_ruff_format_check_clean(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        r = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--check", "src", "tests"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            env=env,
        )
        assert r.returncode == 0, r.stdout + "\n" + r.stderr

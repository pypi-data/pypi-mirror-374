import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def have_mypy():
    try:
        import mypy  # type: ignore  # noqa: F401

        return True
    except Exception:
        return False


@pytest.mark.skipif(not have_mypy(), reason="mypy 未安装，跳过类型检查集成测试")
class TestMypy:
    def test_mypy_clean(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        r = subprocess.run(
            [sys.executable, "-m", "mypy", "--hide-error-context", "--no-color-output", "src/pmcc"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            env=env,
        )
        assert r.returncode == 0, r.stdout + "\n" + r.stderr

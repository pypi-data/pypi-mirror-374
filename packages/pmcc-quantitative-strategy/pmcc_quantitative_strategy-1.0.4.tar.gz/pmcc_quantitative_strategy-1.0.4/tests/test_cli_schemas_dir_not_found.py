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


def test_validate_schema_with_nonexistent_schemas_dir_should_exit_4(tmp_path: Path):
    missing = tmp_path / "schemas_not_exist"
    assert not missing.exists()
    r = run_pmcc(["--validate-schema", "--schemas-dir", str(missing)])
    # 期望 SchemaError → 退出码 4
    assert r.returncode == 4, r.stdout + "\n" + r.stderr
    out = r.stdout + "\n" + r.stderr
    assert "Schema 校验失败" in out
    assert "目录不存在" in out or "不存在" in out

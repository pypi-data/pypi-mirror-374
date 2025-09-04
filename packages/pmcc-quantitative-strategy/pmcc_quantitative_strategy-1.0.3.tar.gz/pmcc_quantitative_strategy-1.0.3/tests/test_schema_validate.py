import json
import os
import shutil
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


def test_schema_validate_ok():
    r = run_cli(["--validate-schema"])  # 默认使用 ./schemas
    assert r.returncode == 0, r.stdout + "\n" + r.stderr


def test_schema_validate_fail_invalid_type(tmp_path: Path):
    # 将 config 复制到临时目录
    tmp_cfg = tmp_path / "config_bad"
    tmp_cfg.mkdir()
    for p in CONFIG_DIR.glob("*.json"):
        shutil.copy2(p, tmp_cfg / p.name)

    # 破坏 data_sources.json: 将 primary.market_data 改为数字，触发 schema 类型错误
    bad_path = tmp_cfg / "data_sources.json"
    data = json.loads(bad_path.read_text(encoding="utf-8"))
    data["primary"]["market_data"] = 123  # 本应为 string
    bad_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    r = subprocess.run(
        [sys.executable, "-m", "pmcc", "--config-dir", str(tmp_cfg), "--validate-schema"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    # 期待非 0，并包含 schema 相关提示
    assert r.returncode != 0
    combined = (r.stdout + "\n" + r.stderr).lower()
    assert "schema" in combined

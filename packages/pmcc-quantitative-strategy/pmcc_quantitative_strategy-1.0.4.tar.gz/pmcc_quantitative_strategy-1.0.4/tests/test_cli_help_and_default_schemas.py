import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def test_cli_help_shows_schemas_dir():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    r = subprocess.run(
        [sys.executable, "-m", "pmcc", "--help"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0
    out = r.stdout
    assert "--schemas-dir" in out
    assert "--validate-schema" in out


def test_default_schemas_auto_detect_fail_on_schema_violation(tmp_path: Path):
    # 准备一份临时 config，将 event_filters.macro.window_days 改为字符串
    tmp_cfg = tmp_path / "config_bad"
    tmp_cfg.mkdir()
    for p in CONFIG_DIR.glob("*.json"):
        (tmp_cfg / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

    ev_path = tmp_cfg / "event_filters.json"
    data = json.loads(ev_path.read_text(encoding="utf-8"))
    data.setdefault("macro", {})["window_days"] = "7"  # schema 期望 integer
    ev_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 未传 --schemas-dir，但项目根存在 ./schemas，且已安装 jsonschema，应触发 jsonschema 校验失败
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
    # 期待非 0，并包含 schema 提示
    assert r.returncode != 0
    combined = (r.stdout + "\n" + r.stderr).lower()
    assert "schema" in combined

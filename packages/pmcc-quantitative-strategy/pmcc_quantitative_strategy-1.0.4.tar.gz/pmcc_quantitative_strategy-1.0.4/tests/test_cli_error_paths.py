import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_pmcc(args):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pmcc", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def copy_config(to_dir: Path) -> Path:
    to_dir.mkdir()
    for p in CONFIG_DIR.glob("*.json"):
        (to_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    return to_dir


def set_logging_file(cfg_dir: Path, file_path: Path):
    path = cfg_dir / "system.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("logging", {})["file"] = str(file_path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_cli_invalid_schemas_dir_fails(tmp_path: Path):
    # Skip if jsonschema is not available; main() falls back to minimal validation in that case
    pytest.importorskip("jsonschema")
    bad_dir = tmp_path / "no_such_schemas_dir"
    r = run_pmcc(
        [
            "--config-dir",
            str(CONFIG_DIR),
            "--validate-schema",
            "--schemas-dir",
            str(bad_dir),
        ]
    )
    combined = r.stdout + "\n" + r.stderr
    assert r.returncode != 0
    assert "Schema 校验失败" in combined
    assert "schemas 目录不存在" in combined or "目录不存在" in combined


def test_cli_missing_required_config_file(tmp_path: Path):
    cfg = copy_config(tmp_path / "cfg_missing")
    # Remove one required config
    missing = cfg / "risk_policy.json"
    if missing.exists():
        missing.unlink()

    r = run_pmcc(["--config-dir", str(cfg)])
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 2
    assert "缺少配置文件" in out


def test_cli_file_logging_writes_log(tmp_path: Path):
    cfg = copy_config(tmp_path / "cfg_logs")
    log_file = tmp_path / "logs" / "app.log"
    set_logging_file(cfg, log_file)

    r = run_pmcc(
        [
            "--config-dir",
            str(cfg),
            "--validate-schema",
            "--dry-risk",
            "--log-level",
            "INFO",
        ]
    )
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    # File should exist and contain risk dry-run output
    assert log_file.exists()
    txt = log_file.read_text(encoding="utf-8")
    assert "[RISK]" in txt

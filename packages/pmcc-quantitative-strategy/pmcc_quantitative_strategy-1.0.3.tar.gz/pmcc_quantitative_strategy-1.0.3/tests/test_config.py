import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_cli_with_config(config_dir: Path, extra_args=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    cmd = [sys.executable, "-m", "pmcc", "--config-dir", str(config_dir)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def copy_config_to(tmp_dir: Path) -> Path:
    target = tmp_dir / "config"
    shutil.copytree(CONFIG_DIR, target)
    return target


def test_missing_config_file_exit_2(tmp_path):
    cfg = copy_config_to(tmp_path)
    # 删除一个必需文件
    missing = cfg / "rolling_modes.json"
    missing.unlink()
    r = run_cli_with_config(cfg)
    assert r.returncode == 2, r.stdout + "\n" + r.stderr
    assert "缺少配置文件" in r.stdout


def test_invalid_config_schema_exit_3(tmp_path):
    cfg = copy_config_to(tmp_path)
    # 破坏必需字段 active_mode
    p = cfg / "rolling_modes.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data.pop("active_mode", None)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_cli_with_config(cfg)
    assert r.returncode == 3, r.stdout + "\n" + r.stderr
    assert "配置校验失败" in r.stdout

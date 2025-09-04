import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_pmcc(args, extra_env=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if extra_env:
        env.update(extra_env)
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


def set_system_concurrency(cfg_dir: Path, value: int):
    path = cfg_dir / "system.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["concurrency"] = value
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_env_config_dir_used_when_cli_absent(tmp_path: Path):
    env_cfg = copy_config(tmp_path / "env_cfg")
    set_system_concurrency(env_cfg, 999)

    r = run_pmcc(
        [
            "--validate-schema",
            "--dry-monitor",
            "--log-level",
            "INFO",
        ],
        extra_env={"PMCC_CONFIG_DIR": str(env_cfg)},
    )
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 0
    assert "[MON] 系统并发：999" in out


def test_cli_overrides_env_config_dir(tmp_path: Path):
    env_cfg = copy_config(tmp_path / "env_cfg")
    set_system_concurrency(env_cfg, 101)

    cli_cfg = copy_config(tmp_path / "cli_cfg")
    set_system_concurrency(cli_cfg, 202)

    r = run_pmcc(
        [
            "--config-dir",
            str(cli_cfg),
            "--validate-schema",
            "--dry-monitor",
            "--log-level",
            "INFO",
        ],
        extra_env={"PMCC_CONFIG_DIR": str(env_cfg)},
    )
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 0
    assert "[MON] 系统并发：202" in out
    assert "[MON] 系统并发：101" not in out

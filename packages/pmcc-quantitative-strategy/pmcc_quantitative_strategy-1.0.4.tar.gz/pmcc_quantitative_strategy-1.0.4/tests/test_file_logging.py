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


def set_logging_file(cfg_dir: Path, file_path: Path):
    sys_path = cfg_dir / "system.json"
    obj = json.loads(sys_path.read_text(encoding="utf-8"))
    obj.setdefault("logging", {})
    obj["logging"]["file"] = str(file_path)
    sys_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def test_file_logging_writes(tmp_path: Path):
    # 复制配置到临时目录，定向日志文件到临时 logs
    cfg_dir = copy_config(tmp_path / "cfg")
    out_dir = tmp_path / "logs"
    out_file = out_dir / "pmcc.log"
    set_logging_file(cfg_dir, out_file)

    r = run_pmcc(
        [
            "--config-dir",
            str(cfg_dir),
            "--dry-risk",
            "--log-level",
            "INFO",
        ]
    )
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    # 文件存在并包含关键日志片段
    assert out_file.exists(), f"日志文件未创建: {out_file}"
    content = out_file.read_text(encoding="utf-8")
    assert "[RISK] 开始干跑风险检查" in content

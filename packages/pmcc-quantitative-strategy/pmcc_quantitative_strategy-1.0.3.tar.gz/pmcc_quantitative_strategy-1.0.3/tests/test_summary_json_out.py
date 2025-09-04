import json
import os
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


def extract_last_json(stdout: str):
    for line in reversed(stdout.strip().splitlines()):
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            return json.loads(s)
    raise AssertionError(f"未找到 JSON：\n{stdout}")


def test_summary_json_out_writes_file_and_prints_stdout(tmp_path: Path):
    out_file = tmp_path / "summary.json"
    r = run_cli(["--summary-json-out", str(out_file)])
    assert r.returncode == 0, r.stdout + "\n" + r.stderr

    # 文件应存在且可解析
    assert out_file.exists()
    data_file = json.loads(out_file.read_text(encoding="utf-8"))

    # stdout 仍应包含 JSON
    data_stdout = extract_last_json(r.stdout)

    # 基本键存在
    for k in ["universe", "risk", "events", "modes", "data_sources", "system"]:
        assert k in data_file
        assert k in data_stdout

    # 关键值一致
    assert data_file["modes"]["active_mode"] == data_stdout["modes"]["active_mode"] == "aggressive"
    assert data_file["data_sources"]["primary"]["market_data"] == "IBKR"

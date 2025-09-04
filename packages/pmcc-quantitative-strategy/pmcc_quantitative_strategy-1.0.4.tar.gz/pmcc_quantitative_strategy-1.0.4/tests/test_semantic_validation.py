import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_pmcc(config_dir: Path, args):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pmcc", "--config-dir", str(config_dir), *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def copy_config(tmp_path: Path) -> Path:
    tmp_cfg = tmp_path / "config_copy"
    tmp_cfg.mkdir()
    for p in CONFIG_DIR.glob("*.json"):
        (tmp_cfg / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_cfg


def test_event_filters_window_days_negative_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "event_filters.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("macro", {})["window_days"] = -1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])  # 默认会自动检测 ./schemas
    assert r.returncode != 0
    combined = (r.stdout + "\n" + r.stderr).lower()
    assert "schema" in combined


def test_event_filters_default_action_invalid_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "event_filters.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("macro", {})["default_action"] = "invalid_action"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败
    assert r.returncode != 0
    combined = (r.stdout + "\n" + r.stderr).lower()
    assert "schema" in combined


def test_risk_policy_hard_floor_above_lower_bound_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "risk_policy.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    # 默认 target_range [0.20, 0.30]，将 hard_floor 调到 0.25 (> 0.20) 以违反约束 hard_floor <= lower_bound
    data.setdefault("cushion", {})["hard_floor"] = 0.25
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败
    assert r.returncode != 0
    combined = (r.stdout + "\n" + r.stderr).lower()
    assert "schema" in combined


def test_universe_tickers_pattern_invalid_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "universe_etf_20.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("tickers", []).append("spy")  # 小写应被拒绝
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败
    assert r.returncode != 0
    combined = (r.stdout + "\n" + r.stderr).lower()
    assert "schema" in combined

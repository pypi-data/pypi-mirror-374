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


def test_ta_invalid_timeframe_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "technical_analysis.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("divergence", {}).setdefault("timeframes", []).append("5M")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])
    assert r.returncode != 0


def test_ta_weights_sum_not_one_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "technical_analysis.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["divergence"]["weights"] = {"1D": 0.7, "4H": 0.3}  # 和为 1.0 但缺少 1H，后续再加一个不为1的场景
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败：键集合与 timeframes 不匹配
    assert r.returncode != 0

    # 再测和不为1的情况
    data = json.loads(path.read_text(encoding="utf-8"))
    data["divergence"]["weights"] = {"1D": 0.6, "4H": 0.3, "1H": 0.3}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败：0.6+0.3+0.3=1.2
    assert r.returncode != 0


def test_ta_event_window_weight_scale_out_of_range_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "technical_analysis.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["divergence"]["event_window_weight_scale"] = 1.5
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败：范围应在[0,1]
    assert r.returncode != 0


def test_ta_macd_fast_slow_order_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "technical_analysis.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["divergence"]["macd"]["fast"] = 30
    data["divergence"]["macd"]["slow"] = 12  # fast >= slow → 非法
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败
    assert r.returncode != 0


def test_ta_filters_min_price_negative_should_fail(tmp_path: Path):
    cfg = copy_config(tmp_path)
    path = cfg / "technical_analysis.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("filters", {})["min_price"] = -10
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = run_pmcc(cfg, ["--validate-schema"])  # 期待失败
    assert r.returncode != 0

from __future__ import annotations

import json
from pathlib import Path

import pmcc.execution as exec_mod

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def _load_cfgs() -> dict:
    required = [
        "data_sources.json",
        "universe_etf_20.json",
        "risk_policy.json",
        "event_filters.json",
        "rolling_modes.json",
        "technical_analysis.json",
        "system.json",
        "portfolio_allocation.json",
    ]
    out: dict[str, dict] = {}
    for name in required:
        out[name] = json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))
    return out


def test_execution_summarize_contains_ibkr_ext_with_counters():
    cfgs = _load_cfgs()
    s = exec_mod.summarize(cfgs)
    ext = s.get("ibkr_ext", {})
    assert isinstance(ext, dict)
    assert ext.get("health") == "ok"
    assert isinstance(ext.get("counters"), dict)
    assert set(ext["counters"]) == {"success", "error"}

from __future__ import annotations

import json
from pathlib import Path

import pmcc.execution as exec_mod
from pmcc.ext import with_ibkr_extensions

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


def test_exec_summarize_uses_injected_extensions():
    cfgs = _load_cfgs()
    cfgs_ex = with_ibkr_extensions(cfgs, counters={"success": 5, "error": 2}, health="warn")
    s = exec_mod.summarize(cfgs_ex)
    ext = s.get("ibkr_ext", {})
    assert ext.get("health") == "warn"
    assert ext.get("counters") == {"success": 5, "error": 2}

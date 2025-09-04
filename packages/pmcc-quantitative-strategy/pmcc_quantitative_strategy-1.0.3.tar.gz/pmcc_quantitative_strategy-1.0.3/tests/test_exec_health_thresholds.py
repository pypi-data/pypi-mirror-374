from __future__ import annotations

import json
from pathlib import Path

import pmcc.execution as exec_mod

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def _load_cfgs() -> dict:
    names = [
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
    for n in names:
        out[n] = json.loads((CONFIG_DIR / n).read_text(encoding="utf-8"))
    return out


def test_exec_derive_health_via_thresholds_in_extensions():
    cfgs = _load_cfgs()
    cfgs["__extensions__"] = {
        "ibkr_counters": {"success": 8, "error": 2},
        "health_thresholds": {"warn_error_rate": 0.1, "block_error_rate": 0.5, "block_burst": 5},
    }
    s = exec_mod.summarize(cfgs)
    assert s.get("ibkr_ext", {}).get("health") == "warn"

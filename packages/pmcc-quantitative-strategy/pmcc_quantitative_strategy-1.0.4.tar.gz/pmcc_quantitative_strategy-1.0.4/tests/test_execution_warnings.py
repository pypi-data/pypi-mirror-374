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


def test_execution_summarize_emits_warning_when_throttle_missing():
    cfgs = _load_cfgs()
    # Remove throttle to trigger the non-breaking warning branch
    ds = dict(cfgs["data_sources.json"])  # shallow copy
    ds.pop("throttle", None)
    cfgs = dict(cfgs)
    cfgs["data_sources.json"] = ds

    s = exec_mod.summarize(cfgs)
    assert isinstance(s.get("warnings"), list)
    assert "missing_throttle" in s["warnings"]


def test_execution_health_fallback_ok_when_derive_raises(monkeypatch):
    import json
    from pathlib import Path

    import pmcc.execution as exec_mod
    import pmcc.health as health_mod

    # Prepare minimal cfgs
    proj_root = Path(__file__).resolve().parents[1]
    cfg_dir = proj_root / "config"
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
    cfgs: dict[str, dict] = {}
    for n in names:
        cfgs[n] = json.loads((cfg_dir / n).read_text(encoding="utf-8"))
    cfgs["__extensions__"] = {
        "ibkr_counters": {"success": 1, "error": 1},
        "health_thresholds": {"warn_error_rate": 0.1},
    }

    # Make derive_health raise to exercise fallback path in summarize()
    def boom(*_a, **_k):  # noqa: D401 - test stub
        raise RuntimeError("boom")

    monkeypatch.setattr(health_mod, "derive_health", boom)
    s = exec_mod.summarize(cfgs)
    assert s.get("ibkr_ext", {}).get("health") == "ok"

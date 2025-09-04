from __future__ import annotations

import json
from pathlib import Path

import pmcc.execution as exec_mod
import pmcc.monitor as mon_mod

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


def test_execution_summarize_basic_structure():
    cfgs = _load_cfgs()
    s = exec_mod.summarize(cfgs)
    assert s["rolling_mode"] == cfgs["rolling_modes.json"]["active_mode"]
    assert "primary" in s["data_sources"] and "throttle" in s["data_sources"]
    assert (
        s["data_sources"]["throttle"]["requests_per_sec"] == cfgs["data_sources.json"]["throttle"]["requests_per_sec"]
    )
    assert "macro" in s["events"]
    # events policy present
    ep = s.get("events_policy", {})
    assert "throttle_coeff" in ep and "delta_shift" in ep
    assert "order_template" in s["plan"]
    # pre_checks_verbose is a list of strings
    pcv = s["plan"].get("pre_checks_verbose", [])
    assert isinstance(pcv, list) and all(isinstance(x, str) for x in pcv)
    # status always ok in summarize (dry-run)
    assert s.get("status") == "ok"
    # pre_checks_detail exists with dict entries
    pcd = s["plan"].get("pre_checks_detail", [])
    assert isinstance(pcd, list) and all(isinstance(x, dict) for x in pcd)
    assert {"name", "description", "applies"}.issubset(set(pcd[0].keys()))
    # suggestions_labeled list of {text, level}
    sl = s.get("suggestions_labeled", [])
    assert isinstance(sl, list) and all(isinstance(x, dict) for x in sl)
    assert {"text", "level"}.issubset(set(sl[0].keys()))
    # constraints mirror risk policy
    assert (
        s["constraints"]["position_limits"]["max_positions"]
        == cfgs["risk_policy.json"]["position_limits"]["max_positions"]
    )
    # mode configuration present and reflects active mode
    m = cfgs["rolling_modes.json"]
    active = m["active_mode"]
    assert s["mode_config"]["short_call"]["target_dte"] == m[active]["short_call"]["target_dte"]
    # hints are present and boolean
    assert set(s["hints"]) == {"has_short_call", "has_events_adjustment", "has_general"}
    assert all(isinstance(v, bool) for v in s["hints"].values())
    # official_events & notes & universe_count
    assert isinstance(s["official_events"], list) and "fomc" in s["official_events"]
    assert s["notes"] == cfgs["data_sources.json"]["notes"]
    assert s["universe_count"] == len(cfgs["universe_etf_20.json"]["tickers"])
    # suggestions present
    assert isinstance(s.get("suggestions"), list) and all(isinstance(x, str) for x in s["suggestions"])
    # fields & contract & warnings
    fp = s.get("fields_present", {})
    assert set(fp) == {"has_primary", "has_throttle", "has_macro"}
    c = s.get("contract", {})
    assert c.get("name") == "exec_plan" and isinstance(c.get("version"), str)
    assert isinstance(s.get("warnings"), list)


def test_monitor_summarize_basic_structure():
    cfgs = _load_cfgs()
    s = mon_mod.summarize(cfgs)
    assert s["rolling_mode"] == cfgs["rolling_modes.json"]["active_mode"]
    assert "cpu_cap" in s["system"]
    assert "macro" in s["events"]
    # risk & portfolio blocks reflect config
    assert abs(s["risk"]["cushion"]["hard_floor"] - cfgs["risk_policy.json"]["cushion"]["hard_floor"]) < 1e-12
    assert s["risk"]["correlation"]["max_pairwise"] == cfgs["risk_policy.json"]["correlation_control"]["max_pairwise"]
    assert (
        s["portfolio"]["rebalance_triggers"]["time_based_days"]
        == cfgs["portfolio_allocation.json"]["rebalance_triggers"]["time_based_days"]
    )
    # checks include cushion relation, underweight threshold and max_pairwise
    assert "cushion_floor_lt_target_low" in s["checks"]
    assert s["checks"]["underweight_threshold"] == cfgs["portfolio_allocation.json"]["min_total_weight"]
    assert s["checks"]["max_pairwise"] == cfgs["risk_policy.json"]["correlation_control"]["max_pairwise"]
    # universe & events_priority
    assert s["universe"]["count"] == len(cfgs["universe_etf_20.json"]["tickers"])
    assert s["events_priority"] == cfgs["event_filters.json"]["macro"]["priority"]
    # suggestions present
    assert isinstance(s.get("suggestions"), list) and any("rebalance" in t for t in s["suggestions"])
    # labeled suggestions present, checks_failed is int, alerts empty and fields/contract present
    sl = s.get("suggestions_labeled", [])
    assert isinstance(sl, list) and all({"text", "level"}.issubset(set(d.keys())) for d in sl)
    assert isinstance(s.get("checks_failed"), int)
    assert isinstance(s.get("alerts"), list) and len(s["alerts"]) == 0
    fp = s.get("fields_present", {})
    assert set(fp) == {"has_macro", "has_cushion", "has_correlation"}
    c = s.get("contract", {})
    assert c.get("name") == "monitor_summary" and isinstance(c.get("version"), str)


def test_monitor_summarize_cushion_status_exception_path():
    cfgs = _load_cfgs()
    # Corrupt cushion.hard_floor to trigger exception in status derivation
    cfgs["risk_policy.json"]["cushion"]["hard_floor"] = "not-a-number"  # type: ignore[assignment]
    s = mon_mod.summarize(cfgs)
    # Should handle gracefully and set status to a valid string
    assert s.get("status") in {"ok", "warn"}

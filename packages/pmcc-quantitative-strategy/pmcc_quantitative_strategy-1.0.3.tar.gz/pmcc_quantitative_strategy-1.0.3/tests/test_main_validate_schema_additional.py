from __future__ import annotations

import json
from pathlib import Path

import pmcc.main as main_mod

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
    ]
    out: dict[str, dict] = {}
    for name in required:
        out[name] = json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))
    return out


def test_universe_tickers_wrong_type_should_fail():
    cfgs = _load_cfgs()
    cfgs["universe_etf_20.json"]["tickers"] = "BAD"  # type: ignore[assignment]
    try:
        main_mod.validate_schema(cfgs, None)
        assert False, "expected SchemaError"
    except main_mod.SchemaError:
        pass


def test_risk_cushion_hard_floor_type_invalid_should_fail():
    cfgs = _load_cfgs()
    cfgs["risk_policy.json"]["cushion"]["hard_floor"] = "x"  # type: ignore[assignment]
    try:
        main_mod.validate_schema(cfgs, None)
        assert False, "expected SchemaError"
    except main_mod.SchemaError:
        pass


def test_risk_cushion_target_range_invalid_should_fail():
    cfgs = _load_cfgs()
    cfgs["risk_policy.json"]["cushion"]["target_range"] = [0.2]
    try:
        main_mod.validate_schema(cfgs, None)
        assert False, "expected SchemaError"
    except main_mod.SchemaError:
        pass


def test_ta_timeframes_type_invalid_should_fail():
    cfgs = _load_cfgs()
    cfgs["technical_analysis.json"]["divergence"]["timeframes"] = "BAD"  # type: ignore[assignment]
    try:
        main_mod.validate_schema(cfgs, None)
        assert False, "expected SchemaError"
    except main_mod.SchemaError:
        pass


def test_ta_timeframes_value_invalid_should_fail():
    cfgs = _load_cfgs()
    cfgs["technical_analysis.json"]["divergence"]["timeframes"] = ["1D", "4H", "5M"]
    try:
        main_mod.validate_schema(cfgs, None)
        assert False, "expected SchemaError"
    except main_mod.SchemaError:
        pass

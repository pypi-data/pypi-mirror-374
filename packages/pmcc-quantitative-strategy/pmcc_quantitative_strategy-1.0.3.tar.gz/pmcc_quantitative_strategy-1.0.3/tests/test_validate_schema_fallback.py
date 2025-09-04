import json
from pathlib import Path

import pytest

from pmcc.main import SchemaError, validate_schema

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


REQUIRED = [
    "data_sources.json",
    "universe_etf_20.json",
    "risk_policy.json",
    "event_filters.json",
    "rolling_modes.json",
    "technical_analysis.json",
    "system.json",
]


def load_cfgs() -> dict:
    cfgs: dict[str, dict] = {}
    for name in REQUIRED:
        path = CONFIG_DIR / name
        cfgs[name] = json.loads(path.read_text(encoding="utf-8"))
    return cfgs


def test_validate_schema_fallback_positive():
    cfgs = load_cfgs()
    # 不提供 schemas_dir → 只走内置语义校验
    validate_schema(cfgs, None)


def test_validate_schema_fallback_negative_data_sources_type():
    cfgs = load_cfgs()
    cfgs["data_sources.json"]["primary"]["market_data"] = 123  # 非字符串
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)


def test_validate_schema_fallback_negative_ta_weights_keyset_and_sum():
    cfgs = load_cfgs()
    div = cfgs["technical_analysis.json"].setdefault("divergence", {})
    # 先制造键集合不一致
    div["timeframes"] = ["1D", "4H", "1H"]
    div["weights"] = {"1D": 0.5, "4H": 0.5}  # 缺少 1H
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    # 再制造和不为 1 的情况（键集合一致）
    cfgs = load_cfgs()
    div = cfgs["technical_analysis.json"].setdefault("divergence", {})
    div["timeframes"] = ["1D", "4H", "1H"]
    div["weights"] = {"1D": 0.6, "4H": 0.3, "1H": 0.3}  # 和为 1.2
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

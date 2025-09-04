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


@pytest.mark.usefixtures()
def test_schema_dir_not_exist_raises(tmp_path: Path):
    pytest.importorskip("jsonschema")
    cfgs = load_cfgs()
    bad_dir = tmp_path / "no_such"
    with pytest.raises(SchemaError):
        validate_schema(cfgs, str(bad_dir))


def test_schema_invalid_json_raises(tmp_path: Path):
    pytest.importorskip("jsonschema")
    cfgs = load_cfgs()
    sdir = tmp_path / "schemas"
    sdir.mkdir()
    # Write invalid JSON to system.json
    (sdir / "system.json").write_text("{ invalid", encoding="utf-8")
    with pytest.raises(SchemaError):
        validate_schema(cfgs, str(sdir))


def test_schema_invalid_schema_object_raises(tmp_path: Path):
    pytest.importorskip("jsonschema")
    cfgs = load_cfgs()
    sdir = tmp_path / "schemas"
    sdir.mkdir()
    # Valid JSON but invalid schema
    (sdir / "system.json").write_text('{"type": 123}', encoding="utf-8")
    with pytest.raises(SchemaError):
        validate_schema(cfgs, str(sdir))


def test_import_jsonschema_fail_fallback(monkeypatch):
    cfgs = load_cfgs()

    real_import = __import__

    def fake_import(name, *args, **kwargs):  # pragma: no cover - only the specific branch is relevant
        if name == "jsonschema":
            raise ImportError("no jsonschema")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)
    # Provide a real schemas dir; import should fail and fallback should pass
    validate_schema(cfgs, str(PROJECT_ROOT / "schemas"))


def test_events_validation_errors():
    cfgs = load_cfgs()
    macro = cfgs["event_filters.json"]["macro"]

    macro["default_action"] = 123  # not a string
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    cfgs = load_cfgs()
    macro = cfgs["event_filters.json"]["macro"]
    macro["default_action"] = "not_allowed"
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    cfgs = load_cfgs()
    macro = cfgs["event_filters.json"]["macro"]
    macro["window_days"] = -1
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)


def test_modes_and_system_validation_errors():
    cfgs = load_cfgs()
    cfgs["rolling_modes.json"]["active_mode"] = 123
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    cfgs = load_cfgs()
    cfgs["system.json"]["cpu_cap"] = "NaN"
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)


def test_ta_semantic_errors():
    # Duplicate timeframes
    cfgs = load_cfgs()
    div = cfgs["technical_analysis.json"]["divergence"]
    div["timeframes"] = ["1D", "1D", "4H"]
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    # Weights keys not strings
    cfgs = load_cfgs()
    div = cfgs["technical_analysis.json"]["divergence"]
    div["weights"] = {1: 0.5, "1D": 0.5, "4H": 0.0, "1H": 0.0}  # type: ignore[dict-item]
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    # Weights values out of range
    cfgs = load_cfgs()
    div = cfgs["technical_analysis.json"]["divergence"]
    div["weights"] = {"1D": 1.1, "4H": 0.0, "1H": -0.1}
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    # Event window weight scale out of [0,1]
    cfgs = load_cfgs()
    cfgs["technical_analysis.json"]["divergence"]["event_window_weight_scale"] = 1.5
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    # MACD type invalid
    cfgs = load_cfgs()
    cfgs["technical_analysis.json"]["divergence"]["macd"]["fast"] = "12"  # type: ignore[assignment]
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    # MACD order invalid
    cfgs = load_cfgs()
    macd = cfgs["technical_analysis.json"]["divergence"]["macd"]
    macd["fast"] = 30
    macd["slow"] = 12
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

    # Filters min_price negative
    cfgs = load_cfgs()
    cfgs["technical_analysis.json"]["filters"]["min_price"] = -1
    with pytest.raises(SchemaError):
        validate_schema(cfgs, None)

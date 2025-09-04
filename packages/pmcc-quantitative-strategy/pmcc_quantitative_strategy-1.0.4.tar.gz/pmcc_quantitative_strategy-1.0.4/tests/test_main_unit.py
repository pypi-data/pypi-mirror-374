import json
import logging
import os
from pathlib import Path

import pmcc.main as main_mod

# note: pytest import removed as it was unused and violated ruff F401

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


PMCC_ENV_VARS = [
    "PMCC_LIVE",
    "PMCC_CONFIG_DIR",
    "PMCC_IBKR_HOST",
    "PMCC_IBKR_CLIENT_ID",
    "PMCC_IBKR_USE_GATEWAY",
    "PMCC_IBKR_GATEWAY_PORT_LIVE",
    "PMCC_IBKR_GATEWAY_PORT_PAPER",
    "PMCC_IBKR_TWS_PORT_LIVE",
    "PMCC_IBKR_TWS_PORT_PAPER",
]


def _clear_pmcc_env():
    for k in PMCC_ENV_VARS:
        os.environ.pop(k, None)


def test_env_bool_and_int_parsers(monkeypatch):
    # bool default
    assert main_mod._env_bool("NON_EXISTENT", False) is False
    assert main_mod._env_bool("NON_EXISTENT", True) is True

    # truthy variants
    for v in ["1", "true", " True ", "YES", "y", "on"]:
        monkeypatch.setenv("TEST_BOOL", v)
        assert main_mod._env_bool("TEST_BOOL", False) is True

    # falsy variants
    for v in ["0", "false", "no", "off", "n", " "]:
        monkeypatch.setenv("TEST_BOOL", v)
        assert main_mod._env_bool("TEST_BOOL", True) is False

    # int default
    assert main_mod._env_int("TEST_INT", 7) == 7
    # valid
    monkeypatch.setenv("TEST_INT", " 42 ")
    assert main_mod._env_int("TEST_INT", 7) == 42
    # invalid -> fallback
    monkeypatch.setenv("TEST_INT", "abc")
    assert main_mod._env_int("TEST_INT", 7) == 7


def test_resolve_ibkr_summary_defaults(monkeypatch, tmp_path: Path):
    _clear_pmcc_env()
    # No keys.json present; paper mode defaults to TWS:7497
    ib = main_mod._resolve_ibkr_summary(tmp_path, live_flag=False)
    assert ib["mode"] == "paper"
    assert ib["use_gateway"] is False
    assert ib["host"] == "127.0.0.1"
    assert ib["client_id"] == 1001
    assert ib["port"] == 7497

    # Live mode defaults to Gateway:4001
    ib2 = main_mod._resolve_ibkr_summary(tmp_path, live_flag=True)
    assert ib2["mode"] == "live"
    assert ib2["use_gateway"] is True
    assert ib2["port"] == 4001


def test_resolve_ibkr_summary_with_keys_json_overrides(monkeypatch, tmp_path: Path):
    _clear_pmcc_env()
    keys = {
        "ibkr": {
            "host": "192.168.0.1",
            "client_id": 123,
            "use_gateway": False,
            "ports": {
                "gateway": {"live": 5001, "paper": 5002},
                "tws": {"live": 6001, "paper": 6002},
            },
        }
    }
    (tmp_path / "keys.json").write_text(json.dumps(keys), encoding="utf-8")

    # live=True but keys force use_gateway=False -> choose TWS live port
    ib_live = main_mod._resolve_ibkr_summary(tmp_path, live_flag=True)
    assert ib_live["mode"] == "live"
    assert ib_live["use_gateway"] is False
    assert ib_live["host"] == "192.168.0.1"
    assert ib_live["client_id"] == 123
    assert ib_live["port"] == 6001

    # paper mode -> keys use_gateway=False (TWS) -> port 6002
    ib_paper = main_mod._resolve_ibkr_summary(tmp_path, live_flag=False)
    assert ib_paper["mode"] == "paper"
    assert ib_paper["use_gateway"] is False
    assert ib_paper["port"] == 6002


def test_resolve_ibkr_summary_env_overrides(monkeypatch, tmp_path: Path):
    # Prepare keys that would otherwise set different values
    keys = {
        "ibkr": {
            "host": "10.10.10.10",
            "client_id": 111,
            "use_gateway": True,
            "ports": {
                "gateway": {"live": 5001, "paper": 5002},
                "tws": {"live": 6001, "paper": 6002},
            },
        }
    }
    (tmp_path / "keys.json").write_text(json.dumps(keys), encoding="utf-8")

    # ENV wins over keys
    monkeypatch.setenv("PMCC_LIVE", "1")
    monkeypatch.setenv("PMCC_IBKR_HOST", "10.0.0.8")
    monkeypatch.setenv("PMCC_IBKR_CLIENT_ID", "777")
    monkeypatch.setenv("PMCC_IBKR_USE_GATEWAY", "false")  # force TWS
    monkeypatch.setenv("PMCC_IBKR_TWS_PORT_LIVE", "17976")

    ib = main_mod._resolve_ibkr_summary(tmp_path, live_flag=True)
    assert ib["mode"] == "live"
    assert ib["use_gateway"] is False
    assert ib["host"] == "10.0.0.8"
    assert ib["client_id"] == 777
    assert ib["port"] == 17976


def test_configure_file_logging_and_ensure_dirs(tmp_path: Path, caplog):
    # ensure_dirs creates parents
    system_cfg = {
        "logging": {"file": str(tmp_path / "logs" / "app.log")},
        "cache": {"path": str(tmp_path / "cache")},
    }
    main_mod.ensure_dirs(system_cfg)
    assert (tmp_path / "logs").is_dir()
    assert (tmp_path / "cache").is_dir()

    # configure_file_logging attaches a file handler and writes
    caplog.set_level(logging.INFO)
    main_mod.configure_file_logging(system_cfg, logging.INFO)
    logging.getLogger().info("hello-file")

    # flush file handler
    logging.shutdown()
    content = (tmp_path / "logs" / "app.log").read_text(encoding="utf-8")
    assert "hello-file" in content


def test_validate_schema_and_summarize():
    # Load real configs and call validate_schema + summarize directly
    cfgs = {}
    for name in [
        "data_sources.json",
        "universe_etf_20.json",
        "risk_policy.json",
        "event_filters.json",
        "rolling_modes.json",
        "technical_analysis.json",
        "system.json",
        "portfolio_allocation.json",
    ]:
        cfgs[name] = main_mod.load_json(CONFIG_DIR / name)

    # Should run without raising
    main_mod.validate_schema(cfgs)

    # Exercise summarize printing
    main_mod.summarize(cfgs)

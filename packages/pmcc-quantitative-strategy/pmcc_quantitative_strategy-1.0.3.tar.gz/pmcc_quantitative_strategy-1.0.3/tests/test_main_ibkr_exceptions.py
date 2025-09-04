from __future__ import annotations

import json
from pathlib import Path

import pmcc.main as main_mod


def test_resolve_ibkr_summary_ignores_invalid_keys_json(tmp_path: Path):
    # Write invalid JSON to keys.json; function should swallow and use defaults
    (tmp_path / "keys.json").write_text("{ invalid", encoding="utf-8")
    info = main_mod._resolve_ibkr_summary(tmp_path, live_flag=False)
    assert info["mode"] == "paper" and isinstance(info["port"], int)


def test_resolve_ibkr_summary_ports_field_invalid_triggers_fallback(tmp_path: Path):
    # ports is not a dict; access .get should raise and be ignored in both branches
    keys = {"ibkr": {"use_gateway": True, "ports": 123}}
    (tmp_path / "keys.json").write_text(json.dumps(keys), encoding="utf-8")
    live = main_mod._resolve_ibkr_summary(tmp_path, live_flag=True)
    assert live["use_gateway"] is True and isinstance(live["port"], int)

    # Switch to TWS branch
    keys = {"ibkr": {"use_gateway": False, "ports": 123}}
    (tmp_path / "keys.json").write_text(json.dumps(keys), encoding="utf-8")
    paper = main_mod._resolve_ibkr_summary(tmp_path, live_flag=False)
    assert paper["use_gateway"] is False and isinstance(paper["port"], int)


def test_resolve_ibkr_summary_gateway_ports_override_ok(tmp_path: Path):
    keys = {
        "ibkr": {
            "use_gateway": True,
            "ports": {"gateway": {"live": 5011, "paper": 5012}},
        }
    }
    (tmp_path / "keys.json").write_text(json.dumps(keys), encoding="utf-8")
    live = main_mod._resolve_ibkr_summary(tmp_path, live_flag=True)
    assert live["use_gateway"] is True and live["port"] == 5011
    paper = main_mod._resolve_ibkr_summary(tmp_path, live_flag=False)
    assert paper["use_gateway"] is True and paper["port"] == 5012

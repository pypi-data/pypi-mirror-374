from __future__ import annotations

from pathlib import Path

import pmcc.main as main_mod


class _BadDict(dict):
    def get(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("bad get")


def test_resolve_ibkr_summary_gateway_ports_get_raises(monkeypatch, tmp_path: Path):
    # Ensure keys.json exists (content ignored by patched json.loads)
    (tmp_path / "keys.json").write_text("{}", encoding="utf-8")

    def _fake_loads(_text: str):  # type: ignore[no-untyped-def]
        return {"ibkr": {"ports": _BadDict()}}

    monkeypatch.setattr(main_mod.json, "loads", _fake_loads, raising=True)

    # live_flag=True ⇒ default use_gateway=True ⇒ exercise gateway branch
    info = main_mod._resolve_ibkr_summary(tmp_path, live_flag=True)
    assert info["mode"] == "live" and info["use_gateway"] is True and isinstance(info["port"], int)


def test_resolve_ibkr_summary_tws_ports_get_raises(monkeypatch, tmp_path: Path):
    # Ensure keys.json exists (content ignored by patched json.loads)
    (tmp_path / "keys.json").write_text("{}", encoding="utf-8")

    def _fake_loads(_text: str):  # type: ignore[no-untyped-def]
        return {"ibkr": {"ports": _BadDict()}}

    monkeypatch.setattr(main_mod.json, "loads", _fake_loads, raising=True)
    # Force TWS family via ENV override, even in live mode
    monkeypatch.setenv("PMCC_IBKR_USE_GATEWAY", "false")

    info = main_mod._resolve_ibkr_summary(tmp_path, live_flag=True)
    assert info["mode"] == "live" and info["use_gateway"] is False and isinstance(info["port"], int)

from __future__ import annotations

from pmcc.pretrade import run_pretrade_checks


def test_pretrade_ok_and_kill_switch(monkeypatch, cfgs_default):
    # ok case
    monkeypatch.delenv("PMCC_KILL_SWITCH", raising=False)
    r = run_pretrade_checks(cfgs_default)
    assert r.ok and r.data and r.data.ok is True
    # kill switch case
    monkeypatch.setenv("PMCC_KILL_SWITCH", "1")
    r2 = run_pretrade_checks(cfgs_default)
    assert r2.ok and r2.data and r2.data.ok is False and "kill_switch_active" in r2.data.reasons


def test_pretrade_macro_freeze(monkeypatch, cfgs_default):
    import copy

    cfgs2 = copy.deepcopy(cfgs_default)
    cfgs2["event_filters.json"]["macro"]["default_action"] = "freeze"
    r = run_pretrade_checks(cfgs2)
    assert r.ok and r.data and r.data.ok is False and "macro_freeze" in r.data.reasons

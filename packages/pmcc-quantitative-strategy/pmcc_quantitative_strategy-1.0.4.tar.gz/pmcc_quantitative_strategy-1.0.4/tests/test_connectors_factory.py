from __future__ import annotations

from pmcc.connectors import get_market_data_provider, get_options_provider, get_throttle
from pmcc.contracts import OptionChainRequest, PMCCErrorCode, QuoteRequest


def test_connectors_mock_and_real_toggle(monkeypatch):
    # mock backend
    monkeypatch.delenv("PMCC_DATA_BACKEND", raising=False)
    prov = get_market_data_provider({})
    r = prov.get_quote(QuoteRequest(symbol="SPY"))
    assert r.ok is True and r.data and r.data.symbol == "SPY"
    # real backend (not implemented)
    monkeypatch.setenv("PMCC_DATA_BACKEND", "real")
    prov2 = get_market_data_provider({})
    r2 = prov2.get_quote(QuoteRequest(symbol="SPY"))
    assert r2.ok is False and r2.error and r2.error.code == PMCCErrorCode.NOT_IMPLEMENTED
    # also cover get_quotes on real backend
    _ = prov2.get_quotes(type("RQ", (), {"symbols": ["SPY", "QQQ"]})())


def test_connectors_get_throttle(cfgs_default):
    th = get_throttle(cfgs_default)
    assert isinstance(th, dict) and "requests_per_sec" in th


def test_get_options_provider_mock_and_real(monkeypatch):
    # mock
    monkeypatch.delenv("PMCC_DATA_BACKEND", raising=False)
    op = get_options_provider({})
    mr = op.get_chain(OptionChainRequest(symbol="SPY"))
    assert mr.ok and mr.data and len(mr.data) == 10
    # real placeholder
    monkeypatch.setenv("PMCC_DATA_BACKEND", "real")
    op2 = get_options_provider({})
    rr = op2.get_chain(OptionChainRequest(symbol="SPY"))
    assert rr.ok is False and rr.error

from __future__ import annotations

import pmcc.adapters as adp
import pmcc.contracts as c


def test_market_data_adapter_basic_quote_and_quotes():
    adapter = adp.MarketDataAdapter()
    r1 = adapter.get_quote(c.QuoteRequest(symbol="SPY"))
    assert r1.ok and r1.data and r1.data.symbol == "SPY"

    r2 = adapter.get_quotes(c.SymbolsRequest(symbols=["SPY", "QQQ"]))
    assert r2.ok and r2.data and len(r2.data.quotes) == 2
    assert {q.symbol for q in r2.data.quotes} == {"SPY", "QQQ"}


def test_market_data_adapter_error_mapping(monkeypatch):
    adapter = adp.MarketDataAdapter()

    def _boom(_sym: str):  # type: ignore[no-untyped-def]
        raise RuntimeError("backend error")

    monkeypatch.setattr(adapter._b, "get_quote", _boom, raising=True)  # type: ignore[attr-defined]
    r = adapter.get_quote(c.QuoteRequest(symbol="SPY"))
    assert r.ok is False and r.error and r.error.code == c.PMCCErrorCode.NETWORK_ERROR


def test_market_data_adapter_error_mapping_bulk(monkeypatch):
    adapter = adp.MarketDataAdapter()

    calls = {"n": 0}

    def _boom_on_second(_sym: str):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("backend error bulk")
        return adapter._b.get_quote("SPY")  # type: ignore[attr-defined]

    monkeypatch.setattr(adapter._b, "get_quote", _boom_on_second, raising=True)  # type: ignore[attr-defined]
    r = adapter.get_quotes(c.SymbolsRequest(symbols=["SPY", "QQQ"]))
    assert r.ok is False and r.error and r.error.code == c.PMCCErrorCode.NETWORK_ERROR


def test_market_data_adapter_counters_increment():
    adapter = adp.MarketDataAdapter()
    assert adapter.get_counters() == {"success": 0, "error": 0}
    adapter.get_quote(c.QuoteRequest(symbol="SPY"))
    adapter.get_quotes(c.SymbolsRequest(symbols=["SPY", "QQQ"]))
    cnt = adapter.get_counters()
    # 1 success for single + 2 success for bulk = 3
    assert cnt["success"] >= 3 and cnt["error"] == 0

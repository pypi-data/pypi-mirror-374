from __future__ import annotations

from pmcc.connectors import get_market_data_provider, get_options_provider
from pmcc.contracts import OptionChainRequest, PMCCErrorCode, QuoteRequest


def test_real_stub_market_and_options_success(monkeypatch):
    # Enable real stub path
    monkeypatch.setenv("PMCC_DATA_BACKEND", "real")
    monkeypatch.setenv("PMCC_REAL_STUB", "1")

    # Patch default fetcher to return deterministic data
    import pmcc.connectors as con

    def fake_fetcher(ep: str, params: dict):  # noqa: D401 - test stub
        if "options" in ep:
            return {
                "chain": [
                    {
                        "symbol": params.get("symbol", "SPY"),
                        "type": "C",
                        "dte": 30,
                        "strike": 500.0,
                        "bid": 1.0,
                        "ask": 1.2,
                    }
                ]
            }
        return {
            "symbol": params.get("symbol", "SPY"),
            "bid": 10.0,
            "ask": 10.2,
            "last": 10.1,
            "ts": 123,
        }

    monkeypatch.setattr(con, "_default_fetcher", fake_fetcher)

    prov = get_market_data_provider({})
    r = prov.get_quote(QuoteRequest(symbol="SPY"))
    assert r.ok and r.data and r.data.symbol == "SPY"

    op = get_options_provider({})
    cr = op.get_chain(OptionChainRequest(symbol="SPY"))
    assert cr.ok and cr.data and len(cr.data) == 1


def test_real_stub_rate_limit(monkeypatch):
    monkeypatch.setenv("PMCC_DATA_BACKEND", "real")
    monkeypatch.setenv("PMCC_REAL_STUB", "1")

    import pmcc.connectors as con
    from pmcc.throttle import TokenBucket

    def fake_fetcher(ep: str, params: dict):  # noqa: D401 - should not be called under rate limit
        raise AssertionError("fetcher should not be called under rate limit")

    class OneShotBucket(TokenBucket):
        def __init__(self) -> None:
            super().__init__(rate_per_sec=0.0, capacity=0.0, now=lambda: 0.0)

    monkeypatch.setattr(con, "_default_fetcher", fake_fetcher)

    def make_bucket(_cfgs):
        return OneShotBucket()

    monkeypatch.setattr(con, "_make_bucket", make_bucket)

    prov = get_market_data_provider({})
    r = prov.get_quote(QuoteRequest(symbol="SPY"))
    assert r.ok is False and r.error and r.error.code == PMCCErrorCode.RATE_LIMIT

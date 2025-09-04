from __future__ import annotations

from typing import Any, Dict, List

from pmcc.contracts import OptionChainRequest, PMCCErrorCode, QuoteRequest
from pmcc.real_readonly import RealReadonlyMarket, RealReadonlyOptions
from pmcc.throttle import TokenBucket


def _bucket_empty() -> TokenBucket:
    # capacity=0.0 & rate=0.0 → allow() always False
    return TokenBucket(rate_per_sec=0.0, capacity=0.0, now=lambda: 0.0)


def _bucket_full() -> TokenBucket:
    # high capacity & rate; now() fixed is fine since we won't drain >1 per call below
    return TokenBucket(rate_per_sec=100.0, capacity=100.0, now=lambda: 0.0)


def test_market_rate_limited_short_circuit():
    calls: List[int] = []

    def fetcher(_endpoint: str, _params: Dict[str, Any]) -> Dict[str, Any]:
        calls.append(1)
        return {}

    mkt = RealReadonlyMarket(fetcher=fetcher, endpoint="/q", bucket=_bucket_empty())
    r = mkt.get_quote(QuoteRequest(symbol="SPY"))
    assert r.ok is False
    assert r.error is not None and r.error.code == PMCCErrorCode.RATE_LIMIT
    # fetcher should not be called when rate-limited
    assert calls == []


def test_market_schema_error_and_network_error():
    # schema error: missing required fields
    def fetch_bad(_endpoint: str, _params: Dict[str, Any]) -> Dict[str, Any]:
        return {"symbol": "SPY", "bid": 1.0}  # missing ask/last/ts → KeyError

    mkt_bad = RealReadonlyMarket(fetcher=fetch_bad, endpoint="/q", bucket=_bucket_full())
    r1 = mkt_bad.get_quote(QuoteRequest(symbol="SPY"))
    assert r1.ok is False and r1.error is not None and r1.error.code == PMCCErrorCode.SCHEMA_ERROR

    # network error: exception bubbling returns NETWORK_ERROR
    def fetch_raises(_endpoint: str, _params: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("boom")

    mkt_err = RealReadonlyMarket(fetcher=fetch_raises, endpoint="/q", bucket=_bucket_full())
    r2 = mkt_err.get_quote(QuoteRequest(symbol="SPY"))
    assert r2.ok is False and r2.error is not None and r2.error.code == PMCCErrorCode.NETWORK_ERROR


def test_market_retry_then_success():
    calls = {"n": 0}

    def fetch_flaky(_endpoint: str, _params: Dict[str, Any]) -> Dict[str, Any]:
        calls["n"] += 1
        if calls["n"] <= 2:
            # simulate transient network failure
            raise RuntimeError("transient")
        return {"symbol": "SPY", "bid": 10.0, "ask": 10.2, "last": 10.1, "ts": 123}

    mkt = RealReadonlyMarket(fetcher=fetch_flaky, endpoint="/q", bucket=_bucket_full())
    r = mkt.get_quote(QuoteRequest(symbol="SPY"))
    assert r.ok is True and r.data is not None
    assert calls["n"] == 3  # 2 failures + 1 success


def test_options_chain_success_and_defaults():
    def fetch_chain(_endpoint: str, _params: Dict[str, Any]) -> Dict[str, Any]:
        # omit optional fields to exercise defaults
        return {
            "chain": [
                {"symbol": "SPY", "type": "C", "dte": 30, "strike": 500.0, "bid": 1.0, "ask": 1.2},
                {"symbol": "SPY", "type": "P", "dte": 365, "strike": 400.0, "bid": 5.0, "ask": 5.5},
            ]
        }

    opt = RealReadonlyOptions(fetcher=fetch_chain, endpoint="/opt", bucket=_bucket_full())
    r = opt.get_chain(OptionChainRequest(symbol="SPY"))
    assert r.ok is True and r.data is not None
    assert len(r.data) == 2
    # last should default to mid if missing
    mid0 = (1.0 + 1.2) / 2.0
    assert abs(r.data[0].last - mid0) < 1e-9


def test_options_rate_limited_and_schema_error():
    # rate-limited short circuit
    opt_rl = RealReadonlyOptions(fetcher=lambda *_a, **_k: {}, endpoint="/opt", bucket=_bucket_empty())
    r0 = opt_rl.get_chain(OptionChainRequest(symbol="SPY"))
    assert r0.ok is False and r0.error is not None and r0.error.code == PMCCErrorCode.RATE_LIMIT

    # schema error: missing required key (e.g., strike)
    def fetch_bad(_endpoint: str, _params: Dict[str, Any]) -> Dict[str, Any]:
        return {"chain": [{"symbol": "SPY", "type": "C", "dte": 30, "bid": 1.0, "ask": 1.1}]}

    opt_bad = RealReadonlyOptions(fetcher=fetch_bad, endpoint="/opt", bucket=_bucket_full())
    r1 = opt_bad.get_chain(OptionChainRequest(symbol="SPY"))
    assert r1.ok is False and r1.error is not None and r1.error.code == PMCCErrorCode.SCHEMA_ERROR


def test_options_network_error_bubbles():
    def fetch_raise(_endpoint: str, _params: Dict[str, Any]) -> Dict[str, Any]:
        raise RuntimeError("downstream")

    opt = RealReadonlyOptions(fetcher=fetch_raise, endpoint="/opt", bucket=_bucket_full())
    r = opt.get_chain(OptionChainRequest(symbol="SPY"))
    assert r.ok is False and r.error is not None and r.error.code == PMCCErrorCode.NETWORK_ERROR


def test_market_get_quotes_accumulates_and_bubbles_first_failure():
    def fetcher(_endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        sym = params.get("symbol")
        if sym == "BAD":
            return {"symbol": "BAD", "bid": 1.0}  # missing ask/last/ts → schema error path
        return {"symbol": sym, "bid": 10.0, "ask": 10.2, "last": 10.1, "ts": 123}

    mkt = RealReadonlyMarket(fetcher=fetcher, endpoint="/q", bucket=_bucket_full())
    # success path: two valid symbols
    ok = mkt.get_quotes(type("Req", (), {"symbols": ["SPY", "QQQ"]})())
    assert ok.ok is True and ok.data is not None and len(ok.data.quotes) == 2
    # failure bubbles out on first error
    bad = mkt.get_quotes(type("Req", (), {"symbols": ["SPY", "BAD", "QQQ"]})())
    assert bad.ok is False and bad.error is not None
    assert bad.error.code in (PMCCErrorCode.SCHEMA_ERROR, PMCCErrorCode.NETWORK_ERROR)

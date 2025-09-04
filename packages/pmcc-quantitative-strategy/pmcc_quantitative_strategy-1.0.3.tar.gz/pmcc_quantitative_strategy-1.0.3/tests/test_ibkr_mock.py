import time

import pytest

from pmcc.ibkr_mock import IBKRMarketDataMock


def test_quote_shape_cache_and_determinism():
    m = IBKRMarketDataMock(ttl_seconds=600)
    q1 = m.get_quote("AAPL")
    q2 = m.get_quote("AAPL")

    # shape
    assert set(q1) == {"symbol", "bid", "ask", "last", "volume", "ts"}
    assert q1["symbol"] == "AAPL"
    assert q1["ask"] >= q1["bid"] > 0
    assert q1["volume"] >= 0
    assert q1["bid"] <= q1["last"] <= q1["ask"]

    # cache: within TTL returns identical snapshot
    assert q1 == q2
    assert m._gen_counts.get(("quote", "AAPL"), 0) == 1  # noqa: SLF001

    # different symbol -> different snapshot
    q3 = m.get_quote("MSFT")
    assert q3 != q1


def test_ohlcv_shape_monotonic_cache():
    m = IBKRMarketDataMock(ttl_seconds=600)
    bars1 = m.get_ohlcv("AAPL", "1D", 20)
    bars2 = m.get_ohlcv("AAPL", "1D", 20)

    assert isinstance(bars1, list) and len(bars1) == 20
    last_ts = -1
    for b in bars1:
        assert set(b) == {"ts", "open", "high", "low", "close", "volume"}
        assert b["low"] <= b["open"] <= b["high"]
        assert b["low"] <= b["close"] <= b["high"]
        assert b["volume"] >= 0
        assert b["ts"] > last_ts
        last_ts = b["ts"]

    # deterministic + cached within TTL
    assert bars1 == bars2
    assert m._gen_counts.get(("ohlcv", "AAPL", "1D", 20), 0) == 1  # noqa: SLF001


@pytest.mark.slow
def test_ttl_expiry_quote_regenerates():
    m = IBKRMarketDataMock(ttl_seconds=1)
    q1 = m.get_quote("MSFT")
    time.sleep(1.1)
    q2 = m.get_quote("MSFT")

    # content differs due to new ts; price components deterministic
    assert q1 != q2
    assert q1["bid"] == q2["bid"]
    assert q1["ask"] == q2["ask"]
    assert q1["last"] == q2["last"]
    assert m._gen_counts.get(("quote", "MSFT"), 0) >= 2  # noqa: SLF001

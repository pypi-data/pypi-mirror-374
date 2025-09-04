from pmcc.data import MockMarketDataProvider


def test_get_ohlcv_basic_shape_and_order():
    p = MockMarketDataProvider(ttl_seconds=600)
    bars = p.get_ohlcv("AAPL", timeframe="1D", limit=20)
    assert isinstance(bars, list) and len(bars) == 20
    # fields and monotonic timestamps
    last_ts = -1
    for b in bars:
        assert set(b) == {"ts", "open", "high", "low", "close", "volume"}
        assert b["low"] <= b["open"] <= b["high"]
        assert b["low"] <= b["close"] <= b["high"]
        assert b["volume"] >= 0
        assert b["ts"] > last_ts
        last_ts = b["ts"]


def test_get_quote_is_cached_per_symbol():
    p = MockMarketDataProvider(ttl_seconds=600)
    q1 = p.get_quote("MSFT")
    q2 = p.get_quote("MSFT")
    assert q1 == q2
    # different symbol -> different deterministic snapshot
    q3 = p.get_quote("AAPL")
    assert q3 != q1


def test_get_ohlcv_cache_hit_counter():
    p = MockMarketDataProvider(ttl_seconds=600)
    _ = p.get_ohlcv("QQQ", "4H", 10)
    _ = p.get_ohlcv("QQQ", "4H", 10)
    # internal counter should record only one data generation for same key
    key = ("ohlcv", "QQQ", "4H", 10)
    assert p._gen_counts.get(key, 0) == 1  # noqa: SLF001

from __future__ import annotations

from pmcc.data import MockMarketDataProvider


def test_cache_expiry_triggers_regeneration(monkeypatch):
    # Control time() via monkeypatch to simulate TTL expiry without sleep
    t = {"now": 100.0}

    def fake_time():
        return t["now"]

    import pmcc.data as data_mod

    monkeypatch.setattr(data_mod, "time", fake_time)

    p = MockMarketDataProvider(ttl_seconds=10)
    key = ("ohlcv", "SPY", "1D", 3)

    # First generation at t=100
    bars1 = p.get_ohlcv("SPY", "1D", 3)
    assert p._gen_counts.get(key, 0) == 1  # noqa: SLF001

    # Within TTL -> cached
    t["now"] = 105.0
    bars2 = p.get_ohlcv("SPY", "1D", 3)
    assert bars2 == bars1
    assert p._gen_counts.get(key, 0) == 1  # noqa: SLF001

    # After TTL -> cache expired, should regenerate
    t["now"] = 200.0
    bars3 = p.get_ohlcv("SPY", "1D", 3)
    assert p._gen_counts.get(key, 0) == 2  # noqa: SLF001
    # New list object regenerated (content is deterministic but cache is refreshed)
    assert bars3 is not bars1

import pytest

from pmcc.data import MockMarketDataProvider
from pmcc.filters import filter_liquidity


def test_filter_liquidity_by_min_volume():
    p = MockMarketDataProvider()
    syms = ["AAPL", "MSFT", "SPY", "QQQ"]
    quotes = [p.get_quote(s) for s in syms]

    vols = [q["volume"] for q in quotes]
    threshold = min(vols) + 1  # ensure at least one drops

    res = filter_liquidity({"min_volume": threshold}, quotes)

    kept_syms = {q["symbol"] for q in res["kept"]}
    dropped_syms = {d["symbol"] for d in res["dropped"]}
    assert kept_syms.isdisjoint(dropped_syms)

    # Validate counts and volumes
    assert all(q["volume"] >= threshold for q in res["kept"])
    assert all(q["volume"] < threshold for q in res["dropped"])  # type: ignore[index]


def test_filter_liquidity_requires_min_volume_number():
    p = MockMarketDataProvider()
    quotes = [p.get_quote("AAPL")]
    with pytest.raises(ValueError):
        filter_liquidity({"min_volume": "bad"}, quotes)

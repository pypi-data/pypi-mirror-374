import pytest

from pmcc.data import MockMarketDataProvider
from pmcc.filters import filter_spread


def test_filter_spread_keep_and_drop_all_based_on_threshold():
    p = MockMarketDataProvider()
    syms = ["AAPL", "MSFT", "SPY", "QQQ"]
    quotes = [p.get_quote(s) for s in syms]

    # Typical mock spread ratio ≈ 0.002
    res_keep = filter_spread({"max_spread_ratio": 0.01}, quotes)
    assert len(res_keep["kept"]) == len(quotes)
    assert len(res_keep["dropped"]) == 0

    res_drop = filter_spread({"max_spread_ratio": 0.001}, quotes)
    assert len(res_drop["kept"]) == 0
    assert len(res_drop["dropped"]) == len(quotes)


def test_filter_spread_requires_max_spread_ratio_number():
    p = MockMarketDataProvider()
    quotes = [p.get_quote("AAPL")]
    with pytest.raises(ValueError):
        filter_spread({"max_spread_ratio": "tight"}, quotes)

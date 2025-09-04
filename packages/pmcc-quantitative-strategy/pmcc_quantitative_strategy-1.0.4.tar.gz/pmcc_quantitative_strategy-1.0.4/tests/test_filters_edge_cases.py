from pmcc.filters import filter_liquidity, filter_spread


def test_filter_liquidity_drops_non_numeric_volume():
    quotes = [
        {"symbol": "X", "volume": "n/a"},  # invalid
        {"symbol": "Y", "volume": 1000},  # valid
    ]
    res = filter_liquidity({"min_volume": 500}, quotes)
    kept_syms = {q["symbol"] for q in res["kept"]}
    dropped_syms = {q["symbol"] for q in res["dropped"]}
    assert "Y" in kept_syms
    assert "X" in dropped_syms


def test_filter_spread_drops_inverted_and_non_positive_quotes():
    quotes = [
        {"symbol": "A", "bid": 10.0, "ask": 9.9},  # inverted -> drop
        {"symbol": "B", "bid": 0.0, "ask": 1.0},  # non-positive bid -> drop
        {"symbol": "C", "bid": 1.0, "ask": 0.0},  # non-positive ask -> drop
        {"symbol": "D", "bid": 10.0, "ask": 10.2},  # valid
    ]
    res = filter_spread({"max_spread_ratio": 0.10}, quotes)
    kept = {q["symbol"] for q in res["kept"]}
    dropped = {q["symbol"] for q in res["dropped"]}
    assert kept == {"D"}
    assert dropped == {"A", "B", "C"}

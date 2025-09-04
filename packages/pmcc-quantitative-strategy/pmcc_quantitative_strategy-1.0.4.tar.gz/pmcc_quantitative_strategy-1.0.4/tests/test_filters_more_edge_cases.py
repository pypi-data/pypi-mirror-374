from pmcc.filters import filter_abnormal_quote, filter_spread


def test_filter_spread_drops_non_numeric_bid_or_ask():
    quotes = [
        {"symbol": "X", "bid": "n/a", "ask": 10.0},  # non-numeric -> drop
        {"symbol": "Y", "bid": 10.0, "ask": 10.5},  # valid
    ]
    res = filter_spread({"max_spread_ratio": 0.10}, quotes)
    kept = {q["symbol"] for q in res["kept"]}
    dropped = {q["symbol"] for q in res["dropped"]}
    assert "Y" in kept
    assert "X" in dropped


def test_filter_abnormal_drops_non_numeric_and_non_positive_last():
    quotes = [
        {"symbol": "A", "bid": 10.0, "ask": 10.2, "last": "x"},  # non-numeric last
        {"symbol": "B", "bid": 10.0, "ask": 10.2, "last": 0.0},  # non-positive last
        {"symbol": "C", "bid": 10.0, "ask": 10.2, "last": 10.1},  # valid
    ]
    res = filter_abnormal_quote({"max_last_mid_dev_ratio": 0.05}, quotes)
    kept = {q["symbol"] for q in res["kept"]}
    dropped = {q["symbol"] for q in res["dropped"]}
    assert "C" in kept
    assert {"A", "B"}.issubset(dropped)

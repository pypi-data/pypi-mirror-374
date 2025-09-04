from pmcc.strategy import (
    _annualized_yield,
    _mid,
    _select_leaps,
    _select_shorts,
    _spread_ratio,
    enumerate_pmcc_candidates,
)


def test_mid_and_spread_ratio_edge_cases():
    # _mid invalid types or non-positive should be 0
    assert _mid("x", 1.0) == 0.0
    assert _mid(1.0, -1.0) == 0.0
    assert _mid(0.0, 1.0) == 0.0
    # _spread_ratio returns large sentinel when mid<=0
    assert _spread_ratio("x", "y") > 1e8


def test_select_leaps_filters_by_type_dte_delta_mid():
    cfg = {"min_leaps_dte": 360, "leaps_delta_range": (0.6, 0.8)}
    chain = [
        {"symbol": "S", "type": "C", "dte": 400, "delta": 0.7, "bid": 10.0, "ask": 10.5},  # keep
        {"symbol": "S", "type": "P", "dte": 500, "delta": 0.7, "bid": 10.0, "ask": 10.5},  # wrong type
        {"symbol": "S", "type": "C", "dte": 300, "delta": 0.7, "bid": 10.0, "ask": 10.5},  # dte too low
        {"symbol": "S", "type": "C", "dte": 400, "delta": 0.9, "bid": 10.0, "ask": 10.5},  # delta out
        {"symbol": "S", "type": "C", "dte": 400, "delta": 0.7, "bid": 0.0, "ask": 1.0},  # mid <= 0
    ]
    res = _select_leaps(cfg, chain)
    assert len(res) == 1
    assert res[0]["dte"] == 400
    assert res[0]["delta"] == 0.7


def test_select_shorts_filters_by_window_delta_mid():
    cfg = {"target_short_dte": 30, "short_delta_range": (0.15, 0.35)}
    chain = [
        {"symbol": "S", "type": "C", "dte": 30, "delta": 0.25, "bid": 2.0, "ask": 2.2},  # keep
        {"symbol": "S", "type": "P", "dte": 30, "delta": 0.25, "bid": 2.0, "ask": 2.2},  # wrong type
        {"symbol": "S", "type": "C", "dte": 50, "delta": 0.25, "bid": 2.0, "ask": 2.2},  # dte above window
        {"symbol": "S", "type": "C", "dte": 10, "delta": 0.25, "bid": 2.0, "ask": 2.2},  # dte below window
        {"symbol": "S", "type": "C", "dte": 30, "delta": 0.05, "bid": 2.0, "ask": 2.2},  # delta too low
        {"symbol": "S", "type": "C", "dte": 30, "delta": 0.95, "bid": 2.0, "ask": 2.2},  # delta too high
        {"symbol": "S", "type": "C", "dte": 30, "delta": 0.25, "bid": 0.0, "ask": 1.0},  # mid <= 0
    ]
    res = _select_shorts(cfg, chain)
    assert len(res) == 1
    assert res[0]["dte"] == 30
    assert res[0]["delta"] == 0.25


def test_annualized_yield_basic_and_guards():
    # Valid annualized yield
    y = _annualized_yield(short_mid=2.0, under_price=100.0, dte=40)
    # 2/100 * 365/40 = 0.02 * 9.125 = 0.1825
    assert abs(y - 0.1825) < 1e-9
    # Guards
    assert _annualized_yield(0.0, 100.0, 30) == 0.0
    assert _annualized_yield(2.0, 0.0, 30) == 0.0
    assert _annualized_yield(2.0, 100.0, 0) == 0.0


def test_enumerate_pairs_only_same_symbol():
    cfg = {
        "min_leaps_dte": 360,
        "leaps_delta_range": (0.6, 0.8),
        "target_short_dte": 30,
        "short_delta_range": (0.15, 0.35),
    }
    quote = {"symbol": "S", "last": 100.0}
    chain = [
        # Eligible LEAPS for S
        {"symbol": "S", "type": "C", "dte": 400, "delta": 0.7, "bid": 10.0, "ask": 10.5},
        # Eligible SHORT for S
        {"symbol": "S", "type": "C", "dte": 30, "delta": 0.25, "bid": 2.0, "ask": 2.2},
        # Eligible SHORT but different symbol T → should not pair
        {"symbol": "T", "type": "C", "dte": 30, "delta": 0.25, "bid": 2.0, "ask": 2.2},
    ]
    pairs = enumerate_pmcc_candidates(cfg, chain, quote)
    assert len(pairs) == 1
    p = pairs[0]
    assert p["symbol"] == "S"
    assert p["leaps"]["symbol"] == "S"
    assert p["short"]["symbol"] == "S"

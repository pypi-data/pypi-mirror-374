import pytest

from pmcc.risk import check_position_limits


def test_position_limits_ok():
    limits = {"max_weight_per_underlying": 0.20, "max_positions": 2}
    positions = [
        {"ticker": "AAPL", "weight": 0.20},
        {"ticker": "MSFT", "weight": 0.10},
    ]
    r = check_position_limits(limits, positions)
    assert r["status"] == "ok"
    assert r["position_count"] == 2
    assert r["over_weight"] == []


def test_position_limits_over_weight_block():
    limits = {"max_weight_per_underlying": 0.20, "max_positions": 10}
    positions = [
        {"ticker": "AAPL", "weight": 0.25},
        {"ticker": "MSFT", "weight": 0.10},
    ]
    r = check_position_limits(limits, positions)
    assert r["status"] == "block"
    assert any(v["ticker"] == "AAPL" for v in r["over_weight"])  # contains offending ticker


def test_position_limits_count_block():
    limits = {"max_weight_per_underlying": 0.50, "max_positions": 2}
    positions = [
        {"ticker": "AAPL", "weight": 0.10},
        {"ticker": "MSFT", "weight": 0.10},
        {"ticker": "GOOGL", "weight": 0.10},
    ]
    r = check_position_limits(limits, positions)
    assert r["status"] == "block"
    assert r["position_count"] == 3


def test_position_limits_equal_threshold_ok():
    limits = {"max_weight_per_underlying": 0.30, "max_positions": 5}
    positions = [
        {"ticker": "TSLA", "weight": 0.30},  # exactly at threshold
    ]
    r = check_position_limits(limits, positions)
    assert r["status"] == "ok"
    assert r["over_weight"] == []


def test_position_limits_invalid_config_max_weight_non_number():
    limits = {"max_weight_per_underlying": "0.2", "max_positions": 5}
    with pytest.raises(ValueError):
        check_position_limits(limits, positions=[])


def test_position_limits_invalid_config_max_positions_not_int():
    limits = {"max_weight_per_underlying": 0.2, "max_positions": 2.0}
    with pytest.raises(ValueError):
        check_position_limits(limits, positions=[])


def test_position_limits_invalid_position_missing_ticker():
    limits = {"max_weight_per_underlying": 0.2, "max_positions": 5}
    positions = [
        {"weight": 0.1},  # missing ticker
    ]
    with pytest.raises(ValueError):
        check_position_limits(limits, positions)


def test_position_limits_invalid_position_weight_non_number():
    limits = {"max_weight_per_underlying": 0.2, "max_positions": 5}
    positions = [
        {"ticker": "AAPL", "weight": "0.1"},  # weight not number
    ]
    with pytest.raises(ValueError):
        check_position_limits(limits, positions)

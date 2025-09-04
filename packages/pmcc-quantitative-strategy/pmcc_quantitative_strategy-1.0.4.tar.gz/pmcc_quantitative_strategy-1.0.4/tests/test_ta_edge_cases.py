import pytest

from pmcc.ta import _divergence_strength, ema, macd, rsi


def test_ema_invalid_length_raises():
    with pytest.raises(ValueError):
        ema([1, 2, 3], 0)
    with pytest.raises(ValueError):
        ema([1, 2, 3], -5)


def test_rsi_invalid_length_raises():
    with pytest.raises(ValueError):
        rsi([1, 2, 3], 0)


def test_macd_invalid_periods_nonpositive():
    with pytest.raises(ValueError):
        macd([1, 2, 3], 0, 26, 9)
    with pytest.raises(ValueError):
        macd([1, 2, 3], 12, -26, 9)
    with pytest.raises(ValueError):
        macd([1, 2, 3], 12, 26, 0)


def test_macd_fast_not_less_than_slow_raises():
    with pytest.raises(ValueError):
        macd([1, 2, 3], 26, 12, 9)
    with pytest.raises(ValueError):
        macd([1, 2, 3], 12, 12, 9)


def test__divergence_strength_bottom_divergence_branch():
    bars = [
        {"close": 10.0},
        {"close": 8.0},
        {"close": 9.0},
        {"close": 7.0},
        {"close": 8.0},
        {"close": 9.0},
    ]
    rsi_vals = [50.0, 40.0, 45.0, 60.0, 55.0, 50.0]
    macd_hist: list[float] = []
    cfg = {
        "rsi": {
            "pivot_left": 1,
            "pivot_right": 1,
            "min_strength": 0.1,
        }
    }

    s = _divergence_strength(bars, rsi_vals, macd_hist, cfg)
    assert 0.1 < s <= 1.0

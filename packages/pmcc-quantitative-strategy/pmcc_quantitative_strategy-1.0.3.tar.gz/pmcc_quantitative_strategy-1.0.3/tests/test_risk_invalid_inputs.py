import pytest

from pmcc.risk import (
    check_assignment_dividend,
    check_correlation_control,
    check_drawdown_guard,
    check_position_limits,
)


def test_position_limits_invalid_config_should_raise():
    with pytest.raises(ValueError):
        check_position_limits({"max_weight_per_underlying": "x", "max_positions": 10}, [])
    with pytest.raises(ValueError):
        check_position_limits({"max_weight_per_underlying": 0.2, "max_positions": "10"}, [])


def test_position_limits_invalid_item_should_raise():
    with pytest.raises(ValueError):
        check_position_limits(
            {"max_weight_per_underlying": 0.2, "max_positions": 5},
            [{"ticker": 123, "weight": 0.1}],
        )
    with pytest.raises(ValueError):
        check_position_limits(
            {"max_weight_per_underlying": 0.2, "max_positions": 5},
            [{"ticker": "AAPL", "weight": "bad"}],
        )


def test_correlation_control_invalid_threshold_should_raise():
    with pytest.raises(ValueError):
        check_correlation_control({"max_pairwise": "x"}, positions=[], pairwise_corr=[])


def test_correlation_control_invalid_pair_tuple_should_raise():
    with pytest.raises(ValueError):
        check_correlation_control({"max_pairwise": 0.9}, positions=[], pairwise_corr=[(1, "B", 0.3)])
    with pytest.raises(ValueError):
        check_correlation_control({"max_pairwise": 0.9}, positions=[], pairwise_corr=[("A", "B", "0.3")])


def test_drawdown_guard_invalid_config_should_raise():
    with pytest.raises(ValueError):
        check_drawdown_guard({"threshold": "x", "action": "reduce"}, current_drawdown=0.1)
    with pytest.raises(ValueError):
        check_drawdown_guard({"threshold": 0.2, "action": 123}, current_drawdown=0.1)


def test_assignment_dividend_invalid_min_diff_should_raise():
    with pytest.raises(ValueError):
        check_assignment_dividend({"ex_div_protection": True, "min_extrinsic_vs_dividend": "x"}, [])


def test_assignment_dividend_invalid_candidate_fields_should_raise():
    cfg = {"ex_div_protection": True, "min_extrinsic_vs_dividend": 0.0}
    # ticker not str
    with pytest.raises(ValueError):
        check_assignment_dividend(
            cfg,
            [
                {
                    "ticker": 123,
                    "extrinsic": 0.1,
                    "dividend": 0.05,
                    "is_short_call": True,
                }
            ],
        )
    # extrinsic not number
    with pytest.raises(ValueError):
        check_assignment_dividend(
            cfg,
            [
                {
                    "ticker": "AAPL",
                    "extrinsic": "bad",
                    "dividend": 0.05,
                    "is_short_call": True,
                }
            ],
        )
    # dividend not number
    with pytest.raises(ValueError):
        check_assignment_dividend(
            cfg,
            [
                {
                    "ticker": "AAPL",
                    "extrinsic": 0.1,
                    "dividend": "bad",
                    "is_short_call": True,
                }
            ],
        )

import pytest

from pmcc.risk import check_correlation_control


def test_correlation_ok_at_or_below_threshold():
    ctrl = {"max_pairwise": 0.50}
    positions = []  # not used in current implementation
    pairwise = [
        ("AAPL", "MSFT", 0.50),
        ("AAPL", "GOOGL", 0.10),
    ]
    r = check_correlation_control(ctrl, positions, pairwise)
    assert r["status"] == "ok"
    assert r["violations"] == []


def test_correlation_warn_when_above_threshold():
    ctrl = {"max_pairwise": 0.50}
    positions = []
    pairwise = [
        ("AAPL", "MSFT", 0.49),
        ("AAPL", "GOOGL", 0.51),  # violation
    ]
    r = check_correlation_control(ctrl, positions, pairwise)
    assert r["status"] == "warn"
    assert any(v["pair"] == ("AAPL", "GOOGL") for v in r["violations"])  # contains the offending pair


def test_correlation_empty_pairs_ok():
    ctrl = {"max_pairwise": 0.30}
    r = check_correlation_control(ctrl, positions=[], pairwise_corr=[])
    assert r["status"] == "ok"
    assert r["violations"] == []


def test_correlation_invalid_threshold_raises():
    ctrl = {"max_pairwise": "0.5"}
    with pytest.raises(ValueError):
        check_correlation_control(ctrl, positions=[], pairwise_corr=[])


def test_correlation_invalid_pair_tuple_types_raises():
    ctrl = {"max_pairwise": 0.5}
    with pytest.raises(ValueError):
        check_correlation_control(ctrl, positions=[], pairwise_corr=[("AAPL", 123, 0.2)])
    with pytest.raises(ValueError):
        check_correlation_control(ctrl, positions=[], pairwise_corr=[("AAPL", "MSFT", "0.2")])

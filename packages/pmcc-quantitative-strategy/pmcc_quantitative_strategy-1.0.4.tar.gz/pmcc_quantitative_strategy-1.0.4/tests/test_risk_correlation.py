from pmcc.risk import check_correlation_control


def positions():
    return [
        {"ticker": "AAPL", "weight": 0.10},
        {"ticker": "MSFT", "weight": 0.15},
        {"ticker": "GOOGL", "weight": 0.05},
    ]


def test_correlation_ok_when_all_below_threshold():
    ctrl = {"max_pairwise": 0.80, "penalty_weight": 0.50}
    corr_pairs = [
        ("AAPL", "MSFT", 0.70),
        ("AAPL", "GOOGL", 0.60),
        ("MSFT", "GOOGL", 0.75),
    ]
    r = check_correlation_control(ctrl, positions(), corr_pairs)
    assert r["status"] == "ok"
    assert r["violations"] == []


def test_correlation_warn_when_any_exceeds_threshold():
    ctrl = {"max_pairwise": 0.80, "penalty_weight": 0.50}
    corr_pairs = [
        ("AAPL", "MSFT", 0.85),  # exceeds
        ("AAPL", "GOOGL", 0.60),
    ]
    r = check_correlation_control(ctrl, positions(), corr_pairs)
    assert r["status"] == "warn"
    assert any(v["pair"] == ("AAPL", "MSFT") for v in r["violations"])  # flagged

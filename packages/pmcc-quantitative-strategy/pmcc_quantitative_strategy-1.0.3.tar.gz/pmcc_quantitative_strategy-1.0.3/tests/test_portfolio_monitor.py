from __future__ import annotations

from pmcc.portfolio import monitor_portfolio


def test_monitor_detects_overweights_and_high_correlation():
    risk_limits = {"max_weight_per_underlying": 0.30, "max_positions": 5}
    correlation_ctrl = {"max_pairwise": 0.80}

    positions = [
        {"ticker": "AAPL", "weight": 0.35},
        {"ticker": "MSFT", "weight": 0.32},
        {"ticker": "TSLA", "weight": 0.10},
    ]
    pairwise_corr = [
        ("AAPL", "MSFT", 0.85),  # above threshold
        ("AAPL", "TSLA", 0.20),
        ("MSFT", "TSLA", 0.25),
    ]

    r = monitor_portfolio(
        risk_limits=risk_limits,
        correlation_ctrl=correlation_ctrl,
        positions=positions,
        pairwise_corr=pairwise_corr,
    )

    assert r["status"] == "warn"

    actions = r["actions"]
    # Two reduce_weight actions for AAPL and MSFT
    reduce_map = {a["ticker"]: a for a in actions if a["action"] == "reduce_weight"}
    assert reduce_map["AAPL"]["target_weight"] == risk_limits["max_weight_per_underlying"]
    assert reduce_map["MSFT"]["target_weight"] == risk_limits["max_weight_per_underlying"]

    # One correlation review action for the pair (AAPL, MSFT)
    corr_pairs = [tuple(a["pair"]) for a in actions if a["action"] == "review_corr_pair"]
    assert ("AAPL", "MSFT") in corr_pairs or ("MSFT", "AAPL") in corr_pairs


def test_monitor_rebalance_when_underweight_total():
    risk_limits = {"max_weight_per_underlying": 0.50, "max_positions": 10, "min_total_weight": 0.95}
    correlation_ctrl = {"max_pairwise": 0.80}

    # Total weight 0.60 < 0.95 threshold, no overweight or high-corr
    positions = [
        {"ticker": "A", "weight": 0.30},
        {"ticker": "B", "weight": 0.30},
    ]
    pairwise_corr = [("A", "B", 0.10)]

    r = monitor_portfolio(
        risk_limits=risk_limits,
        correlation_ctrl=correlation_ctrl,
        positions=positions,
        pairwise_corr=pairwise_corr,
    )

    assert r["status"] == "warn"
    actions = r["actions"]
    kinds = {a["action"] for a in actions}
    assert "rebalance_underweight" in kinds
    # Should not include reduce_weight actions or corr review here
    assert all(a["action"] != "reduce_weight" for a in actions)

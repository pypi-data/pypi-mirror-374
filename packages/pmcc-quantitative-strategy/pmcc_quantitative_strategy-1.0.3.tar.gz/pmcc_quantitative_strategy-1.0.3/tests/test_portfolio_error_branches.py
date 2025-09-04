from __future__ import annotations

from pmcc.portfolio import optimize_portfolio_greedy, propose_allocation_risk_balanced


def test_risk_balanced_invalid_capital():
    candidates = [{"symbol": "A", "score": 1.0, "risk": 0.2}]
    risk_limits = {"max_weight_per_underlying": 0.5, "max_positions": 2}

    r = propose_allocation_risk_balanced(cfg={}, candidates=candidates, capital=0.0, risk_limits=risk_limits)
    assert r["status"] == "block" and r["reason"] == "invalid_capital"


def test_risk_balanced_invalid_risk_limits():
    candidates = [{"symbol": "A", "score": 1.0, "risk": 0.2}]

    r1 = propose_allocation_risk_balanced(
        cfg={},
        candidates=candidates,
        capital=1000.0,
        risk_limits={"max_weight_per_underlying": 0.5, "max_positions": "x"},
    )
    assert r1["status"] == "block" and r1["reason"] == "invalid_risk_limits"

    r2 = propose_allocation_risk_balanced(
        cfg={},
        candidates=candidates,
        capital=1000.0,
        risk_limits={"max_weight_per_underlying": "x", "max_positions": 2},
    )
    assert r2["status"] == "block" and r2["reason"] == "invalid_risk_limits"


def test_risk_balanced_no_candidates():
    # Missing/invalid risk or score should lead to no_candidates
    candidates = [
        {"symbol": "A", "score": 1.0},
        {"symbol": "B", "risk": 0.3},
        {"symbol": "C", "score": "bad", "risk": "bad"},
    ]
    risk_limits = {"max_weight_per_underlying": 0.5, "max_positions": 2}

    r = propose_allocation_risk_balanced(cfg={}, candidates=candidates, capital=1000.0, risk_limits=risk_limits)
    assert r["status"] == "block" and r["reason"] == "no_candidates"


def test_optimize_invalid_capital():
    candidates = [{"symbol": "A", "score": 1.0, "risk": 0.2}]

    r = optimize_portfolio_greedy(
        cfg={},
        candidates=candidates,
        pairwise_corr=[],
        capital=-1.0,
        risk_limits={"max_weight_per_underlying": 0.5, "max_positions": 2},
    )
    assert r["status"] == "block" and r["reason"] == "invalid_capital"


def test_optimize_invalid_risk_limits():
    candidates = [{"symbol": "A", "score": 1.0, "risk": 0.2}]

    r1 = optimize_portfolio_greedy(
        cfg={},
        candidates=candidates,
        pairwise_corr=[],
        capital=1000.0,
        risk_limits={"max_weight_per_underlying": 0.5, "max_positions": "x"},
    )
    assert r1["status"] == "block" and r1["reason"] == "invalid_risk_limits"

    r2 = optimize_portfolio_greedy(
        cfg={},
        candidates=candidates,
        pairwise_corr=[],
        capital=1000.0,
        risk_limits={"max_weight_per_underlying": "x", "max_positions": 2},
    )
    assert r2["status"] == "block" and r2["reason"] == "invalid_risk_limits"


def test_optimize_no_candidates():
    candidates = [
        {"symbol": "A", "score": "bad", "risk": 0.2},
        {"symbol": "B", "score": 1.0, "risk": "bad"},
    ]

    r = optimize_portfolio_greedy(
        cfg={},
        candidates=candidates,
        pairwise_corr=[],
        capital=1000.0,
        risk_limits={"max_weight_per_underlying": 0.5, "max_positions": 3},
    )
    assert r["status"] == "block" and r["reason"] == "no_candidates"

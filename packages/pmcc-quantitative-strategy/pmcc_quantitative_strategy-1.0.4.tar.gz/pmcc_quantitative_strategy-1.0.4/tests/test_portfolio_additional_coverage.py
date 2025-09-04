from __future__ import annotations

from pmcc.portfolio import propose_allocation_risk_balanced


def test_risk_balanced_equal_weight_fallback_on_negative_sum():
    # Configure epsilon negative and risks negative so that bases sum <= 0,
    # forcing equal-weight fallback branch.
    candidates = [
        {"symbol": "A", "score": 1.0, "risk": -0.10},
        {"symbol": "B", "score": 0.9, "risk": -0.20},
    ]
    cfg = {"epsilon": -1.0}
    risk_limits = {"max_weight_per_underlying": 0.60, "max_positions": 2}

    r = propose_allocation_risk_balanced(cfg=cfg, candidates=candidates, capital=1000.0, risk_limits=risk_limits)
    assert r["status"] == "ok"
    weights = {p["ticker"]: p["weight"] for p in r["proposal"]}
    # Equal weight 0.5 each
    assert abs(weights["A"] - 0.5) < 1e-9
    assert abs(weights["B"] - 0.5) < 1e-9


def test_risk_balanced_redistribute_break_when_no_eligible():
    # Both names capped, leftover remains, and no eligible receivers -> break path covered
    candidates = [
        {"symbol": "X", "score": 2.0, "risk": 0.05},
        {"symbol": "Y", "score": 1.9, "risk": 0.06},
    ]
    cfg = {"redistribute_leftover": True}
    # Cap low to ensure both are capped
    risk_limits = {"max_weight_per_underlying": 0.30, "max_positions": 2}

    r = propose_allocation_risk_balanced(cfg=cfg, candidates=candidates, capital=100_000.0, risk_limits=risk_limits)
    assert r["status"] == "ok"
    weights = [p["weight"] for p in r["proposal"]]
    # Both exactly at cap; sum < 1.0, leftover not redistributed due to no eligible
    assert all(abs(w - 0.30) < 1e-9 for w in weights)
    assert sum(weights) < 1.0 - 1e-6


def test_risk_balanced_tiny_leftover_no_progress_breaks_loop():
    # Three names where one slightly exceeds cap producing a tiny leftover < eps_w,
    # and others have headroom but added share < eps_w so no progress occurs.
    # This hits the `not progressed` early break branch.
    candidates = [
        {"symbol": "A", "score": 2.0, "risk": 1.0 / 0.3400000000001},
        {"symbol": "B", "score": 2.0, "risk": 1.0 / 0.33},
        {"symbol": "C", "score": 2.0, "risk": 1.0 / 0.33},
    ]
    capital = 100_000.0
    risk_limits = {"max_weight_per_underlying": 0.34, "max_positions": 3}

    r = propose_allocation_risk_balanced(
        cfg={"redistribute_leftover": True},
        candidates=candidates,
        capital=capital,
        risk_limits=risk_limits,
    )
    assert r["status"] == "ok"
    prop = r["proposal"]
    weights = {p["ticker"]: p["weight"] for p in prop}
    # A should be exactly at cap; B/C should remain ~0.33 (no increase due to tiny leftover)
    assert abs(weights["A"] - 0.34) < 1e-12
    assert abs(weights["B"] - 0.33) < 1e-12
    assert abs(weights["C"] - 0.33) < 1e-12
    # Sum slightly below 1.0 due to tiny leftover and no progress
    total = sum(weights.values())
    assert 1.0 - 1e-12 < total < 1.0

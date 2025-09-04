from __future__ import annotations

import math
from typing import TypedDict

from pmcc.portfolio import propose_allocation_risk_balanced


class Cand(TypedDict, total=False):
    symbol: str
    score: float
    risk: float


def test_risk_balanced_alloc_prefers_lower_risk_among_top_by_score():
    candidates: list[Cand] = [
        {"symbol": "A", "score": 1.00, "risk": 0.20},
        {"symbol": "B", "score": 1.20, "risk": 0.50},  # top score
        {"symbol": "C", "score": 1.10, "risk": 0.30},  # second score
    ]
    capital = 100_000.0
    risk_limits = {"max_weight_per_underlying": 0.70, "max_positions": 2}

    r = propose_allocation_risk_balanced(cfg={}, candidates=candidates, capital=capital, risk_limits=risk_limits)

    assert r["status"] == "ok"
    proposal = r["proposal"]
    # Top-2 by score should be B and C (A is third by score)
    tickers = [p["ticker"] for p in proposal]
    assert tickers == ["B", "C"]

    # Within top-2, lower risk (C:0.30) should receive higher weight than higher risk (B:0.50)
    wb = next(p["weight"] for p in proposal if p["ticker"] == "B")
    wc = next(p["weight"] for p in proposal if p["ticker"] == "C")
    assert wc > wb

    # Capital allocation consistent with weights
    for p in proposal:
        assert math.isclose(
            p["allocated_capital"],
            p["weight"] * capital,
            rel_tol=1e-12,
            abs_tol=1e-9,
        )


def test_risk_balanced_alloc_respects_per_name_cap_and_weight_sum():
    candidates: list[Cand] = [
        {"symbol": "X", "score": 2.0, "risk": 0.05},  # very low risk, would dominate without cap
        {"symbol": "Y", "score": 1.9, "risk": 0.50},
        {"symbol": "Z", "score": 1.8, "risk": 0.60},
    ]
    capital = 50_000.0
    risk_limits = {"max_weight_per_underlying": 0.40, "max_positions": 2}

    r = propose_allocation_risk_balanced(cfg={}, candidates=candidates, capital=capital, risk_limits=risk_limits)

    assert r["status"] == "ok"
    proposal = r["proposal"]
    # Top-2 by score are X and Y
    assert [p["ticker"] for p in proposal] == ["X", "Y"]

    # Each weight should be <= cap
    for p in proposal:
        assert p["weight"] <= risk_limits["max_weight_per_underlying"] + 1e-9

    # Weight sum should not exceed 1.0 (leftover is acceptable, no redistribution required)
    total_w = sum(p["weight"] for p in proposal)
    assert 0.0 < total_w <= 1.0 + 1e-9


def test_risk_balanced_redistribute_leftover_when_enabled():
    # X has extremely low risk and would be capped; ensure leftover is redistributed when flag enabled
    candidates: list[Cand] = [
        {"symbol": "X", "score": 2.0, "risk": 0.05},
        {"symbol": "Y", "score": 1.9, "risk": 0.50},
    ]
    capital = 100_000.0
    risk_limits = {"max_weight_per_underlying": 0.70, "max_positions": 2}

    # Without redistribution (default): X capped at 0.70, Y remains at raw ~0.0909; sum < 1
    r_no = propose_allocation_risk_balanced(cfg={}, candidates=candidates, capital=capital, risk_limits=risk_limits)
    assert r_no["status"] == "ok"
    prop_no = r_no["proposal"]
    wx_no = next(p["weight"] for p in prop_no if p["ticker"] == "X")
    wy_no = next(p["weight"] for p in prop_no if p["ticker"] == "Y")
    assert abs(wx_no - 0.70) < 1e-9
    assert abs(wy_no - (2.0 / (20.0 + 2.0))) < 1e-9  # 1/r normalized = 2 / (20+2)
    assert sum(p["weight"] for p in prop_no) < 1.0 - 1e-6

    # With redistribution: leftover goes to Y (within cap), making total close to 1
    r_yes = propose_allocation_risk_balanced(
        cfg={"redistribute_leftover": True},
        candidates=candidates,
        capital=capital,
        risk_limits=risk_limits,
    )
    assert r_yes["status"] == "ok"
    prop_yes = r_yes["proposal"]
    wx_yes = next(p["weight"] for p in prop_yes if p["ticker"] == "X")
    wy_yes = next(p["weight"] for p in prop_yes if p["ticker"] == "Y")
    assert abs(wx_yes - 0.70) < 1e-9
    assert abs(wy_yes - 0.30) < 1e-6
    assert abs(sum(p["weight"] for p in prop_yes) - 1.0) < 1e-6

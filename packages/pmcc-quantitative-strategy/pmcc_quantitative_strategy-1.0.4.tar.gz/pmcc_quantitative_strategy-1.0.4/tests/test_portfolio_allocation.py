from __future__ import annotations

from typing import TypedDict

from pmcc.portfolio import propose_allocation


class Cand(TypedDict):
    symbol: str
    score: float


def test_equal_weight_allocation_respects_limits():
    candidates: list[Cand] = [
        {"symbol": "AAPL", "score": 1.5},
        {"symbol": "MSFT", "score": 1.4},
        {"symbol": "TSLA", "score": 1.3},
        {"symbol": "GOOGL", "score": 1.2},
    ]
    capital = 100_000.0
    risk_limits = {"max_weight_per_underlying": 0.30, "max_positions": 3}

    r = propose_allocation(cfg={}, candidates=candidates, capital=capital, risk_limits=risk_limits)

    assert r["status"] == "ok"
    proposal = r["proposal"]
    # Select top 3 by score
    assert [p["ticker"] for p in proposal] == ["AAPL", "MSFT", "TSLA"]
    # Each weight <= 0.30 and approximately equal (equal=1/3=0.333..., clipped to 0.30)
    for p in proposal:
        assert p["weight"] <= risk_limits["max_weight_per_underlying"] + 1e-9
    # Allocated capital respects total
    total_alloc = sum(p["allocated_capital"] for p in proposal)
    assert total_alloc <= capital + 1e-6
    # Weights sum is clipped to <= 1.0
    total_weight = sum(p["weight"] for p in proposal)
    assert 0.0 < total_weight <= 1.0 + 1e-9

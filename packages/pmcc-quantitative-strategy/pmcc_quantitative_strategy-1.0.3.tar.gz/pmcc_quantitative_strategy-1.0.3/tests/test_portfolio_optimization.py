from __future__ import annotations

from typing import TypedDict

from pmcc.portfolio import optimize_portfolio_greedy


class Cand(TypedDict, total=False):
    symbol: str
    score: float
    risk: float


def test_optimize_prefers_low_risk_and_low_corr():
    candidates: list[Cand] = [
        {"symbol": "A", "score": 1.00, "risk": 0.50},
        {"symbol": "B", "score": 1.00, "risk": 0.90},  # higher risk
        {"symbol": "C", "score": 0.95, "risk": 0.40},  # slightly lower score, low risk
    ]
    pairwise_corr = [
        ("A", "B", 0.90),
        ("A", "C", 0.20),
        ("B", "C", 0.80),
    ]
    risk_limits = {"max_weight_per_underlying": 0.50, "max_positions": 2}
    cfg = {"risk_aversion": 0.5, "corr_penalty": 0.5}

    r = optimize_portfolio_greedy(
        cfg=cfg,
        candidates=candidates,
        pairwise_corr=pairwise_corr,
        capital=100_000.0,
        risk_limits=risk_limits,
    )

    assert r["status"] == "ok"
    proposal = r["proposal"]
    # avoid selecting A and B together due to high correlation; prefer A and C
    assert [p["ticker"] for p in proposal] == ["A", "C"]
    # weights within cap, equal weight when two positions
    for p in proposal:
        assert p["weight"] <= risk_limits["max_weight_per_underlying"] + 1e-9
        assert abs(p["weight"] - 0.5) < 1e-9


def test_optimize_corr_penalty_zero_ignores_correlation():
    candidates: list[Cand] = [
        {"symbol": "A", "score": 1.00, "risk": 0.50},
        {"symbol": "B", "score": 1.00, "risk": 0.50},
        {"symbol": "C", "score": 0.90, "risk": 0.50},
    ]
    pairwise_corr = [
        ("A", "B", 0.99),  # very high, should be ignored when corr_penalty=0
        ("A", "C", 0.00),
        ("B", "C", 0.00),
    ]
    risk_limits = {"max_weight_per_underlying": 0.60, "max_positions": 2}
    cfg = {"risk_aversion": 0.0, "corr_penalty": 0.0}

    r = optimize_portfolio_greedy(
        cfg=cfg,
        candidates=candidates,
        pairwise_corr=pairwise_corr,
        capital=100_000.0,
        risk_limits=risk_limits,
    )

    assert r["status"] == "ok"
    proposal = r["proposal"]
    # Highest two scores A and B selected despite high correlation
    assert [p["ticker"] for p in proposal] == ["A", "B"]
    for p in proposal:
        assert abs(p["weight"] - 0.5) < 1e-9


def test_optimize_corr_penalty_huge_avoids_high_corr_pairs():
    candidates: list[Cand] = [
        {"symbol": "A", "score": 1.00, "risk": 0.50},
        {"symbol": "B", "score": 1.00, "risk": 0.50},
        {"symbol": "C", "score": 1.00, "risk": 0.50},
    ]
    pairwise_corr = [
        ("A", "B", 0.99),  # avoid pairing A with B
        ("A", "C", 0.00),
        ("B", "C", 0.00),
    ]
    risk_limits = {"max_weight_per_underlying": 0.60, "max_positions": 2}
    cfg = {"risk_aversion": 0.0, "corr_penalty": 1e6}

    r = optimize_portfolio_greedy(
        cfg=cfg,
        candidates=candidates,
        pairwise_corr=pairwise_corr,
        capital=100_000.0,
        risk_limits=risk_limits,
    )

    assert r["status"] == "ok"
    proposal = r["proposal"]
    # Choose A and C (avoid A-B high correlation)
    assert [p["ticker"] for p in proposal] == ["A", "C"]


def test_optimize_risk_aversion_huge_prefers_low_risk():
    candidates: list[Cand] = [
        {"symbol": "A", "score": 1.00, "risk": 0.50},
        {"symbol": "B", "score": 0.95, "risk": 0.10},
        {"symbol": "C", "score": 0.94, "risk": 0.05},
    ]
    pairwise_corr = [("A", "B", 0.10), ("A", "C", 0.10), ("B", "C", 0.10)]
    risk_limits = {"max_weight_per_underlying": 0.60, "max_positions": 2}
    cfg = {"risk_aversion": 1e6, "corr_penalty": 0.0}

    r = optimize_portfolio_greedy(
        cfg=cfg,
        candidates=candidates,
        pairwise_corr=pairwise_corr,
        capital=100_000.0,
        risk_limits=risk_limits,
    )

    assert r["status"] == "ok"
    proposal = r["proposal"]
    assert {p["ticker"] for p in proposal} == {"B", "C"}

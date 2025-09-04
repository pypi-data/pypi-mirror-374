from pmcc.portfolio import monitor_portfolio, propose_allocation


def test_propose_allocation_invalid_inputs():
    cfg = {}
    candidates = [{"symbol": "A", "score": 1.0}]
    risk_limits = {"max_weight_per_underlying": 0.5, "max_positions": 5}

    # invalid capital
    r = propose_allocation(cfg, candidates, capital=0.0, risk_limits=risk_limits)
    assert r["status"] == "block" and r["reason"] == "invalid_capital"

    # invalid risk limits (max_positions not int)
    bad_limits = {"max_weight_per_underlying": 0.5, "max_positions": "x"}
    r2 = propose_allocation(cfg, candidates, capital=1000.0, risk_limits=bad_limits)
    assert r2["status"] == "block" and r2["reason"] == "invalid_risk_limits"

    # no valid candidates
    bad_cands = [{"symbol": "A"}]  # missing score
    r3 = propose_allocation(cfg, bad_cands, capital=1000.0, risk_limits=risk_limits)
    assert r3["status"] == "block" and r3["reason"] == "no_candidates"


def test_monitor_portfolio_invalid_risk_limits_blocks():
    risk_limits = {"max_weight_per_underlying": "NaN"}  # not a number
    correlation_ctrl = {"max_pairwise": 0.8}
    positions = [{"ticker": "X", "weight": 0.6}]
    pairwise_corr = [("X", "Y", 0.9)]

    r = monitor_portfolio(
        risk_limits=risk_limits,
        correlation_ctrl=correlation_ctrl,
        positions=positions,
        pairwise_corr=pairwise_corr,
    )
    assert r["status"] == "block" and r["reason"] == "invalid_risk_limits"


def test_propose_allocation_invalid_max_weight_type():
    cfg = {}
    candidates = [{"symbol": "A", "score": 1.0}]
    # invalid max_weight_per_underlying
    bad_limits = {"max_weight_per_underlying": "x", "max_positions": 2}
    r = propose_allocation(cfg, candidates, capital=1000.0, risk_limits=bad_limits)
    assert r["status"] == "block" and r["reason"] == "invalid_risk_limits"

from pmcc.risk import check_drawdown_guard


def test_drawdown_ok_when_below_threshold():
    guard = {"threshold": 0.10, "action": "reduce"}
    r = check_drawdown_guard(guard, current_drawdown=0.05)
    assert r["status"] == "ok"
    assert r["threshold"] == 0.10


def test_drawdown_warn_when_at_or_above_threshold():
    guard = {"threshold": 0.10, "action": "reduce"}
    r = check_drawdown_guard(guard, current_drawdown=0.10)
    assert r["status"] == "warn"
    assert r["action"] == "reduce"

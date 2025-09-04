import logging

from pmcc.risk import dry_run


def base_cfg():
    return {
        "risk_policy.json": {
            "cushion": {"hard_floor": 0.1, "target_range": [0.2, 0.3]},
            "position_limits": {"max_weight_per_underlying": 0.5, "max_positions": 5},
            "correlation_control": {"max_pairwise": 0.9},
            "drawdown_guard": {"threshold": 0.5, "action": "reduce"},
            "assignment_dividend": {"ex_div_protection": False, "min_extrinsic_vs_dividend": 0.0},
        }
    }


def test_dry_run_logs_error_position_limits(caplog):
    cfg = base_cfg()
    cfg["risk_policy.json"]["position_limits"] = {
        "max_weight_per_underlying": "bad",
        "max_positions": 2.0,
    }
    caplog.set_level(logging.ERROR, logger="pmcc.risk")
    dry_run(cfg)
    assert any("持仓上限规则检查异常" in rec.message for rec in caplog.records)


def test_dry_run_logs_error_correlation_control(caplog):
    cfg = base_cfg()
    cfg["risk_policy.json"]["correlation_control"] = {"max_pairwise": "bad"}
    caplog.set_level(logging.ERROR, logger="pmcc.risk")
    dry_run(cfg)
    assert any("相关性规则检查异常" in rec.message for rec in caplog.records)


def test_dry_run_logs_error_drawdown_guard(caplog):
    cfg = base_cfg()
    cfg["risk_policy.json"]["drawdown_guard"] = {"threshold": "x", "action": "reduce"}
    caplog.set_level(logging.ERROR, logger="pmcc.risk")
    dry_run(cfg)
    assert any("回撤守护规则检查异常" in rec.message for rec in caplog.records)


def test_dry_run_logs_error_assignment_dividend(caplog):
    cfg = base_cfg()
    cfg["risk_policy.json"]["assignment_dividend"] = {
        "ex_div_protection": True,
        "min_extrinsic_vs_dividend": "bad",
    }
    caplog.set_level(logging.ERROR, logger="pmcc.risk")
    dry_run(cfg)
    assert any("除息/指派规则检查异常" in rec.message for rec in caplog.records)

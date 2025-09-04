from __future__ import annotations

from dataclasses import asdict

import pmcc.contracts as c


def test_error_code_enum_contains_expected_values():
    assert c.PMCCErrorCode.RATE_LIMIT.value == "RATE_LIMIT"
    assert c.PMCCErrorCode.KILL_SWITCH_ACTIVE.value == "KILL_SWITCH_ACTIVE"
    assert c.PMCCErrorCode.PRECHECK_BLOCKED.value == "PRECHECK_BLOCKED"


def test_apiresult_ok_and_error_shapes():
    r_ok = c.APIResult[dict](ok=True, data={"k": 1})
    d = r_ok.to_dict()
    assert d["ok"] is True and d["data"]["k"] == 1 and d["error"] is None

    err = c.APIError(code=c.PMCCErrorCode.RATE_LIMIT, message="too fast", detail={"retry_after": 1})
    r_ng = c.APIResult[None](ok=False, error=err)
    d2 = asdict(r_ng)
    assert d2["ok"] is False and d2["data"] is None and d2["error"]["code"] == c.PMCCErrorCode.RATE_LIMIT


def test_execution_plan_and_precheck_detail_contracts():
    pd = c.PreCheckDetail(name="spread", description="guard quotes", applies=True)
    plan = c.ExecutionPlan(
        order_template="IBKR Combo",
        pre_checks=["spread", "slippage"],
        pre_checks_verbose=["spread: x", "slippage: y"],
        pre_checks_detail=[pd],
    )
    d = asdict(plan)
    assert d["order_template"] and isinstance(d["pre_checks_detail"], list)


def test_data_layer_contracts_shape():
    qr = c.QuoteRequest(symbol="SPY")
    q = c.Quote(symbol="SPY", bid=1.0, ask=1.2, last=1.1, ts=123456)
    oc = c.OptionContract(
        symbol="SPY",
        type="C",
        dte=30,
        strike=500.0,
        bid=1.0,
        ask=1.2,
        last=1.1,
        iv=0.2,
        oi=1000,
        delta=0.25,
        gamma=0.01,
    )
    assert qr.symbol == "SPY" and q.ts > 0 and oc.type == "C"

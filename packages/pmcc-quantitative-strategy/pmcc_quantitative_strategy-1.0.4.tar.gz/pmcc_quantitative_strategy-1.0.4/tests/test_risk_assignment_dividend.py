import decimal

import pytest

from pmcc import risk as risk
from pmcc.risk import check_assignment_dividend


def test_assignment_ok_when_protection_off():
    cfg = {"ex_div_protection": False, "min_extrinsic_vs_dividend": 0.0}
    candidates = [
        {"ticker": "AAPL", "extrinsic": 0.10, "dividend": 0.50, "is_short_call": True},
    ]
    r = check_assignment_dividend(cfg, candidates)
    assert r["status"] == "ok"
    assert r["violations"] == []


def test_assignment_dividend_numeric_parse_failure_monkeypatched(monkeypatch):
    # Force Decimal conversion failure during candidate loop to exercise the except branch.
    real_decimal = decimal.Decimal

    def fake_decimal(s: str):
        # Allow min_extrinsic_vs_dividend ("0.0") to convert, but fail for others used in loop
        if s == "0.0":
            return real_decimal(s)
        # Simulate InvalidOperation during conversion
        raise risk.InvalidOperation

    monkeypatch.setattr(risk, "Decimal", fake_decimal)

    cfg = {"ex_div_protection": True, "min_extrinsic_vs_dividend": 0.0}
    cands = [
        {"ticker": "AAPL", "extrinsic": 0.10, "dividend": 0.05, "is_short_call": True},
    ]

    with pytest.raises(ValueError):
        check_assignment_dividend(cfg, cands)


def test_assignment_warn_when_dividend_exceeds_extrinsic():
    cfg = {"ex_div_protection": True, "min_extrinsic_vs_dividend": 0.0}
    candidates = [
        {"ticker": "AAPL", "extrinsic": 0.20, "dividend": 0.25, "is_short_call": True},
    ]
    r = check_assignment_dividend(cfg, candidates)
    assert r["status"] == "warn"
    assert any(v["ticker"] == "AAPL" for v in r["violations"])  # flagged


def test_assignment_ignores_non_short_calls():
    cfg = {"ex_div_protection": True, "min_extrinsic_vs_dividend": 0.0}
    candidates = [
        {"ticker": "AAPL", "extrinsic": 0.05, "dividend": 0.10, "is_short_call": False},
    ]
    r = check_assignment_dividend(cfg, candidates)
    assert r["status"] == "ok"
    assert r["violations"] == []

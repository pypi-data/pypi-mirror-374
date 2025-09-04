from __future__ import annotations

import pmcc.contracts as c
import pmcc.providers as p


class DummyMD:
    def get_quote(self, req: c.QuoteRequest) -> c.APIResult[c.Quote]:
        return c.APIResult(ok=True, data=c.Quote(symbol=req.symbol, bid=1.0, ask=1.2, last=1.1, ts=1))

    def get_quotes(self, req: c.SymbolsRequest) -> c.APIResult[c.MultiQuote]:
        quotes = [c.Quote(symbol=s, bid=1.0, ask=1.2, last=1.1, ts=1) for s in req.symbols]
        return c.APIResult(ok=True, data=c.MultiQuote(quotes=quotes, page=None))


class DummyOP:
    def get_chain(self, req: c.OptionChainRequest) -> c.APIResult[list[c.OptionContract]]:
        oc = c.OptionContract(
            symbol=req.symbol,
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
        return c.APIResult(ok=True, data=[oc])


class DummyExec:
    def plan(self, cfgs: dict) -> c.APIResult[c.ExecutionPlan]:
        pd = c.PreCheckDetail(name="spread", description="guard quotes", applies=True)
        ep = c.ExecutionPlan(
            order_template="IBKR Combo",
            pre_checks=["spread"],
            pre_checks_verbose=["spread: x"],
            pre_checks_detail=[pd],
        )
        return c.APIResult(ok=True, data=ep)


class DummyPre:
    def run(self, cfgs: dict, context: dict) -> c.APIResult[c.PretradeResult]:
        return c.APIResult(ok=True, data=c.PretradeResult(ok=True, reasons=[], details={}))


def test_runtime_protocol_conformance_and_shapes():
    md = DummyMD()
    op = DummyOP()
    ex = DummyExec()
    pr = DummyPre()

    # runtime_checkable Protocols allow isinstance checks
    assert isinstance(md, p.MarketDataProvider)
    assert isinstance(op, p.OptionsProvider)
    assert isinstance(ex, p.ExecutionPlanner)
    assert isinstance(pr, p.PretradeChecks)

    # shape checks
    r1 = md.get_quote(c.QuoteRequest(symbol="SPY"))
    assert r1.ok and r1.data and r1.data.symbol == "SPY"

    r2 = md.get_quotes(c.SymbolsRequest(symbols=["SPY", "QQQ"]))
    assert r2.ok and r2.data and len(r2.data.quotes) == 2

    r3 = op.get_chain(c.OptionChainRequest(symbol="SPY"))
    assert r3.ok and r3.data and r3.data[0].type == "C"

    r4 = ex.plan({})
    assert r4.ok and r4.data and r4.data.pre_checks_detail[0].name == "spread"

    r5 = pr.run({}, {})
    assert r5.ok and r5.data and r5.data.ok is True

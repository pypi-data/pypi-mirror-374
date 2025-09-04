from __future__ import annotations

from typing import Any

from pmcc.contracts import OptionChainRequest, QuoteRequest
from pmcc.real_readonly import RealReadonlyMarket, RealReadonlyOptions


def test_real_http_success_quote_and_chain():
    # Success fetchers: should not include error detail; attempts path should be minimal
    def q_fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        return {"symbol": params["symbol"], "bid": 10.0, "ask": 10.2, "last": 10.1, "ts": 123}

    def c_fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        return {
            "chain": [
                {
                    "symbol": params["symbol"],
                    "type": "C",
                    "dte": 30,
                    "strike": 500.0,
                    "bid": 1.0,
                    "ask": 1.2,
                }
            ]
        }

    from pmcc.throttle import TokenBucket

    m = RealReadonlyMarket(fetcher=q_fetch, endpoint="/quote", bucket=TokenBucket(100.0))
    o = RealReadonlyOptions(fetcher=c_fetch, endpoint="/options", bucket=TokenBucket(100.0))

    qr = m.get_quote(QuoteRequest(symbol="SPY"))
    assert qr.ok and qr.data is not None and qr.data.symbol == "SPY"

    cr = o.get_chain(OptionChainRequest(symbol="SPY"))
    assert cr.ok and cr.data is not None and len(cr.data) == 1 and cr.data[0].strike == 500.0

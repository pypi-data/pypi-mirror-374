from __future__ import annotations

import sys
from types import SimpleNamespace

from pmcc.contracts import APIResult, OptionChainRequest, QuoteRequest
from pmcc.real_http_provider import make_market_provider, make_options_provider


def test_real_http_provider_factories(monkeypatch):
    # Fake requests.get to avoid network
    class Resp:
        def __init__(self, body):
            self.status_code = 200
            self._body = body

        def json(self):  # noqa: D401 - test stub
            return self._body

    def get(url, params=None, timeout=None, headers=None):  # noqa: A002 - signature tolerant
        if url.endswith("/options"):
            return Resp(
                {
                    "chain": [
                        {
                            "symbol": params.get("symbol", "SPY"),
                            "type": "C",
                            "dte": 30,
                            "strike": 500.0,
                            "bid": 1.0,
                            "ask": 1.2,
                        }
                    ]
                }
            )
        return Resp({"symbol": params.get("symbol", "SPY"), "bid": 10.0, "ask": 10.2, "last": 10.1, "ts": 123})

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(get=get))

    mkt = make_market_provider({})
    r = mkt.get_quote(QuoteRequest(symbol="SPY"))
    assert isinstance(r, APIResult) and r.ok and r.data and r.data.symbol == "SPY"

    opt = make_options_provider({})
    rr = opt.get_chain(OptionChainRequest(symbol="SPY"))
    assert isinstance(rr, APIResult) and rr.ok and rr.data and len(rr.data) == 1

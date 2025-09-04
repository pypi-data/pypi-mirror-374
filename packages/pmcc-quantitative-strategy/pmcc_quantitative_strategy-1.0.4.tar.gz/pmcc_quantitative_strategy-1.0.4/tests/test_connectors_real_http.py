from __future__ import annotations

import sys
from dataclasses import asdict
from types import SimpleNamespace

from pmcc.connectors import get_market_data_provider, get_options_provider
from pmcc.contracts import OptionChainRequest, PMCCErrorCode, QuoteRequest


def test_real_http_market_and_options_success(monkeypatch):
    # Enable real http path
    monkeypatch.setenv("PMCC_DATA_BACKEND", "real")
    monkeypatch.setenv("PMCC_REAL_HTTP", "1")
    monkeypatch.setenv("PMCC_REAL_BASE_URL", "http://fake")

    # fake requests module
    class Resp:
        def __init__(self, status: int, body: dict | None):
            self.status_code = status
            self._body = body or {}

        def json(self):  # noqa: D401 - test stub
            return self._body

    def get(url, params=None, timeout=None, headers=None):  # noqa: A002 - signature tolerant
        if url.endswith("/options"):
            return Resp(
                200,
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
                },
            )
        return Resp(200, {"symbol": params.get("symbol", "SPY"), "bid": 10.0, "ask": 10.2, "last": 10.1, "ts": 123})

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(get=get))

    prov = get_market_data_provider({})
    r = prov.get_quote(QuoteRequest(symbol="SPY"))
    assert r.ok and r.data and r.data.symbol == "SPY"
    dj = asdict(r)
    assert dj["ok"] is True and dj["data"]["symbol"] == "SPY"

    op = get_options_provider({})
    cr = op.get_chain(OptionChainRequest(symbol="SPY"))
    assert cr.ok and cr.data and len(cr.data) == 1
    dj2 = asdict(cr)
    assert dj2["ok"] is True and isinstance(dj2["data"], list) and dj2["data"][0]["type"] == "C"


def test_real_http_error_mapping(monkeypatch):
    monkeypatch.setenv("PMCC_DATA_BACKEND", "real")
    monkeypatch.setenv("PMCC_REAL_HTTP", "1")
    monkeypatch.setenv("PMCC_REAL_BASE_URL", "http://fake")

    class Resp:
        status_code = 500

        def json(self):  # noqa: D401 - not used
            return {}

    def get_fail(url, **kwargs):  # noqa: ARG001 - unused
        return Resp()

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(get=get_fail))
    prov = get_market_data_provider({})
    r = prov.get_quote(QuoteRequest(symbol="SPY"))
    assert r.ok is False and r.error and r.error.code == PMCCErrorCode.NETWORK_ERROR

    # invalid json
    class Resp2:
        status_code = 200

        def json(self):  # noqa: D401 - raise
            raise ValueError("broken")

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(get=lambda *a, **k: Resp2()))
    # new provider to avoid rate limit between calls
    prov2 = get_market_data_provider({})
    r2 = prov2.get_quote(QuoteRequest(symbol="SPY"))
    assert r2.ok is False and r2.error and r2.error.code == PMCCErrorCode.NETWORK_ERROR

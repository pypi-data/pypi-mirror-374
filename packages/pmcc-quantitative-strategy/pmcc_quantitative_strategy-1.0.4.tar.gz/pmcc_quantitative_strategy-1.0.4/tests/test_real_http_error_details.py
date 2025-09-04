from __future__ import annotations

from typing import Any

from pmcc.contracts import OptionChainRequest, QuoteRequest
from pmcc.real_readonly import RealReadonlyMarket, RealReadonlyOptions


def _mk_market(fetcher):
    from pmcc.throttle import TokenBucket

    return RealReadonlyMarket(fetcher=fetcher, endpoint="/quote", bucket=TokenBucket(10.0))


def _mk_options(fetcher):
    from pmcc.throttle import TokenBucket

    return RealReadonlyOptions(fetcher=fetcher, endpoint="/options", bucket=TokenBucket(10.0))


def test_error_detail_http_status_market():
    def fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        raise RuntimeError("http status 503")

    m = _mk_market(fetch)
    r = m.get_quote(QuoteRequest(symbol="SPY"))
    assert not r.ok and r.error is not None
    assert r.error.detail and r.error.detail.get("status_code") == 503
    assert r.error.detail.get("attempts") == 3  # retries=2 → 3 attempts
    assert r.error.detail.get("endpoint") == "/quote"


def test_error_detail_invalid_json_options():
    def fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        raise RuntimeError("invalid json: x")

    o = _mk_options(fetch)
    r = o.get_chain(OptionChainRequest(symbol="SPY"))
    assert not r.ok and r.error is not None
    assert r.error.detail and r.error.detail.get("error") == "invalid_json"
    assert r.error.detail.get("attempts") == 3
    assert r.error.detail.get("endpoint") == "/options"


def test_error_detail_timeout_heuristic():
    class TimeoutEx(Exception):
        pass

    def fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        raise TimeoutEx("Timeout")

    m = _mk_market(fetch)
    r = m.get_quote(QuoteRequest(symbol="SPY"))
    assert not r.ok and r.error is not None
    assert r.error.detail and r.error.detail.get("error") in {"timeout"}
    assert r.error.detail.get("attempts") == 3


def test_error_detail_connection_market():
    class ConnEx(Exception):
        pass

    def fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        raise ConnEx("connection aborted")

    m = _mk_market(fetch)
    r = m.get_quote(QuoteRequest(symbol="SPY"))
    assert not r.ok and r.error is not None
    assert r.error.detail and r.error.detail.get("error") == "connection"


def test_error_detail_http_status_options():
    def fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        raise RuntimeError("http status 500")

    o = _mk_options(fetch)
    r = o.get_chain(OptionChainRequest(symbol="SPY"))
    assert not r.ok and r.error is not None
    assert r.error.detail and r.error.detail.get("status_code") == 500
    assert r.error.detail.get("endpoint") == "/options"


def test_error_detail_timeout_options():
    class TimeoutEx(Exception):
        pass

    def fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        raise TimeoutEx("Timeout waiting")

    o = _mk_options(fetch)
    r = o.get_chain(OptionChainRequest(symbol="SPY"))
    assert not r.ok and r.error is not None
    assert r.error.detail and r.error.detail.get("error") == "timeout"


def test_error_detail_connection_options():
    class ConnEx(Exception):
        pass

    def fetch(ep: str, params: dict[str, Any]):  # noqa: ARG001
        raise ConnEx("connection reset")

    o = _mk_options(fetch)
    r = o.get_chain(OptionChainRequest(symbol="SPY"))
    assert not r.ok and r.error is not None
    assert r.error.detail and r.error.detail.get("error") == "connection"

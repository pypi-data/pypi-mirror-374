from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

import pmcc.connectors as conn


def test_http_fetcher_requests_missing(monkeypatch):
    """Cover connectors._http_fetcher import error branch (requests missing)."""

    real_import = importlib.import_module

    def fake_import(name: str):
        if name == "requests":
            raise RuntimeError("missing")
        return real_import(name)

    monkeypatch.setattr(importlib, "import_module", fake_import, raising=True)

    with pytest.raises(RuntimeError) as ei:
        conn._http_fetcher("/quote", {"symbol": "SPY"})
    assert "requests missing" in str(ei.value)


def test_http_fetcher_headers_json_invalid_and_success(monkeypatch):
    """Invalid PMCC_REAL_HEADERS_JSON should be ignored and still succeed."""

    class Resp:
        status_code = 200

        def json(self):  # noqa: D401 - simple
            return {"symbol": "SPY", "bid": 1.0, "ask": 1.2, "last": 1.1, "ts": 1}

    def get(_url, params=None, timeout=None, headers=None):  # noqa: A002 - signature tolerant
        # headers will be None due to invalid JSON; we only assert it does not crash
        return Resp()

    fake_requests = SimpleNamespace(get=get)

    # Ensure import succeeds and our fake module is returned
    def import_requests(name: str):
        if name == "requests":
            return fake_requests
        return importlib.import_module(name)

    monkeypatch.setenv("PMCC_REAL_BASE_URL", "http://fake")
    monkeypatch.setenv("PMCC_REAL_HEADERS_JSON", "{not a json}")
    monkeypatch.setattr(importlib, "import_module", import_requests, raising=True)

    out = conn._http_fetcher("/quote", {"symbol": "SPY"})
    assert out and out.get("symbol") == "SPY"


def test_http_fetcher_headers_json_valid(monkeypatch):
    """Valid PMCC_REAL_HEADERS_JSON should be converted to str:str mapping (lines 67-68)."""

    class Resp:
        status_code = 200

        def json(self):  # noqa: D401 - simple
            return {"symbol": "SPY", "bid": 1.0, "ask": 1.2, "last": 1.1, "ts": 1}

    captured = {}

    def get(url, params=None, timeout=None, headers=None):  # noqa: A002 - signature tolerant
        captured["headers"] = headers
        return Resp()

    fake_requests = SimpleNamespace(get=get)

    def import_requests(name: str):
        if name == "requests":
            return fake_requests
        return importlib.import_module(name)

    monkeypatch.setenv("PMCC_REAL_BASE_URL", "http://fake")
    # include non-str value to verify coercion to str
    monkeypatch.setenv("PMCC_REAL_HEADERS_JSON", '{\n "Authorization": "Bearer X", "X-Trace": 123\n}')
    monkeypatch.setattr(importlib, "import_module", import_requests, raising=True)

    out = conn._http_fetcher("/quote", {"symbol": "SPY"})
    assert out and out.get("symbol") == "SPY"
    assert captured.get("headers") == {"Authorization": "Bearer X", "X-Trace": "123"}


def test_default_fetcher_reads_json(monkeypatch):
    """Cover connectors._default_fetcher path with a monkeypatched urlopen."""

    from urllib import request as _rq  # import namespace to patch attr

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # noqa: D401 - context manager
            return False

        def read(self):  # noqa: D401 - bytes body
            return b'{\n "symbol": "SPY", "bid": 1.0, "ask": 1.2, "last": 1.1, "ts": 1\n}'

    def fake_urlopen(_req, timeout=2.0):  # noqa: ARG001
        return _Resp()

    monkeypatch.setenv("PMCC_REAL_BASE_URL", "http://example")
    monkeypatch.setattr(_rq, "urlopen", fake_urlopen, raising=True)

    out = conn._default_fetcher("/quote", {"symbol": "SPY"})
    assert out and out.get("symbol") == "SPY"

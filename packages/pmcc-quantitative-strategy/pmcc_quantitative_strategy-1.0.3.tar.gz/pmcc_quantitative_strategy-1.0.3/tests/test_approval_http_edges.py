from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from pmcc.approval import HTTPApprovalService
from pmcc.contracts import APIResult, ApprovalDecision, ApprovalRequest, PMCCErrorCode


def test_http_approval_2xx_invalid_json_body(monkeypatch):
    """Covers lines where r.json() raises and body defaults to {} (lines 91-92)."""

    class Resp:
        status_code = 200

        def json(self):  # noqa: D401 - simulate invalid json
            raise ValueError("invalid json")

    def post(_url, **_kwargs):
        return Resp()

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=post))
    svc = HTTPApprovalService(url="http://example/approve", retries=0, base_delay=0.0)
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    # Should succeed with defaults from empty body
    assert isinstance(r, APIResult) and r.ok and isinstance(r.data, ApprovalDecision)
    assert r.data.approved is False and r.data.approver == "http"


@pytest.mark.parametrize(
    "exc_name, expected",
    [
        ("Timeout", "timeout"),
        ("ConnectionError", "connection"),
    ],
)
def test_http_approval_exception_mapping_timeout_connection(monkeypatch, exc_name, expected):
    """Covers mapping of requests.exceptions.Timeout/ConnectionError to NETWORK_ERROR with detail."""

    class Exceptions:
        class Timeout(Exception):
            pass

        class ConnectionError(Exception):
            pass

    def post(_url, **_kwargs):
        raise getattr(Exceptions, exc_name)()

    fake_requests = SimpleNamespace(post=post, exceptions=Exceptions)
    monkeypatch.setitem(sys.modules, "requests", fake_requests)

    svc = HTTPApprovalService(url="http://example/approve", retries=0, base_delay=0.0)
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert r.ok is False and r.error and r.error.code == PMCCErrorCode.NETWORK_ERROR
    assert isinstance(r.error.detail, dict) and r.error.detail.get("error") == expected


def test_http_approval_exception_mapping_inner_try_except(monkeypatch):
    """Force inner mapping try to raise, covering lines 123-124 (except: pass)."""

    class Explosive:
        def __getattr__(self, name):  # raise on .exceptions access
            raise RuntimeError("boom")

        def post(self, url, **kwargs):  # noqa: A003 - method name okay in test
            # trigger outer except path with a generic error
            raise ValueError("post failed")

    monkeypatch.setitem(sys.modules, "requests", Explosive())
    svc = HTTPApprovalService(url="http://example/approve", retries=0, base_delay=0.0)
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert r.ok is False and r.error and r.error.code == PMCCErrorCode.NETWORK_ERROR

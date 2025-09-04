from __future__ import annotations

import sys
from types import SimpleNamespace

from pmcc.approval import HTTPApprovalService
from pmcc.contracts import APIResult, ApprovalDecision, ApprovalRequest


def test_http_approval_success(monkeypatch):
    # create a fake requests module
    def post(url, **kwargs):  # noqa: A002 - shadow ok in test
        class Resp:
            status_code = 200

            def json(self):
                return {"approved": True, "approver": "ops", "comment": None}

        return Resp()

    fake_requests = SimpleNamespace(post=post)
    monkeypatch.setitem(sys.modules, "requests", fake_requests)  # inject

    svc = HTTPApprovalService(url="http://example/approve")
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert isinstance(r, APIResult) and r.ok and isinstance(r.data, ApprovalDecision) and r.data.approved is True


def test_http_approval_non_2xx_and_missing_requests(monkeypatch):
    # non-2xx response
    class Resp:
        status_code = 500

        def json(self):  # noqa: D401 - unused
            return {}

    def post(url, **kwargs):  # noqa: A002
        return Resp()

    fake_requests = SimpleNamespace(post=post)
    monkeypatch.setitem(sys.modules, "requests", fake_requests)
    svc = HTTPApprovalService(url="http://example/approve")
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert r.ok is False and r.error and r.error.code.name == "NETWORK_ERROR"

    # simulate requests missing
    monkeypatch.delitem(sys.modules, "requests", raising=False)
    r2 = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert r2.ok is False and r2.error and r2.error.code.name == "NETWORK_ERROR"


def test_http_approval_retry_then_success(monkeypatch):
    calls = {"n": 0}

    class Resp:
        def __init__(self, status):
            self.status_code = status

        def json(self):  # noqa: D401 - unused
            return {"approved": True, "approver": "ops"}

    def post(_url, **_kwargs):
        calls["n"] += 1
        if calls["n"] <= 2:
            return Resp(500)
        return Resp(200)

    import sys
    from types import SimpleNamespace

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=post))
    svc = HTTPApprovalService(url="http://example/approve", retries=2, base_delay=0.0)
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert r.ok and r.data and r.data.approved is True and calls["n"] == 3


def test_http_approval_retry_exhausted(monkeypatch):
    class Resp:
        status_code = 503

        def json(self):  # noqa: D401 - unused
            return {}

    def post(_url, **_kwargs):
        return Resp()

    import sys
    from types import SimpleNamespace

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=post))
    svc = HTTPApprovalService(url="http://example/approve", retries=1, base_delay=0.0)
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert r.ok is False and r.error and r.error.detail and r.error.detail.get("attempts") == 2

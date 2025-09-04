from __future__ import annotations

from types import SimpleNamespace

from pmcc.approval import HTTPApprovalService
from pmcc.contracts import APIResult, ApprovalRequest


def test_http_approval_inner_exception_mapping_is_tolerant(monkeypatch):
    # Craft a requests module whose exceptions object raises on getattr
    class Exc:
        def __getattr__(self, _name):  # noqa: D401 - induce failure inside mapping
            raise RuntimeError("boom")

    def post(_url, **_kwargs):  # noqa: D401 - simulate failure
        raise RuntimeError("zzz")

    fake_requests = SimpleNamespace(post=post, exceptions=Exc())
    monkeypatch.setitem(__import__("sys").modules, "requests", fake_requests)

    svc = HTTPApprovalService(url="http://example/approve", retries=1, base_delay=0.0)
    r = svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="cli"))
    assert isinstance(r, APIResult) and r.ok is False and r.error is not None
    # attempts should reflect retries+1 even when mapping raises
    assert r.error.detail and r.error.detail.get("attempts") == 2
    # error key may be absent due to inner mapping exception; tolerate either
    assert "error" not in r.error.detail or r.error.detail.get("error") in {"timeout", "connection"}

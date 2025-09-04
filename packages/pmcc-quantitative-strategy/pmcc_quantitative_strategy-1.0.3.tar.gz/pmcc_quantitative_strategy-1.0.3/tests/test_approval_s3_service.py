from __future__ import annotations

import json
from types import SimpleNamespace

import pmcc.approval as appr
from pmcc.contracts import ApprovalRequest


def test_approval_s3_service_puts_object(monkeypatch):
    events: list[dict] = []

    class _Client:
        def put_object(self, **kw):  # noqa: D401 - test stub
            events.append(kw)

    def _client(name: str):  # noqa: D401 - test stub
        assert name == "s3"
        return _Client()

    fake_boto3 = SimpleNamespace(client=_client)
    # patch uuid/time used inside service for deterministic key
    import time
    import uuid

    monkeypatch.setattr(uuid, "uuid4", lambda: "uuid-1", raising=True)
    # freeze time.time used inside service
    monkeypatch.setattr(time, "time", lambda: 1234567890, raising=True)
    # importlib path
    import importlib

    real_import_module = importlib.import_module
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda n: fake_boto3 if n == "boto3" else real_import_module(n),
        raising=True,
    )

    svc = appr.ApprovalS3Service(bucket="bkt", prefix="audit", kms_key_id=None)
    req = ApprovalRequest(plan_id="p", summary={"pretrade_ok": True}, requested_by="cli")
    r = svc.request(req)
    assert r.ok is True
    assert len(events) == 1
    ev = events[0]
    assert ev["Bucket"] == "bkt"
    assert ev["Key"].startswith("audit/") and ev["ContentType"] == "application/json"
    body = json.loads(ev["Body"].decode("utf-8"))
    assert body["request"]["plan_id"] == "p"

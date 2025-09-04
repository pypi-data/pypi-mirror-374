from __future__ import annotations

from types import SimpleNamespace

import pmcc.approval as appr
from pmcc.contracts import ApprovalRequest


def test_approval_s3_service_with_kms(monkeypatch):
    calls = []

    class _Client:
        def put_object(self, **kw):  # noqa: D401 - test stub
            calls.append(kw)

    fake_boto3 = SimpleNamespace(client=lambda name: _Client())
    import importlib

    real_import_module = importlib.import_module
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda n: fake_boto3 if n == "boto3" else real_import_module(n),
        raising=True,
    )
    # freeze uuid/time for deterministic key
    import time
    import uuid

    monkeypatch.setattr(uuid, "uuid4", lambda: "uuid-2", raising=True)
    monkeypatch.setattr(time, "time", lambda: 1111111111, raising=True)

    svc = appr.ApprovalS3Service(bucket="bkt", prefix="audit", kms_key_id="kms-123")
    r = svc.request(ApprovalRequest(plan_id="p", summary={}, requested_by="cli"))
    assert r.ok is True and len(calls) == 1
    args = calls[0]
    assert args.get("ServerSideEncryption") == "aws:kms" and args.get("SSEKMSKeyId") == "kms-123"


def test_approval_s3_service_error_path(monkeypatch):
    class _Client:
        def put_object(self, **_):  # noqa: D401 - simulate error
            raise RuntimeError("denied")

    fake_boto3 = SimpleNamespace(client=lambda name: _Client())
    import importlib

    real_import_module = importlib.import_module
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda n: fake_boto3 if n == "boto3" else real_import_module(n),
        raising=True,
    )
    # freeze uuid/time for deterministic key
    import time
    import uuid

    monkeypatch.setattr(uuid, "uuid4", lambda: "uuid-3", raising=True)
    monkeypatch.setattr(time, "time", lambda: 2222222222, raising=True)

    svc = appr.ApprovalS3Service(bucket="bkt", prefix="audit", kms_key_id=None)
    r = svc.request(ApprovalRequest(plan_id="p", summary={}, requested_by="cli"))
    assert r.ok is False and r.error is not None
    det = r.error.detail or {}
    assert det.get("bucket") == "bkt" and isinstance(det.get("key"), str)


def test_approval_s3_service_bucket_required():
    import pytest

    with pytest.raises(ValueError):
        appr.ApprovalS3Service(bucket="", prefix="audit", kms_key_id=None)

from __future__ import annotations

import json
from pathlib import Path

from pmcc.approval import ApprovalFileService
from pmcc.contracts import ApprovalRequest


def test_approval_file_service_append_and_replay(tmp_path: Path):
    logp = tmp_path / "approval.log"
    svc = ApprovalFileService(logp)
    r1 = svc.request(ApprovalRequest(plan_id="p1", summary={"pretrade_ok": True}, requested_by="ai"))
    r2 = svc.request(ApprovalRequest(plan_id="p2", summary={"pretrade_ok": False}, requested_by="ai"))
    assert r1.ok and r2.ok and logp.exists()
    last = svc.replay_last(1)
    assert isinstance(last, list) and isinstance(last[0], dict)
    payload = json.loads(logp.read_text(encoding="utf-8").splitlines()[-1])
    assert payload["decision"]["approved"] is False


def test_approval_file_write_error(monkeypatch, tmp_path: Path):
    from pmcc.approval import ApprovalFileService
    from pmcc.contracts import ApprovalRequest

    svc = ApprovalFileService(tmp_path / "appr.log")

    # force open to raise
    class BadPath(type(tmp_path)):
        def open(self, *a, **k):  # type: ignore[no-untyped-def]
            raise RuntimeError("io")

    monkeypatch.setattr(svc, "path", BadPath(tmp_path / "appr.log"), raising=True)
    r = svc.request(ApprovalRequest(plan_id="p", summary={}, requested_by="ai"))
    assert r.ok is False and r.error


def test_approval_replay_file_not_found(tmp_path: Path):
    from pmcc.approval import ApprovalFileService

    svc = ApprovalFileService(tmp_path / "missing" / "appr.log")
    out = svc.replay_last(1)
    assert out == []


def test_approval_replay_skip_invalid_json(tmp_path: Path):
    from pmcc.approval import ApprovalFileService
    from pmcc.contracts import ApprovalRequest

    svc = ApprovalFileService(tmp_path / "appr2.log")
    # write one valid and one invalid
    svc.request(ApprovalRequest(plan_id="p1", summary={}, requested_by="ai"))
    (tmp_path / "appr2.log").write_text("{invalid}\n", encoding="utf-8")
    out = svc.replay_last(2)
    assert isinstance(out, list)

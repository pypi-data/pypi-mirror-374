from __future__ import annotations

from pathlib import Path

from pmcc.approval import ApprovalFileService
from pmcc.contracts import ApprovalRequest


def test_file_env_parse_fallback_to_defaults(monkeypatch, tmp_path: Path):
    # invalid ints should fall back to defaults without raising
    monkeypatch.setenv("PMCC_APPROVAL_MAX_BYTES", "notint")
    monkeypatch.setenv("PMCC_APPROVAL_ROTATE_KEEP", "oops")
    svc = ApprovalFileService(tmp_path / "appr.log")
    # defaults: 5MB and 1
    assert getattr(svc, "_max_bytes", None) == 5 * 1024 * 1024
    assert getattr(svc, "_rotate_keep", None) == 1


def test_file_rotation_keep_two_performs_rename_chain(monkeypatch, tmp_path: Path):
    log = tmp_path / "approval.jsonl"
    # Set tiny max size and keep two backups to exercise rename path
    monkeypatch.setenv("PMCC_APPROVAL_MAX_BYTES", "1")
    monkeypatch.setenv("PMCC_APPROVAL_ROTATE_KEEP", "2")
    svc = ApprovalFileService(log)
    req = ApprovalRequest(plan_id="p", summary={"pretrade_ok": True}, requested_by="cli")
    # trigger multiple rotations so that .1 exists and gets renamed to .2
    for _ in range(5):
        svc.request(req)
    b1 = Path(str(log) + ".1")
    b2 = Path(str(log) + ".2")
    assert log.exists() and b1.exists() and b2.exists()

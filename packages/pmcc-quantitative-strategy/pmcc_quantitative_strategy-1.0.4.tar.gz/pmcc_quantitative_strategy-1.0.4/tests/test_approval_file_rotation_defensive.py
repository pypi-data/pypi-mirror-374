from __future__ import annotations

from pathlib import Path

from pmcc.approval import ApprovalFileService
from pmcc.contracts import ApprovalRequest


def test_approval_file_rotation_defensive(monkeypatch, tmp_path):
    log = tmp_path / "approval.jsonl"
    # tiny max bytes to trigger rotation quickly; keep one backup to exercise delete/rename branches
    monkeypatch.setenv("PMCC_APPROVAL_MAX_BYTES", "1")
    monkeypatch.setenv("PMCC_APPROVAL_ROTATE_KEEP", "1")

    svc = ApprovalFileService(str(log))

    def req():
        return svc.request(ApprovalRequest(plan_id="p", summary={"pretrade_ok": True}, requested_by="t"))

    # Prepare file to exceed max_bytes and cause rotation on next write
    log.write_text("x" * 10, encoding="utf-8")

    # First write (should rotate current to .1 best-effort and append)
    r1 = req()
    assert r1.ok

    # Monkeypatch unlink/rename to raise, exercising defensive suppress blocks
    def bad_unlink(self):  # noqa: D401
        raise OSError("deny unlink")

    def bad_rename(self, other):  # noqa: D401, ARG002
        raise OSError("deny rename")

    monkeypatch.setattr(Path, "unlink", bad_unlink, raising=True)
    monkeypatch.setattr(Path, "rename", bad_rename, raising=True)

    # Make file big again to trigger rotation path; defensive errors will be suppressed
    log.write_text("y" * 10, encoding="utf-8")
    r2 = req()
    assert r2.ok

    # Ensure a line exists despite failures in rotation helpers
    content = log.read_text(encoding="utf-8").strip().splitlines()
    assert content and "{" in content[-1]

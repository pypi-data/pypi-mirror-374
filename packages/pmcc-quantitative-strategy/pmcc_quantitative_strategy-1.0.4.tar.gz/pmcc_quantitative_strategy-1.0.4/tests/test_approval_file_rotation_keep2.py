from __future__ import annotations

from pathlib import Path

from pmcc.approval import ApprovalFileService
from pmcc.contracts import ApprovalRequest


def test_approval_file_rotation_keep2_unlink_nbk(monkeypatch, tmp_path):
    log = tmp_path / "approval.jsonl"
    # trigger rotation frequently and allow keep=2 so the else-branch executes (k < keep)
    monkeypatch.setenv("PMCC_APPROVAL_MAX_BYTES", "1")
    monkeypatch.setenv("PMCC_APPROVAL_ROTATE_KEEP", "2")

    svc = ApprovalFileService(str(log))

    def req():
        return svc.request(ApprovalRequest(plan_id="p", summary={"pretrade_ok": True}, requested_by="t"))

    # prepare current file large -> rotation on first write (current -> .1)
    log.write_text("x" * 10, encoding="utf-8")
    assert req().ok

    # create a pre-existing .2 so that在 k=1 时 nbk==.2 存在
    p2 = Path(str(log) + ".2")
    p2.write_text("old2", encoding="utf-8")

    # 保留 .2 不被 k=2 分支删除：对 Path.unlink 做选择性 monkeypatch
    _orig_unlink = Path.unlink

    def unlink_conditional(self: Path):  # noqa: D401
        # 当删除目标为 .2 时，跳过以便在 k=1 时 nbk.exists() 为真
        if str(self).endswith(".2"):
            return None
        return _orig_unlink(self)

    monkeypatch.setattr(Path, "unlink", unlink_conditional, raising=True)

    # make current large again -> second rotation run will attempt to move .1->.2,
    # and because .2 exists it should first unlink nbk (.2), hitting line 64
    log.write_text("y" * 10, encoding="utf-8")
    assert req().ok

    # verify .2 was replaced and log has a valid JSON line appended
    assert p2.exists()
    assert "old2" not in p2.read_text(encoding="utf-8")
    last = log.read_text(encoding="utf-8").splitlines()[-1]
    assert last.strip().startswith("{")

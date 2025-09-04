from __future__ import annotations

from pathlib import Path

from pmcc.approval import ApprovalFileService
from pmcc.contracts import ApprovalRequest


def test_approval_file_rotation(tmp_path: Path, monkeypatch):
    log = tmp_path / "approval.jsonl"
    # set tiny max_bytes to force rotation quickly; keep 1 backup
    monkeypatch.setenv("PMCC_APPROVAL_MAX_BYTES", "1")
    monkeypatch.setenv("PMCC_APPROVAL_ROTATE_KEEP", "1")

    svc = ApprovalFileService(log)
    req = ApprovalRequest(plan_id="p", summary={"pretrade_ok": True}, requested_by="cli")

    # write multiple times to exceed 1 byte and trigger rotation
    for _ in range(3):
        svc.request(req)

    # current file应存在，且应存在 .1 备份之一
    assert log.exists()
    backup = Path(str(log) + ".1")
    assert backup.exists()


def test_approval_file_rotation_unlink_next(tmp_path: Path, monkeypatch):
    """当下一层备份已存在时，触发 unlink 分支确保覆盖该路径。"""
    log = tmp_path / "approval.jsonl"
    # keep 两层，确保 .2 存在后再次触发旋转时会先 unlink .2 再把 .1 重命名为 .2
    monkeypatch.setenv("PMCC_APPROVAL_MAX_BYTES", "1")
    monkeypatch.setenv("PMCC_APPROVAL_ROTATE_KEEP", "2")
    svc = ApprovalFileService(log)
    req = ApprovalRequest(plan_id="p", summary={"pretrade_ok": True}, requested_by="cli")
    # 连续写入制造 .1 与 .2
    for _ in range(4):
        svc.request(req)
    b1 = Path(str(log) + ".1")
    b2 = Path(str(log) + ".2")
    assert b1.exists() and b2.exists()
    # 再次写入，将进入 for k 循环：k=2 时 .3 不存在，k=1 时 .2 存在 → 先 unlink .2 再将 .1 → .2
    svc.request(req)
    # 断言：.2 仍然存在，但其 mtime 应更新（无法便捷断言 mtime，这里仅断言存在性与流水线通过）
    assert b2.exists()

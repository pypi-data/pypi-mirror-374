from __future__ import annotations

import sys
from pathlib import Path

import pmcc.approval as appr_mod
import pmcc.main as main_mod
from pmcc.contracts import APIResult, ApprovalDecision, ApprovalRequest


def test_main_http_env_parse_fallback_inprocess(monkeypatch, tmp_path: Path):
    """Force HTTP path with bad env values to cover parse fallback except blocks.

    We monkeypatch HTTPApprovalService to avoid any real HTTP I/O.
    """

    # Ensure config is accessible
    project_root = Path(__file__).resolve().parents[1]
    cfg = project_root / "config"

    class FakeHTTP(appr_mod.HTTPApprovalService):  # type: ignore[misc]
        def __init__(self, url: str, timeout: float = 5.0, *, retries: int = 0, base_delay: float = 0.1) -> None:  # noqa: D401
            self.url = url
            self.timeout = timeout
            self.retries = retries
            self.base_delay = base_delay

        def request(self, req: ApprovalRequest) -> APIResult[ApprovalDecision]:  # noqa: D401
            return APIResult(ok=True, data=ApprovalDecision(approved=True, approver="fake"))

    # Patch class used by main
    monkeypatch.setattr(appr_mod, "HTTPApprovalService", FakeHTTP, raising=True)

    # Set HTTP path and bad env values to trigger parse exceptions
    monkeypatch.setenv("PMCC_APPROVAL_HTTP_URL", "http://fake")
    monkeypatch.setenv("PMCC_APPROVAL_HTTP_RETRIES", "oops")  # int() fails → fallback path
    monkeypatch.setenv("PMCC_APPROVAL_HTTP_BASE_DELAY", "oops")  # float() fails → fallback path

    argv = [
        "pmcc.main",
        "--config-dir",
        str(cfg),
        "--summary-json",
        "--require-approval",
    ]
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    monkeypatch.setattr(sys, "argv", argv)

    # Capture stdout and SystemExit
    try:
        main_mod.main()
    except SystemExit as e:  # normal exit
        assert e.code == 0

    # Parse last JSON line from captured stdout via capsys is more idiomatic,
    # but here we re-run summary file to keep minimal coupling; we rely on normal flow.

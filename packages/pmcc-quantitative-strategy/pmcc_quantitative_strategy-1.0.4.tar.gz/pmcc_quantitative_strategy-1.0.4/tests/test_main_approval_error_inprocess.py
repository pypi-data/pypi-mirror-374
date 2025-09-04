from __future__ import annotations

import sys
from pathlib import Path

import pmcc.approval as appr_mod
import pmcc.main as main_mod

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def test_inprocess_approval_error_branch(monkeypatch):
    class Bad(appr_mod.InMemoryApprovalService):
        def request(self, req):  # type: ignore[no-untyped-def]
            raise RuntimeError("boom")

    monkeypatch.setenv("PYTHONPATH", str(PROJECT_ROOT / "src"))
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    monkeypatch.setattr(appr_mod, "InMemoryApprovalService", lambda: Bad(), raising=True)

    argv = [
        "pmcc.main",
        "--config-dir",
        str(CONFIG_DIR),
        "--summary-json",
        "--require-approval",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    try:
        main_mod.main()
    except SystemExit as e:
        assert e.code == 0

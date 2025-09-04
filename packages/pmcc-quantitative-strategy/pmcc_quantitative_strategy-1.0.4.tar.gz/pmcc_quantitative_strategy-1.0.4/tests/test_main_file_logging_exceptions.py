from __future__ import annotations

import logging as _real_logging
from pathlib import Path

import pmcc.main as main_mod


class _RaisingFileHandler(_real_logging.FileHandler):
    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise OSError("simulated failure creating file handler")


def test_configure_file_logging_handles_filehandler_failure(monkeypatch, tmp_path: Path):
    # Arrange: system config with a file path, but FileHandler raising
    system_cfg = {"logging": {"file": str(tmp_path / "pmcc.log")}}
    # Swap in raising handler
    monkeypatch.setattr(main_mod.logging, "FileHandler", _RaisingFileHandler, raising=True)

    # Act: should not raise
    main_mod.configure_file_logging(system_cfg, _real_logging.INFO)

    # Assert: file not created, no crash
    assert not (tmp_path / "pmcc.log").exists()

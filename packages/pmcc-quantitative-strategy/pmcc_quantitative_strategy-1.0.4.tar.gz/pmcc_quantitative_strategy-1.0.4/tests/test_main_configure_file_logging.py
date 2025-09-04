import logging
from pathlib import Path

from pmcc.main import configure_file_logging


def test_configure_file_logging_no_file_noop():
    # Should return quietly when no logging.file specified
    cfg = {"logging": {}}
    configure_file_logging(cfg, logging.INFO)


def test_configure_file_logging_skips_duplicate_handler(tmp_path: Path):
    # Prepare a real root logger with an existing FileHandler pointing to the same file
    log_path = tmp_path / "dup.log"
    root = logging.getLogger()
    # Ensure parent dir exists and attach one FileHandler manually
    fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    root.addHandler(fh)
    try:
        # Count matching file handlers before
        target = str(log_path.resolve())

        def _count_matching_handlers():
            return sum(
                1
                for h in root.handlers
                if isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == target
            )

        before = _count_matching_handlers()
        assert before == 1  # our manual handler only

        cfg = {"logging": {"file": str(log_path)}}
        configure_file_logging(cfg, logging.INFO)

        # Should detect duplicate and not add another handler
        after = _count_matching_handlers()
        assert after == before
    finally:
        root.removeHandler(fh)
        fh.close()


def test_configure_file_logging_swallows_filehandler_error(monkeypatch, tmp_path: Path):
    # Patch FileHandler to raise to exercise best-effort exception path
    def boom(*_a, **_k):
        raise OSError("cannot open file")

    # Preserve original type for isinstance checks below, then patch
    OrigFileHandler = logging.FileHandler
    # Patch logging.FileHandler globally; pytest logging plugin doesn't use FileHandler
    monkeypatch.setattr(logging, "FileHandler", boom)

    root = logging.getLogger()

    # Count FileHandler instances before and after; should be unchanged due to error
    def _count_file_handlers():
        return sum(1 for h in root.handlers if isinstance(h, OrigFileHandler))

    before = _count_file_handlers()
    cfg = {"logging": {"file": str(tmp_path / "x.log")}}
    # Should not raise despite FileHandler failure
    configure_file_logging(cfg, logging.INFO)
    after = _count_file_handlers()
    assert after == before

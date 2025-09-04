from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pmcc.main as main_mod

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


class _BadLogLevel:
    def upper(self) -> str:  # type: ignore[override]
        raise RuntimeError("boom")


def test_main_log_level_upper_exception_path(monkeypatch):
    # Use env for config-dir to avoid relying on CLI parsing
    monkeypatch.setenv("PMCC_CONFIG_DIR", str(CONFIG_DIR))

    # Return a crafted args namespace that triggers log-level fallback
    def _fake_parse_args(self):  # type: ignore[no-untyped-def]
        return SimpleNamespace(
            version=False,
            config_dir=str(CONFIG_DIR),
            dry_risk=False,
            dry_exec=False,
            dry_monitor=False,
            dry_run=False,
            summary_json=False,
            summary_json_out=None,
            validate_schema=False,
            schemas_dir=None,
            log_level=_BadLogLevel(),  # triggers args.log_level.upper() exception
            live=False,
            redistribute_leftover=False,
            min_total_weight=None,
        )

    monkeypatch.setattr(main_mod.argparse.ArgumentParser, "parse_args", _fake_parse_args, raising=True)

    # Run main and ensure it exits successfully (SystemExit with code 0)
    try:
        main_mod.main()
    except SystemExit as e:  # pragma: no cover - control flow check
        assert e.code == 0

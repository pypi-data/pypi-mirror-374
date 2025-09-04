from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pmcc.main as main_mod


def _copy_config(tmp_path: Path) -> Path:
    proj_root = Path(__file__).resolve().parents[1]
    cfg_src = proj_root / "config"
    cfg_dst = tmp_path / "config_copy"
    cfg_dst.mkdir()
    for p in cfg_src.glob("*.json"):
        (cfg_dst / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    return cfg_dst


def test_main_dry_run_inprocess_succeeds(tmp_path: Path, monkeypatch):
    cfg = _copy_config(tmp_path)
    # Redirect logging file to tmp to avoid touching repo logs
    sys_path = cfg / "system.json"
    system = json.loads(sys_path.read_text(encoding="utf-8"))
    system["logging"]["file"] = str(tmp_path / "logs" / "app.log")
    sys_path.write_text(json.dumps(system, ensure_ascii=False, indent=2), encoding="utf-8")

    argv = [
        "pmcc",
        "--config-dir",
        str(cfg),
        "--dry-run",
        "--summary-json",
        "--log-level",
        "INFO",
    ]
    monkeypatch.setattr(sys, "argv", argv, raising=False)

    try:
        main_mod.main()
    except SystemExit as e:
        assert e.code == 0

    # file logging should have created the file
    log_file = tmp_path / "logs" / "app.log"
    assert log_file.exists()


def test_configure_file_logging_attr_error_branch(tmp_path: Path, monkeypatch):
    # Build a handler type that raises on baseFilename access and is used as FileHandler
    class DummyFH:
        def __init__(self, *args, **kwargs):
            pass

        def setLevel(self, level):
            pass

        def setFormatter(self, formatter):
            pass

        def __getattr__(self, name: str):
            if name == "baseFilename":
                raise RuntimeError("boom")
            raise AttributeError(name)

    # Replace logging.FileHandler and inject a dummy handler to root
    monkeypatch.setattr(logging, "FileHandler", DummyFH)
    root = logging.getLogger()
    prev_handlers = list(root.handlers)
    root.handlers = [DummyFH()]

    system_cfg = {"logging": {"file": str(tmp_path / "f.log")}}
    # Should not raise even though attribute access errors occur
    main_mod.configure_file_logging(system_cfg, logging.INFO)
    # restore handlers to avoid leaking dummy handler into other tests
    root.handlers = prev_handlers


def test_main_assertion_exit_code_on_invalid_universe(tmp_path: Path, monkeypatch):
    cfg = _copy_config(tmp_path)
    # Make universe tickers empty to trigger AssertionError in validate()
    uni_path = cfg / "universe_etf_20.json"
    uni = json.loads(uni_path.read_text(encoding="utf-8"))
    uni["tickers"] = []
    uni_path.write_text(json.dumps(uni, ensure_ascii=False, indent=2), encoding="utf-8")

    argv = [
        "pmcc",
        "--config-dir",
        str(cfg),
        "--log-level",
        "INFO",
    ]
    monkeypatch.setattr(sys, "argv", argv, raising=False)

    try:
        main_mod.main()
        assert False, "should exit with code 3"
    except SystemExit as e:
        assert e.code == 3


def test_main_summary_json_out_io_error_exit1(tmp_path: Path, monkeypatch):
    cfg = _copy_config(tmp_path)
    # Ensure file logging writes to tmp (avoid external paths)
    sys_path = cfg / "system.json"
    system = json.loads(sys_path.read_text(encoding="utf-8"))
    system["logging"]["file"] = str(tmp_path / "logs" / "app.log")
    sys_path.write_text(json.dumps(system, ensure_ascii=False, indent=2), encoding="utf-8")

    out_file = tmp_path / "out" / "summary.json"

    # Monkeypatch Path.open to raise when writing the summary out file to trigger generic Exception path
    import pmcc.main as main_mod

    real_open = main_mod.Path.open

    def fake_open(self: Path, *args, **kwargs):  # type: ignore[override]
        if str(self) == str(out_file):
            raise OSError("write failed")
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(main_mod.Path, "open", fake_open)

    argv = [
        "pmcc",
        "--config-dir",
        str(cfg),
        "--summary-json",
        "--summary-json-out",
        str(out_file),
    ]
    monkeypatch.setattr(sys, "argv", argv, raising=False)

    try:
        main_mod.main()
        assert False, "should exit with code 1"
    except SystemExit as e:
        assert e.code == 1


def test_main_approval_report_path_resolve_error_inprocess(tmp_path: Path, monkeypatch, capsys):
    # Copy config and point logging to tmp
    cfg = _copy_config(tmp_path)
    sys_path = cfg / "system.json"
    system = json.loads(sys_path.read_text(encoding="utf-8"))
    system["logging"]["file"] = str(tmp_path / "logs" / "app.log")
    sys_path.write_text(json.dumps(system, ensure_ascii=False, indent=2), encoding="utf-8")

    import pmcc.main as main_mod

    # Monkeypatch Path.resolve inside pmcc.main to raise only for the approval log path,
    # so config_dir resolution remains unaffected.
    real_resolve = main_mod.Path.resolve

    logp = tmp_path / "appr.log"

    def bad_resolve(self: Path):  # type: ignore[override]
        if str(self) == str(logp):
            raise OSError("cannot resolve")
        return real_resolve(self)

    monkeypatch.setattr(main_mod.Path, "resolve", bad_resolve, raising=False)

    argv = [
        "pmcc",
        "--config-dir",
        str(cfg),
        "--summary-json",
        "--require-approval",
    ]
    monkeypatch.setattr(sys, "argv", argv, raising=False)
    monkeypatch.setenv("PMCC_APPROVAL_LOG", str(logp))

    try:
        main_mod.main()
    except SystemExit as e:
        assert e.code == 0

    out = capsys.readouterr().out
    lines = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("{") and ln.strip().endswith("}")]
    data = json.loads(lines[-1])
    appr = data.get("approval", {})
    assert appr.get("required") is True
    # report_path should be the raw env string when resolve() fails
    assert appr.get("report_path") == str(logp)


def test_main_approval_outer_except_with_report_path_resolve_error(tmp_path: Path, monkeypatch, capsys):
    # Copy config and set logging
    cfg = _copy_config(tmp_path)
    sys_path = cfg / "system.json"
    system = json.loads(sys_path.read_text(encoding="utf-8"))
    system["logging"]["file"] = str(tmp_path / "logs" / "app.log")
    sys_path.write_text(json.dumps(system, ensure_ascii=False, indent=2), encoding="utf-8")

    import pmcc.approval as appr_mod
    import pmcc.main as main_mod

    logp = tmp_path / "appr2.log"

    # Patch Path.resolve to raise for this log path only
    real_resolve = main_mod.Path.resolve

    def bad_resolve(self: Path):  # type: ignore[override]
        if str(self) == str(logp):
            raise OSError("cannot resolve 2")
        return real_resolve(self)

    monkeypatch.setattr(main_mod.Path, "resolve", bad_resolve, raising=False)

    # Force outer except by making ApprovalFileService.request raise
    def boom(self, req):  # noqa: D401 - stub
        raise RuntimeError("request failed")

    monkeypatch.setattr(appr_mod.ApprovalFileService, "request", boom)

    argv = [
        "pmcc",
        "--config-dir",
        str(cfg),
        "--summary-json",
        "--require-approval",
    ]
    monkeypatch.setattr(sys, "argv", argv, raising=False)
    monkeypatch.setenv("PMCC_APPROVAL_LOG", str(logp))

    try:
        main_mod.main()
    except SystemExit as e:
        assert e.code == 0

    out = capsys.readouterr().out
    lines = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("{") and ln.strip().endswith("}")]
    data = json.loads(lines[-1])
    appr = data.get("approval", {})
    # Outer except path marks error=True and sets raw report_path when resolve fails
    assert appr.get("required") is True and appr.get("approved") is False and appr.get("error") is True
    assert appr.get("report_path") == str(logp)

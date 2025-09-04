from __future__ import annotations

from pathlib import Path

from pmcc.integration import run_cli_summary, validate_summary_with_schema


def test_integration_run_and_validate_summary():
    proj = Path(__file__).resolve().parents[1]
    cfg_dir = proj / "config"
    summary = run_cli_summary(str(cfg_dir))
    assert isinstance(summary, dict)
    # minimal key presence
    assert "universe" in summary and "risk" in summary and "events" in summary
    # optional schema validation if available
    validate_summary_with_schema(summary, proj / "schemas" / "summary.json")


def test_integration_with_approval_and_outfile(tmp_path: Path):
    proj = Path(__file__).resolve().parents[1]
    cfg_dir = proj / "config"
    out_file = tmp_path / "summary.json"
    log_file = tmp_path / "appr.jsonl"
    summary = run_cli_summary(
        str(cfg_dir),
        require_approval=True,
        summary_out=str(out_file),
        env_overrides={"PMCC_APPROVAL_LOG": str(log_file)},
    )
    assert isinstance(summary, dict)
    assert out_file.exists()
    # approval block present
    appr = summary.get("approval", {})
    assert isinstance(appr, dict) and appr.get("required") is True
    # file got written
    assert log_file.exists()


def test_integration_live_and_extra_args():
    proj = Path(__file__).resolve().parents[1]
    cfg_dir = proj / "config"
    # live flag doesn't perform trading; just exercises CLI flag path
    summary = run_cli_summary(str(cfg_dir), live=True, extra_args=["--log-level", "INFO"])
    assert isinstance(summary, dict) and summary.get("ibkr", {}).get("mode") in {"live", "paper"}


def test_integration_invalid_config_raises(tmp_path: Path):
    bad_dir = tmp_path / "nope"
    try:
        run_cli_summary(str(bad_dir))
        assert False, "should raise"
    except RuntimeError:
        pass


def test_validate_schema_path_missing_noop(tmp_path: Path):
    proj = Path(__file__).resolve().parents[1]
    cfg_dir = proj / "config"
    summary = run_cli_summary(str(cfg_dir))
    # pass a non-existing schema path → no exception
    validate_summary_with_schema(summary, tmp_path / "no_schema.json")

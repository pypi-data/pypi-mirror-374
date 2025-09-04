from __future__ import annotations

import json
import os
import subprocess  # nosec B404 - controlled subprocess to call our own CLI
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def _parse_last_json_line(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.strip().splitlines()):
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            return json.loads(s)
    raise RuntimeError("No JSON summary found in stdout")  # pragma: no cover - defensive


def run_cli_summary(
    config_dir: str | Path,
    *,
    require_approval: bool = False,
    live: bool = False,
    summary_out: str | Path | None = None,
    extra_args: list[str] | None = None,
    env_overrides: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run the pmcc CLI to obtain the summary JSON and return it as a dict.

    This wrapper isolates environment and parsing details for integrations.
    """
    args = [
        sys.executable,
        "-m",
        "pmcc",
        "--config-dir",
        str(Path(config_dir)),
        "--summary-json",
    ]
    if require_approval:
        args.append("--require-approval")
    if live:
        args.append("--live")
    if summary_out is not None:
        args += ["--summary-json-out", str(Path(summary_out))]
    if extra_args:
        args += list(extra_args)

    env = os.environ.copy()
    # keep CLI output deterministic for parsers and stable in CI
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    # Allow consumer to override or inject approval path, etc.
    if env_overrides:
        env.update({str(k): str(v) for k, v in env_overrides.items()})

    p = subprocess.run(args, capture_output=True, text=True, env=env)  # nosec B603 - no shell, controlled argv
    if p.returncode != 0:
        raise RuntimeError(f"pmcc CLI failed: code={p.returncode}\n{p.stdout}\n{p.stderr}")
    return _parse_last_json_line(p.stdout)


def validate_summary_with_schema(summary: Mapping[str, Any], schema_path: str | Path | None = None) -> None:
    """Validate the summary dict with JSON Schema if available.

    Raises jsonschema.ValidationError / jsonschema.SchemaError on failure.
    If jsonschema is not installed or schema missing, this function is a no-op.
    """
    try:
        import jsonschema
    except Exception:  # pragma: no cover - optional dependency not installed
        return
    path = Path(schema_path) if schema_path else Path("schemas") / "summary.json"
    if not path.exists():
        return
    schema_obj = json.loads(Path(path).read_text(encoding="utf-8"))
    jsonschema.validate(instance=summary, schema=schema_obj)

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def run_cli(args, env_extra: dict[str, str] | None = None):
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "pmcc", "--config-dir", str(CONFIG_DIR), *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def extract_last_json(stdout: str):
    for line in reversed(stdout.strip().splitlines()):
        s = line.strip()
        if s.startswith("{") and s.endswith("}"):
            import json

            return json.loads(s)
    raise AssertionError("未找到 JSON")


def test_cli_approval_http_url_inprocess(monkeypatch, capsys):
    # fake requests.post
    class Resp:
        status_code = 200

        def json(self):  # noqa: D401 - test stub
            return {"approved": True, "approver": "http"}

    def post(_url, **_kwargs):
        return Resp()

    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=post))

    import pmcc.main as main_mod

    argv = [
        "pmcc",
        "--config-dir",
        str(CONFIG_DIR),
        "--summary-json",
        "--require-approval",
    ]
    monkeypatch.setenv("PMCC_APPROVAL_HTTP_URL", "http://example/approve")
    monkeypatch.setattr(sys, "argv", argv, raising=False)
    try:
        main_mod.main()
    except SystemExit as e:
        assert e.code == 0
    out = capsys.readouterr().out
    data = extract_last_json(out)
    appr = data.get("approval", {})
    assert appr.get("required") is True and appr.get("approved") is True

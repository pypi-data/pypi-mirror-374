import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def have_jsonschema():
    try:
        import jsonschema  # noqa: F401

        return True
    except Exception:
        return False


@pytest.mark.skipif(not have_jsonschema(), reason="jsonschema 未安装，跳过集成测试")
class TestJsonSchemaIntegration:
    def run_cli(self, args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        return subprocess.run(
            [sys.executable, "-m", "pmcc", "--config-dir", str(CONFIG_DIR), *args],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            env=env,
        )

    def test_schemas_dir_override_fail(self, tmp_path: Path):
        # 定义一个更严格的 schema：限制 system.cpu_cap ≤ 0.2，从而使当前配置(0.3)失败
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()
        schema_system = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"cpu_cap": {"type": "number", "maximum": 0.2}},
            "required": ["cpu_cap"],
            "additionalProperties": True,
        }
        (schemas_dir / "system.json").write_text(json.dumps(schema_system), encoding="utf-8")

        r = self.run_cli(["--validate-schema", "--schemas-dir", str(schemas_dir)])
        assert r.returncode != 0
        combined = (r.stdout + "\n" + r.stderr).lower()
        assert "schema" in combined

    def test_schemas_dir_override_ok(self, tmp_path: Path):
        # 宽松 schema：system.cpu_cap 为 number 即可，当前配置(0.3)应通过
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()
        schema_system = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"cpu_cap": {"type": "number"}},
            "required": ["cpu_cap"],
            "additionalProperties": True,
        }
        (schemas_dir / "system.json").write_text(json.dumps(schema_system), encoding="utf-8")

        r = self.run_cli(["--validate-schema", "--schemas-dir", str(schemas_dir)])
        assert r.returncode == 0, r.stdout + "\n" + r.stderr

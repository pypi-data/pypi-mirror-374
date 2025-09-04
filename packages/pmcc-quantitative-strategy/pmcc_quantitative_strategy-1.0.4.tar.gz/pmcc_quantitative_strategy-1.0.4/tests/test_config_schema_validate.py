import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"


# 配置文件名到 schema 文件名的一般映射（同名）。
# 对于没有对应 schema 的配置（如 keys_example.json），在测试中将自动跳过。


def iter_config_and_schema_paths():
    for cfg_path in sorted(CONFIG_DIR.glob("*.json")):
        schema_path = SCHEMAS_DIR / cfg_path.name
        if not schema_path.exists():
            # 无对应 schema，跳过（例如密钥示例文件）
            continue
        yield cfg_path, schema_path


@pytest.mark.parametrize("cfg_path,schema_path", list(iter_config_and_schema_paths()))
def test_config_files_conform_to_schema(cfg_path: Path, schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(data)


def test_risk_policy_negative_missing_required() -> None:
    # 构造一个缺少 cushion.hard_floor 的不合法对象，应当校验失败。
    schema_path = SCHEMAS_DIR / "risk_policy.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    invalid_cfg = {
        "cushion": {
            # 缺少 "hard_floor"
            "target_range": [0.1, 0.3],
        }
    }

    with pytest.raises(Exception):
        Draft202012Validator(schema).validate(invalid_cfg)

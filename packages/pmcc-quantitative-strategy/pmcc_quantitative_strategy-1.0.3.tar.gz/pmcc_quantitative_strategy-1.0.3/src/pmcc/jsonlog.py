from __future__ import annotations

import json
import logging
import time
from typing import Any


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit a single JSON line to the provided logger.

    - Includes `ts` (epoch seconds) and `event`.
    - Best-effort serialization：不可序列化对象使用 repr() 回退。
    - 不改变现有文本日志路径；仅在调用处使用。
    """

    def _safe(v: Any) -> Any:
        try:
            json.dumps(v)
            return v
        except Exception:
            return repr(v)

    obj: dict[str, Any] = {"ts": int(time.time()), "event": str(event)}
    obj.update({k: _safe(v) for k, v in fields.items()})
    logger.info(json.dumps(obj, ensure_ascii=False))

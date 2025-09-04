from __future__ import annotations

import os
from typing import Any


def notify(event: str, detail: dict[str, Any] | None = None) -> bool:
    """Send a JSON webhook when PMCC_ALERT_WEBHOOK is set.

    - Non-blocking best-effort; returns True when POST returns 2xx; else False。
    - Avoids hard dependency by importing requests via importlib; if missing, returns False。
    - Payload: {event: str, detail: object}
    """
    url = os.environ.get("PMCC_ALERT_WEBHOOK")
    if not url:
        return False
    payload = {"event": str(event), "detail": detail or {}}
    try:
        import importlib

        rq = importlib.import_module("requests")
        r = rq.post(url, json=payload, timeout=3.0)
        return 200 <= int(getattr(r, "status_code", 0)) < 300
    except Exception:
        return False

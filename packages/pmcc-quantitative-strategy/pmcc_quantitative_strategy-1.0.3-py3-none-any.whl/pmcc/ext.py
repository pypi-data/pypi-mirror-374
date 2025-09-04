from __future__ import annotations

from typing import Any


def with_ibkr_extensions(
    cfgs: dict[str, Any], *, counters: dict[str, int] | None = None, health: str | None = None
) -> dict[str, Any]:
    """Return a shallow-copied cfgs with __extensions__ injected for summarize().

    This does not perform any I/O. Callers can pass counters/health derived from
    in-memory services (e.g., adapters) to be reflected in execution summaries.
    """
    base = dict(cfgs)
    ext = dict(base.get("__extensions__", {}))
    if counters is not None and isinstance(counters, dict):
        ext["ibkr_counters"] = {"success": int(counters.get("success", 0)), "error": int(counters.get("error", 0))}
    if health is not None:
        ext["ibkr_health"] = str(health)
    base["__extensions__"] = ext
    return base

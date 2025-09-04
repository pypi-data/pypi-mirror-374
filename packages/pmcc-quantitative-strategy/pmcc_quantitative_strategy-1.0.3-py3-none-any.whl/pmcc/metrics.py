from __future__ import annotations

from collections import defaultdict

_total_success = 0
_total_error = 0
_by_kind: dict[str, dict[str, int]] = defaultdict(lambda: {"success": 0, "error": 0})


def inc_success(kind: str | None = None) -> None:
    global _total_success
    _total_success += 1
    if kind:
        _by_kind[kind]["success"] += 1


def inc_error(kind: str | None = None) -> None:
    global _total_error
    _total_error += 1
    if kind:
        _by_kind[kind]["error"] += 1


def get_counters() -> dict[str, int]:
    return {"success": int(_total_success), "error": int(_total_error)}


def get_counters_by_kind() -> dict[str, dict[str, int]]:
    return {k: {"success": v["success"], "error": v["error"]} for k, v in _by_kind.items()}


def reset() -> None:
    global _total_success, _total_error, _by_kind
    _total_success = 0
    _total_error = 0
    _by_kind = defaultdict(lambda: {"success": 0, "error": 0})

from __future__ import annotations


def derive_health(counters: dict[str, int] | None, thresholds: dict[str, float | int] | None) -> str:
    if not isinstance(counters, dict) or not isinstance(thresholds, dict):
        return "ok"
    succ = int(counters.get("success", 0))
    err = int(counters.get("error", 0))
    total = succ + err
    warn_rate = float(thresholds.get("warn_error_rate", 0.05))
    block_rate = float(thresholds.get("block_error_rate", 0.2))
    block_burst = int(thresholds.get("block_burst", 5))
    if err >= block_burst:
        return "blocked"
    if total > 0:
        rate = err / float(total)
        if rate >= block_rate:
            return "blocked"
        if rate > warn_rate:
            return "warn"
    return "ok"

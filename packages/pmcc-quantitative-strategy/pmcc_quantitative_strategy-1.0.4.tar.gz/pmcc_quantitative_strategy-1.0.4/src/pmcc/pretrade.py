from __future__ import annotations

from typing import Any

from pmcc.contracts import APIResult, PretradeResult
from pmcc.providers import PretradeChecks as _PretradeChecks


def run_pretrade_checks(cfgs: dict[str, Any]) -> APIResult[PretradeResult]:
    reasons: list[str] = []
    # Kill switch via environment or config-derived health
    import os

    kill = str(os.environ.get("PMCC_KILL_SWITCH", "0")).strip().lower() in {"1", "true", "yes", "on", "y"}
    if kill:
        reasons.append("kill_switch_active")
    events = cfgs.get("event_filters.json", {})
    macro = events.get("macro", {}) if isinstance(events, dict) else {}
    if str(macro.get("default_action", "")).strip().lower() == "freeze":
        reasons.append("macro_freeze")

    ok = not reasons
    return APIResult(ok=True, data=PretradeResult(ok=ok, reasons=reasons, details={}))


class DefaultPretradeChecks(_PretradeChecks):
    """Protocol-compatible pretrade checks implementation.

    Mirrors run_pretrade_checks() to keep backward compatibility while enabling
    typed injection via providers.PretradeChecks.
    """

    def run(self, cfgs: dict, context: dict) -> APIResult[PretradeResult]:
        _ = context  # reserved for future use
        return run_pretrade_checks(cfgs)

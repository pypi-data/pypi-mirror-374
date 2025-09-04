"""Monitoring module (stub) for PMCC prototype.

Simulates a daily evaluation loop in dry-run mode. No trades are placed.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("pmcc.monitor")


def dry_run(cfgs: dict[str, Any]) -> None:
    """Log a placeholder monitoring step using config hints only."""
    system = cfgs.get("system.json", {})
    events = cfgs.get("event_filters.json", {})
    modes = cfgs.get("rolling_modes.json", {})

    logger.debug("[MON][DEBUG] 进入监控循环 dry_run()")
    logger.info("[MON] 启动监控循环干跑（占位版，无真实盘）…")
    logger.info(f"[MON] 系统并发：{system.get('concurrency')}，CPU上限：{system.get('cpu_cap')}")
    logger.info(
        f"[MON] 事件窗口（宏观）：默认动作={events.get('macro', {}).get('default_action')}，"
        f"窗口±{events.get('macro', {}).get('window_days')}天"
    )
    logger.info(f"[MON] 滚动模式：{modes.get('active_mode')}（最小变更原则，未来将基于持仓与风险评估做轻量调整）")
    logger.info("[MON] 今日评估：未检测到需要强制调整的配置层风险；建议保持或小幅调整（示例）。")
    logger.info("[MON] 监控循环干跑完成（仅打印，不做任何变更）。")


def summarize(cfgs: dict[str, Any]) -> dict[str, Any]:
    """Return a structured monitoring summary (dry-run context).

    Includes the core knobs relevant for a monitoring cycle; no I/O.
    """
    system = cfgs.get("system.json", {})
    events = cfgs.get("event_filters.json", {})
    modes = cfgs.get("rolling_modes.json", {})
    risk = cfgs.get("risk_policy.json", {})
    portfolio = cfgs.get("portfolio_allocation.json", {})
    uni = cfgs.get("universe_etf_20.json", {})
    # derive status from cushion relation check
    cushion_ok = False
    if isinstance(risk.get("cushion"), dict):
        try:
            hf = float(risk.get("cushion", {}).get("hard_floor"))
            tr0 = float(risk.get("cushion", {}).get("target_range", [0, 0])[0])
            cushion_ok = hf <= tr0
        except Exception:
            cushion_ok = False
    # compute safe cushion relation for checks
    cushion_rel_ok = False
    if isinstance(risk.get("cushion"), dict):
        try:
            hf2 = float(risk.get("cushion", {}).get("hard_floor"))
            tr02 = float(risk.get("cushion", {}).get("target_range", [0, 0])[0])
            cushion_rel_ok = hf2 <= tr02
        except Exception:
            cushion_rel_ok = False

    # fields & alerts (non-breaking helpers)
    fields_present = {
        "has_macro": isinstance(events.get("macro"), dict),
        "has_cushion": isinstance(risk.get("cushion"), dict),
        "has_correlation": isinstance(risk.get("correlation_control"), dict),
    }
    alerts: list[str] = []
    failed_checks = 0
    if not cushion_rel_ok:
        alerts.append("cushion_floor_above_target_low")
        failed_checks += 1

    return {
        "system": {
            "concurrency": system.get("concurrency"),
            "cpu_cap": system.get("cpu_cap"),
        },
        "events": {"macro": events.get("macro", {})},
        "rolling_mode": modes.get("active_mode"),
        "universe": {"count": len(uni.get("tickers", []))},
        "risk": {
            "cushion": risk.get("cushion", {}),
            "correlation": risk.get("correlation_control", {}),
            "drawdown": risk.get("drawdown_guard", {}),
        },
        "portfolio": {
            "min_total_weight": portfolio.get("min_total_weight"),
            "rebalance_triggers": portfolio.get("rebalance_triggers", {}),
        },
        "checks": {
            "cushion_floor_lt_target_low": cushion_rel_ok,
            "underweight_threshold": portfolio.get("min_total_weight"),
            "max_pairwise": risk.get("correlation_control", {}).get("max_pairwise"),
        },
        "events_priority": events.get("macro", {}).get("priority"),
        "suggestions": [
            "monitor cushion vs target band",
            "review correlation pairs above threshold",
            "rebalance if total weight < threshold",
        ],
        "suggestions_labeled": [
            {
                "text": "monitor cushion vs target band",
                "level": "warn" if not cushion_ok else "info",
            },
            {"text": "review correlation pairs above threshold", "level": "info"},
            {"text": "rebalance if total weight < threshold", "level": "info"},
        ],
        "alerts": alerts,
        "checks_failed": failed_checks,
        "fields_present": fields_present,
        "contract": {"name": "monitor_summary", "version": "1"},
        "status": "ok" if cushion_ok else "warn",
    }

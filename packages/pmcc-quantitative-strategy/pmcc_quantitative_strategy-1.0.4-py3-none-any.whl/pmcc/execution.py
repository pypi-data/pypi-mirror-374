"""Execution module (stub) for PMCC prototype.

Generates dry-run execution planning messages. No real orders are sent.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("pmcc.execution")


def dry_run(cfgs: dict[str, Any]) -> None:
    """Log a placeholder execution plan using config hints only."""
    modes = cfgs.get("rolling_modes.json", {})
    events = cfgs.get("event_filters.json", {})
    ds = cfgs.get("data_sources.json", {})
    active = modes.get("active_mode")
    active_cfg = modes.get(active, {}) if isinstance(active, str) else {}

    logger.debug("[EXEC][DEBUG] 进入执行规划 dry_run()")
    logger.info("[EXEC] 开始干跑执行规划（占位版，无真实盘）…")
    logger.info(
        f"[EXEC] 数据源（主）：market={ds.get('primary', {}).get('market_data')}, "
        f"options={ds.get('primary', {}).get('options_data')}"
    )
    logger.info(f"[EXEC] 当前滚动模式：{active} → {active_cfg}")
    logger.info(
        f"[EXEC] 事件窗口策略（宏观）：默认动作={events.get('macro', {}).get('default_action')}, "
        f"窗口±{events.get('macro', {}).get('window_days')}天"
    )
    logger.info("[EXEC] 订单模板（规划）：IBKR Combo + Mid/Adaptive（未来接入），含价差/滑点前置检查。")
    logger.info("[EXEC] 执行规划干跑完成（仅打印，不下单）。")


def summarize(cfgs: dict[str, Any]) -> dict[str, Any]:
    """Return a structured summary for execution planning (dry-run context).

    The summary is deterministic given the provided cfgs and does not trigger
    any I/O. It is intended for tests and integrations that prefer structured
    data over log parsing.
    """
    modes = cfgs.get("rolling_modes.json", {})
    events = cfgs.get("event_filters.json", {})
    ds = cfgs.get("data_sources.json", {})
    risk = cfgs.get("risk_policy.json", {})
    active = modes.get("active_mode")
    mode_cfg = modes.get(active, {}) if isinstance(active, str) else {}
    uni = cfgs.get("universe_etf_20.json", {})
    # collect auxiliary non-breaking fields
    inputs = sorted(list(cfgs.keys()))
    warnings: list[str] = []

    if not isinstance(ds.get("throttle"), dict):
        warnings.append("missing_throttle")
    # keep warnings available for future non-breaking diagnostics

    # optional extensions injection (pure-path, from cfgs only)
    ext = cfgs.get("__extensions__", {}) if isinstance(cfgs, dict) else {}
    injected_counters = ext.get("ibkr_counters") if isinstance(ext, dict) else None
    injected_health = ext.get("ibkr_health") if isinstance(ext, dict) else None
    health_thresholds = ext.get("health_thresholds") if isinstance(ext, dict) else None

    from pmcc.health import derive_health as __derive

    def __derive_health(
        ds: dict[str, Any],
        counters: dict[str, int] | None,
        thresholds: dict[str, float | int] | None,
    ) -> str:
        # if thresholds provided, compute derived health; else ok
        try:
            return __derive(counters, thresholds)
        except Exception:
            return "ok"

    return {
        "rolling_mode": active,
        "data_sources": {"primary": ds.get("primary", {}), "throttle": ds.get("throttle", {})},
        "events": {"macro": events.get("macro", {})},
        "events_policy": {
            "throttle_coeff": events.get("macro", {}).get("throttle_coeff"),
            "delta_shift": events.get("macro", {}).get("delta_shift"),
        },
        "mode_config": {
            "short_call": mode_cfg.get("short_call", {}),
            "events_adjustment": mode_cfg.get("events_adjustment", {}),
            "general": modes.get("general", {}),
        },
        "plan": {
            "order_template": "IBKR Combo + Mid/Adaptive",
            "pre_checks": ["spread", "slippage", "margin"],
            "pre_checks_verbose": [
                "spread: max_spread_ratio in filters",
                "slippage: compare to throttle",
                "margin: ensure cushion above floor",
            ],
            "pre_checks_detail": [
                {
                    "name": "spread",
                    "description": ("Use filters.max_spread_ratio " "to guard quotes."),
                    "applies": True,
                },
                {
                    "name": "slippage",
                    "description": ("Adjust quotes vs throttle to mitigate slippage."),
                    "applies": True,
                },
                {
                    "name": "margin",
                    "description": ("Ensure cushion is above hard_floor before planning."),
                    "applies": True,
                },
            ],
        },
        "constraints": {
            "position_limits": risk.get("position_limits", {}),
            "correlation_control": risk.get("correlation_control", {}),
        },
        "hints": {
            "has_short_call": isinstance(mode_cfg.get("short_call"), dict),
            "has_events_adjustment": isinstance(mode_cfg.get("events_adjustment"), dict),
            "has_general": isinstance(modes.get("general"), dict),
        },
        "suggestions": [
            "validate pre_checks: spread/slippage/margin",
            "review throttle settings for batch planning",
        ],
        "suggestions_labeled": [
            {"text": "validate pre_checks: spread/slippage/margin", "level": "info"},
            {"text": "review throttle settings for batch planning", "level": "info"},
        ],
        "status": "ok",
        "fields_present": {
            "has_primary": isinstance(ds.get("primary"), dict),
            "has_throttle": isinstance(ds.get("throttle"), dict),
            "has_macro": isinstance(events.get("macro"), dict),
        },
        "warnings": warnings,
        "contract": {"name": "exec_plan", "version": "1"},
        "official_events": sorted(list(ds.get("official_events", {}).keys())),
        "notes": ds.get("notes"),
        "universe_count": len(uni.get("tickers", [])),
        "inputs": inputs,
        # Optional non-breaking IBKR extension (config-derived, no I/O)
        "ibkr_ext": {
            "throttle": ds.get("throttle", {}),
            "health": injected_health or __derive_health(ds, injected_counters, health_thresholds),
            "counters": injected_counters if isinstance(injected_counters, dict) else {"success": 0, "error": 0},
        },
    }

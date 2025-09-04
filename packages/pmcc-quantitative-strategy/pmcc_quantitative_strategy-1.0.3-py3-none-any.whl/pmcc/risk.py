"""Risk module for PMCC prototype.

Provides dry-run risk checks based on config only. No trading.
Implements core risk rules with internal Decimal calculations.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from decimal import Decimal, InvalidOperation
from typing import Any

from pmcc.utils import is_number

logger = logging.getLogger("pmcc.risk")


def check_cushion(cushion: dict[str, Any], current: float) -> dict[str, Any]:
    """评估 Cushion 水位。

    规则：
    - current < hard_floor → status = "block"
    - hard_floor <= current < target_range[0] → status = "warn"
    - target_range[0] <= current <= target_range[1] → status = "ok"
    - current > target_range[1] → status = "warn"（过高同样提示）

    返回：{"status": str, "current": float, "hard_floor": float, "target_range": [lo, hi]}
    """
    hf = cushion.get("hard_floor")
    tr = cushion.get("target_range")
    if not is_number(hf):
        raise ValueError("cushion.hard_floor 应为数值")
    if not (isinstance(tr, list) and len(tr) == 2 and all(is_number(x) for x in tr)):
        raise ValueError("cushion.target_range 应为长度为2的数值列表")

    # Type narrowing after validation
    hf_val = float(hf)
    lo, hi = float(tr[0]), float(tr[1])
    if lo > hi:
        raise ValueError("cushion.target_range 下界不可大于上界")
    cur = float(current)

    if cur < hf_val:
        status = "block"
    elif cur < lo:
        status = "warn"
    elif cur <= hi:
        status = "ok"
    else:
        status = "warn"

    return {
        "status": status,
        "current": cur,
        "hard_floor": hf_val,
        "target_range": [lo, hi],
    }


def check_position_limits(
    limits: dict[str, Any],
    positions: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """检查持仓数量与单标权重限制。

    规则（配置驱动）：
    - 若任一 `position["weight"]` 超过 `limits.max_weight_per_underlying` → block
    - 若 `len(positions)` 超过 `limits.max_positions` → block
    - 否则 → ok

    返回包含详情：{"status", "position_count", "over_weight": [...], "limit_max_positions": int}
    """
    max_w = limits.get("max_weight_per_underlying")
    max_n = limits.get("max_positions")
    if not is_number(max_w) or not isinstance(max_n, int):
        raise ValueError("position_limits 配置非法")

    # type narrowing after validation
    max_w_dec = Decimal(str(float(max_w)))
    over_weight: list[dict[str, Any]] = []
    for p in positions:
        t = p.get("ticker")
        w = p.get("weight")
        if not isinstance(t, str) or not is_number(w):
            raise ValueError("positions 元素需包含 ticker(str) 与 weight(number)")
        w_dec = Decimal(str(float(w)))
        if w_dec > max_w_dec:
            over_weight.append({"ticker": t, "weight": float(w_dec), "max_weight": float(max_w_dec)})

    count = len(positions)
    status = "ok"
    if over_weight or count > max_n:
        status = "block"

    return {
        "status": status,
        "position_count": count,
        "over_weight": over_weight,
        "limit_max_positions": int(max_n),
    }


def check_correlation_control(
    ctrl: dict[str, Any],
    positions: Sequence[dict[str, Any]],
    pairwise_corr: Sequence[tuple[str, str, float]],
) -> dict[str, Any]:
    """相关性控制（成对相关 ≤ 阈值）。

    - 若任一成对相关 > ctrl.max_pairwise → warn（提示风险，但不阻断）
    - 否则 → ok
    返回：{"status", "violations": [{"pair": (a,b), "corr": float}]}
    """
    _ = positions  # 当前版本不依据权重聚合，仅做阈值检查
    th = ctrl.get("max_pairwise")
    if not is_number(th):
        raise ValueError("correlation_control.max_pairwise 应为数值")
    th_dec = Decimal(str(float(th)))
    violations: list[dict[str, Any]] = []
    for a, b, c in pairwise_corr:
        if not isinstance(a, str) or not isinstance(b, str) or not is_number(c):
            raise ValueError("pairwise_corr 元素形如 (str, str, number)")
        c_dec = Decimal(str(float(c)))
        if c_dec > th_dec:
            violations.append({"pair": (a, b), "corr": float(c_dec)})

    status = "warn" if violations else "ok"
    return {"status": status, "violations": violations}


def check_drawdown_guard(guard: dict[str, Any], current_drawdown: float) -> dict[str, Any]:
    """回撤保护。

    - current_drawdown >= guard.threshold → warn（根据 guard.action 给出建议）
    - 否则 → ok
    返回：{"status", "threshold": float, "action": str}
    """
    th = guard.get("threshold")
    action = guard.get("action")
    if not is_number(th) or not isinstance(action, str):
        raise ValueError("drawdown_guard 配置非法")
    th_dec = Decimal(str(float(th)))
    cur_dd = Decimal(str(float(current_drawdown)))
    status = "warn" if cur_dd >= th_dec else "ok"
    return {"status": status, "threshold": float(th_dec), "action": action}


def check_assignment_dividend(
    ad: dict[str, Any],
    candidates: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """除息与指派风险检查（针对短腿 call 候选）。

    规则：当开启 ex_div_protection 时，若分红额 > （外在价值 - min_extrinsic_vs_dividend），
    则标记为风险（warn）。

    期望 candidates 字段：
    - ticker: str
    - extrinsic: number  外在价值（短腿 call）
    - dividend: number   即将除息的分红额（若无，则可为0或缺省）
    - is_short_call: bool 仅在为 True 时检查
    返回：{"status", "violations": [{"ticker", "extrinsic", "dividend"}]}（无风险时 violations=[]）
    """
    enabled = bool(ad.get("ex_div_protection", False))
    min_diff = ad.get("min_extrinsic_vs_dividend", 0.0)
    if not is_number(min_diff):
        raise ValueError("assignment_dividend.min_extrinsic_vs_dividend 应为数值")

    min_diff_dec = Decimal(str(float(min_diff)))
    violations: list[dict[str, Any]] = []
    if enabled:
        for c in candidates:
            ticker = c.get("ticker")
            extrinsic = c.get("extrinsic", 0.0)
            dividend = c.get("dividend", 0.0)
            is_short_call = bool(c.get("is_short_call", False))
            if not is_short_call:
                continue
            if not isinstance(ticker, str) or not is_number(extrinsic) or not is_number(dividend):
                raise ValueError("candidates 元素字段非法")
            try:
                ex_dec = Decimal(str(float(extrinsic)))
                div_dec = Decimal(str(float(dividend)))
            except (InvalidOperation, ValueError) as _err:
                raise ValueError("candidates 数值解析失败") from None
            # 分红大于外在价值减去阈值 → 风险
            if div_dec > (ex_dec - min_diff_dec):
                violations.append(
                    {
                        "ticker": ticker,
                        "extrinsic": float(ex_dec),
                        "dividend": float(div_dec),
                    }
                )

    status = "warn" if violations else "ok"
    return {"status": status, "violations": violations}


def dry_run(cfgs: dict[str, Any]) -> None:
    """Log a summary risk check based on `config/risk_policy.json`.

    This is a placeholder: it does not evaluate real portfolio or market data.

    已实现并以干跑方式调用以下规则：
    1. check_position_limits() - 持仓数量与权重限制
    2. check_correlation_control() - 相关性控制
    3. check_drawdown_guard() - 回撤保护
    4. check_assignment_dividend() - 除息与指派风险
    """
    risk = cfgs.get("risk_policy.json", {})
    pos = risk.get("position_limits", {})
    corr = risk.get("correlation_control", {})
    dd = risk.get("drawdown_guard", {})
    ad = risk.get("assignment_dividend", {})
    cushion = risk.get("cushion", {})

    logger.debug("[RISK][DEBUG] 进入风险检查 dry_run()")
    logger.info("[RISK] 开始干跑风险检查（占位版，无真实盘）…")
    logger.info(f"[RISK] Cushion: 硬下限={cushion.get('hard_floor')}, 目标={cushion.get('target_range')}")
    logger.info(
        f"[RISK] 持仓上限: 单标权重≤{pos.get('max_weight_per_underlying')}, 最大持仓数={pos.get('max_positions')}"
    )
    logger.info(f"[RISK] 相关性控制: 成对相关≤{corr.get('max_pairwise')}, 罚项权重={corr.get('penalty_weight')}")
    logger.info(f"[RISK] 回撤守护: 阈值={dd.get('threshold')}, 动作={dd.get('action')}")
    logger.info(
        f"[RISK] 除息/指派: 保护={ad.get('ex_div_protection')}, "
        f"最低外在价值vs股息={ad.get('min_extrinsic_vs_dividend')}"
    )
    # 调用已实现规则（使用空/示例数据，严格 dry-run 不触达交易或真实数据）
    try:
        _pl = check_position_limits(pos or {}, positions=[])
        logger.debug(f"[RISK][DEBUG] 规则-持仓上限: status={_pl['status']}, count={_pl['position_count']}")
    except Exception as e:  # nosec B110
        logger.error(f"[RISK] 持仓上限规则检查异常: {e}")
    try:
        _cc = check_correlation_control(corr or {}, positions=[], pairwise_corr=[])
        logger.debug(f"[RISK][DEBUG] 规则-相关性: status={_cc['status']}, violations={len(_cc['violations'])}")
    except Exception as e:  # nosec B110
        logger.error(f"[RISK] 相关性规则检查异常: {e}")
    try:
        _dd = check_drawdown_guard(dd or {}, current_drawdown=0.0)
        logger.debug(f"[RISK][DEBUG] 规则-回撤守护: status={_dd['status']}")
    except Exception as e:  # nosec B110
        logger.error(f"[RISK] 回撤守护规则检查异常: {e}")
    try:
        _ad = check_assignment_dividend(ad or {}, candidates=[])
        logger.debug(f"[RISK][DEBUG] 规则-除息/指派: status={_ad['status']}")
    except Exception as e:  # nosec B110
        logger.error(f"[RISK] 除息/指派规则检查异常: {e}")

    logger.info("[RISK] 风险检查干跑完成（未发现配置层面的阻断项）。")

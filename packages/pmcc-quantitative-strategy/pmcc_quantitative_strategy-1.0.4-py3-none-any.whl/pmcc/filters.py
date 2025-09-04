"""Market filters: liquidity, spread, abnormal quote (mock-friendly).

Phase 2 minimal implementations to support unit tests using MockMarketDataProvider.
This module is config-driven by callers; it does not read JSON files directly.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from pmcc.utils import is_number


def filter_liquidity(cfg: dict[str, Any], quotes: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Filter quotes by minimum volume threshold.

    Parameters
    - cfg: {"min_volume": number}
    - quotes: sequence of quote dicts each including at least {symbol, volume}

    Returns
    - {"kept": [...], "dropped": [...], "min_volume": float}
    """
    min_vol = cfg.get("min_volume")
    if not is_number(min_vol):
        raise ValueError("liquidity.min_volume 应为数值")

    thr = float(min_vol)
    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for q in quotes:
        vol = q.get("volume", 0)
        if not is_number(vol):
            # 非法输入，直接丢弃至 dropped，保持健壮
            dropped.append(q)
            continue
        if float(vol) >= thr:
            kept.append(q)
        else:
            dropped.append(q)
    return {"kept": kept, "dropped": dropped, "min_volume": thr}


def filter_spread(cfg: dict[str, Any], quotes: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Filter quotes by maximum spread ratio.

    spread_ratio = (ask - bid) / mid, where mid = (bid + ask) / 2.

    Parameters
    - cfg: {"max_spread_ratio": number in (0, +inf)}
    - quotes: sequence of quote dicts each including at least {symbol, bid, ask}

    Returns
    - {"kept": [...], "dropped": [...], "max_spread_ratio": float}
    """
    mx = cfg.get("max_spread_ratio")
    if not is_number(mx):
        raise ValueError("spread.max_spread_ratio 应为数值")
    thr = float(mx)

    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for q in quotes:
        bid = q.get("bid")
        ask = q.get("ask")
        if not (is_number(bid) and is_number(ask)):
            dropped.append(q)
            continue
        bid_f = float(cast(int | float, bid))
        ask_f = float(cast(int | float, ask))
        if ask_f <= 0 or bid_f <= 0 or ask_f < bid_f:
            # 非法或倒挂，视作不合格
            dropped.append(q)
            continue
        mid = (ask_f + bid_f) / 2.0
        ratio = (ask_f - bid_f) / mid
        if ratio <= thr:
            kept.append(q)
        else:
            dropped.append(q)
    return {"kept": kept, "dropped": dropped, "max_spread_ratio": thr}


def filter_abnormal_quote(cfg: dict[str, Any], quotes: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Filter quotes where last price deviates from mid beyond a ratio.

    deviation_ratio = abs(last - mid) / mid, where mid = (bid + ask) / 2.

    Parameters
    - cfg: {"max_last_mid_dev_ratio": number in [0, +inf)}
    - quotes: sequence of quote dicts each including at least {symbol, bid, ask, last}

    Returns
    - {"kept": [...], "dropped": [...], "max_last_mid_dev_ratio": float}
    """
    mx = cfg.get("max_last_mid_dev_ratio")
    if not is_number(mx):
        raise ValueError("abnormal.max_last_mid_dev_ratio 应为数值")
    thr = float(mx)

    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for q in quotes:
        bid = q.get("bid")
        ask = q.get("ask")
        last = q.get("last")
        if not (is_number(bid) and is_number(ask) and is_number(last)):
            dropped.append(q)
            continue
        bid_f = float(cast(int | float, bid))
        ask_f = float(cast(int | float, ask))
        last_f = float(cast(int | float, last))
        # 基本合法性与不倒挂
        if ask_f <= 0 or bid_f <= 0 or last_f <= 0 or ask_f < bid_f:
            dropped.append(q)
            continue
        mid = (ask_f + bid_f) / 2.0
        dev = abs(last_f - mid) / mid
        if dev <= thr:
            kept.append(q)
        else:
            dropped.append(q)
    return {"kept": kept, "dropped": dropped, "max_last_mid_dev_ratio": thr}

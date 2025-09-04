"""技术分析计算器（RSI、MACD 与背离聚合）

说明：
- 这里实现轻量、无依赖的指标计算，满足单元测试与离线干跑需求。
- 指标计算采用常见定义：EMA、MACD(12,26,9 默认)、RSI(14 默认)。
- 背离聚合遵循配置中的多周期加权与事件窗缩放，但背离强度使用简化的枢轴近似。

注意：该实现面向教学/测试，不构成交易建议。
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any


def _to_floats(vals: Iterable[float]) -> list[float]:
    return [float(x) for x in vals]


def ema(series: Sequence[float], length: int) -> list[float]:
    if length <= 0:
        raise ValueError("EMA length must be > 0")
    out: list[float] = []
    k = 2.0 / (length + 1.0)
    ema_val: float | None = None
    for x in series:
        ema_val = float(x) if ema_val is None else (float(x) - ema_val) * k + ema_val
        out.append(float(ema_val))
    return out


def rsi(series: Sequence[float], length: int) -> list[float]:
    if length <= 0:
        raise ValueError("RSI length must be > 0")
    gains: list[float] = [0.0]
    losses: list[float] = [0.0]
    for i in range(1, len(series)):
        diff = float(series[i]) - float(series[i - 1])
        gains.append(max(0.0, diff))
        losses.append(max(0.0, -diff))
    avg_gain = ema(gains, length)
    avg_loss = ema(losses, length)
    out: list[float] = []
    for g, loss in zip(avg_gain, avg_loss, strict=True):
        rs = (float("inf") if g > 0 else 0.0) if loss == 0.0 else g / loss
        val = 100.0 - 100.0 / (1.0 + rs) if rs != float("inf") else 100.0
        # Clamp to [0,100]（数值稳定）
        out.append(max(0.0, min(100.0, float(val))))
    return out


def macd(series: Sequence[float], fast: int, slow: int, signal: int) -> dict[str, list[float]]:
    if not (fast > 0 and slow > 0 and signal > 0):
        raise ValueError("MACD periods must be positive")
    if not fast < slow:
        raise ValueError("MACD requires fast < slow")
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    line = [a - b for a, b in zip(ema_fast, ema_slow, strict=True)]
    sig = ema(line, signal)
    hist = [a - b for a, b in zip(line, sig, strict=True)]
    return {"macd": _to_floats(line), "signal": _to_floats(sig), "hist": _to_floats(hist)}


def compute_indicators(bars: Sequence[dict[str, Any]], div_cfg: dict[str, Any]) -> dict[str, Any]:
    closes = [float(b.get("close", 0.0)) for b in bars]
    if not closes:
        return {"rsi": [], "macd": {"macd": [], "signal": [], "hist": []}}
    rsi_len = int(div_cfg.get("rsi", {}).get("length", 14))
    macd_cfg = div_cfg.get("macd", {})
    fast = int(macd_cfg.get("fast", 12))
    slow = int(macd_cfg.get("slow", 26))
    signal = int(macd_cfg.get("signal", 9))
    rsi_vals = rsi(closes, rsi_len)
    macd_vals = macd(closes, fast, slow, signal)
    return {"rsi": rsi_vals, "macd": macd_vals}


def _find_pivots(series: Sequence[float], left: int, right: int, mode: str) -> list[int]:
    """极简枢轴识别，用于背离近似。

    mode = 'low'  → 局部低点
    mode = 'high' → 局部高点
    """
    idxs: list[int] = []
    n = len(series)
    for i in range(left, n - right):
        win = series[i - left : i + right + 1]
        c = series[i]
        if mode == "low" and c == min(win):
            idxs.append(i)
        if mode == "high" and c == max(win):
            idxs.append(i)
    return idxs


def _divergence_strength(
    bars: Sequence[dict[str, Any]],
    rsi_vals: Sequence[float],
    macd_hist: Sequence[float],
    cfg: dict[str, Any],
) -> float:
    """返回 [0,1] 的背离强度近似。

    简化策略：
    - 使用价格与 RSI 的最近两个低点/高点判断底/顶背离
    - 使用 MACD 柱体作为附加修正
    - 结果裁剪到 [0,1]
    """
    if not bars or len(bars) < 5:
        return 0.0
    closes = [float(b.get("close", 0.0)) for b in bars]

    rsi_cfg = cfg.get("rsi", {})
    ml = int(rsi_cfg.get("pivot_left", 2))
    mr = int(rsi_cfg.get("pivot_right", 2))
    min_strength = float(rsi_cfg.get("min_strength", 0.1))

    lows = _find_pivots(closes, ml, mr, "low")
    highs = _find_pivots(closes, ml, mr, "high")

    strength = 0.0
    # 底背离：价格更低，RSI 更高
    if len(lows) >= 2:
        i1, i2 = lows[-2], lows[-1]
        price_ll = closes[i2] < closes[i1]
        rsi_hl = rsi_vals[i2] > rsi_vals[i1]
        if price_ll and rsi_hl:
            d_price = abs((closes[i1] - closes[i2]) / max(1e-9, closes[i1]))
            d_rsi = abs((rsi_vals[i2] - rsi_vals[i1]) / 100.0)
            strength = max(strength, min(1.0, min_strength + 0.5 * d_price + 0.5 * d_rsi))

    # 顶背离：价格更高，RSI 更低（用于风险提示，同样计为强度）
    if len(highs) >= 2:
        i1, i2 = highs[-2], highs[-1]
        price_hh = closes[i2] > closes[i1]
        rsi_lh = rsi_vals[i2] < rsi_vals[i1]
        if price_hh and rsi_lh:
            d_price = abs((closes[i2] - closes[i1]) / max(1e-9, closes[i1]))
            d_rsi = abs((rsi_vals[i1] - rsi_vals[i2]) / 100.0)
            strength = max(strength, min(1.0, min_strength + 0.5 * d_price + 0.5 * d_rsi))

    # MACD 柱体辅助：若最近柱体靠近 0 且向上/下拐头，给予小幅加成
    if macd_hist:
        h_tail = macd_hist[-5:] if len(macd_hist) >= 5 else macd_hist
        slope = h_tail[-1] - h_tail[0]
        near_zero = sum(abs(x) for x in h_tail) / len(h_tail) < 1.0
        if near_zero:
            strength = min(1.0, strength + 0.05 * (1.0 if slope > 0 else 0.5))

    return float(max(0.0, min(1.0, strength)))


def aggregate_divergence(
    bars_by_tf: dict[str, Sequence[dict[str, Any]]],
    ta_cfg: dict[str, Any],
    *,
    in_event_window: bool,
) -> float:
    div = ta_cfg.get("divergence", {})
    tfs: list[str] = list(div.get("timeframes", []))
    weights: dict[str, float] = {str(k): float(v) for k, v in dict(div.get("weights", {})).items()}
    ew_scale = float(div.get("event_window_weight_scale", 1.0))

    total = 0.0
    for tf in tfs:
        bars = list(bars_by_tf.get(tf, []))
        ind = compute_indicators(bars, div)
        rsi_vals = ind["rsi"]
        macd_hist = ind["macd"]["hist"]
        s = _divergence_strength(bars, rsi_vals, macd_hist, div)
        w = float(weights.get(tf, 0.0))
        total += w * s

    if in_event_window:
        total *= max(0.0, min(1.0, ew_scale))
    # 范围裁剪，保证契约
    return float(max(0.0, min(1.0, total)))

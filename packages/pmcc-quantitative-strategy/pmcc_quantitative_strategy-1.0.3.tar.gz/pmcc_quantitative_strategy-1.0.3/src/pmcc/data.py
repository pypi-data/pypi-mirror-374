"""数据层 Mock Provider（离线可重复、可缓存）

仅用于单元测试与本地开发的干跑模式：
- 提供确定性（同进程内）OHLCV 与 Quote
- 支持基于 (kind, symbol, timeframe, limit) 的 TTL 内存缓存
- 暴露内部 _gen_counts 以便测试 Cache 命中

注意：该模块不进行真实网络访问，不构成交易建议。
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5
from time import time
from typing import Any

from pmcc.cache import TTLCache


def _tf_seconds(tf: str) -> int:
    mapping = {"1D": 86400, "4H": 4 * 3600, "1H": 3600}
    return mapping.get(tf, 86400)


def _stable_seed(*parts: str) -> int:
    """将若干字符串转为稳定的 64bit 种子（进程间一致）。

    安全说明：此处 md5 仅用于非安全场景的确定性种子，不涉及密码学用途。
    """
    h = md5()  # nosec B324: non-security deterministic seed
    for p in parts:
        h.update(p.encode("utf-8"))
    return int.from_bytes(h.digest()[:8], "big", signed=False)


@dataclass
class _CacheItem:
    ts: float
    value: Any


class MockMarketDataProvider:
    """简易行情提供者（确定性 + 内存缓存）。

    - get_quote(symbol): 返回确定性快照，并在 TTL 内缓存
    - get_ohlcv(symbol, timeframe, limit): 返回确定性 OHLCV 序列（单调时间戳），TTL 内缓存
    """

    def __init__(self, ttl_seconds: int = 600) -> None:
        self._ttl = float(ttl_seconds)
        self._cache = TTLCache(self._ttl, now=time)
        # 仅供测试：记录每个 key 的真实生成次数（缓存命中不计数）
        self._gen_counts: dict[tuple[Any, ...], int] = {}

    # ---------------------------- public API ----------------------------
    def get_quote(self, symbol: str) -> dict[str, Any]:
        key = ("quote", symbol)
        cached = self._get_cache(key)
        if cached is not None:
            return cached
        q = self._gen_quote(symbol)
        self._put_cache(key, q)
        return q

    def get_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
        key = ("ohlcv", symbol, timeframe, int(limit))
        cached = self._get_cache(key)
        if cached is not None:
            return cached
        bars = self._gen_ohlcv(symbol, timeframe, int(limit))
        self._put_cache(key, bars)
        return bars

    # --------------------------- cache helpers --------------------------
    def _get_cache(self, key: tuple[Any, ...]):
        return self._cache.get(key)

    def _put_cache(self, key: tuple[Any, ...], value: Any) -> None:
        self._cache.set(key, value)

    # --------------------------- generators ----------------------------
    def _gen_quote(self, symbol: str) -> dict[str, Any]:
        key = ("ohlcv-quote-gen", symbol)
        self._gen_counts[key] = self._gen_counts.get(key, 0) + 1
        seed = _stable_seed("quote", symbol)
        base = (seed % 10_000) / 10.0 + 50.0  # 50 ~ 1050 区间
        bid = base * 0.999
        ask = base * 1.001
        last = base
        return {
            "symbol": symbol,
            "bid": round(bid, 4),
            "ask": round(ask, 4),
            "last": round(last, 4),
            "volume": int(seed % 1_000_000),
            "ts": int(time()),
        }

    def _gen_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
        self._gen_counts[("ohlcv", symbol, timeframe, limit)] = (
            self._gen_counts.get(("ohlcv", symbol, timeframe, limit), 0) + 1
        )
        # 稳定种子驱动的简易波动模型：
        seed = _stable_seed("ohlcv", symbol, timeframe)
        # 以种子确定初始价格与方向
        price = 50.0 + (seed % 10_000) / 100.0  # 50 ~ 150 区间
        drift = ((seed >> 8) % 200 - 100) / 10_000.0  # -0.01 ~ 0.01
        vol = max(0.1, ((seed >> 16) % 500) / 1000.0)  # 0.1 ~ 0.5
        ts0 = 1_700_000_000  # 固定起点，确保单调
        step = _tf_seconds(timeframe)

        bars: list[dict[str, Any]] = []
        for i in range(limit):
            # 简化价格演化：随机游走 + 漂移
            wobble = (((seed >> (i % 32)) & 0xFF) - 127) / 127.0
            change = drift + vol * wobble / 100.0
            o = price
            c = max(0.01, o * (1.0 + change))
            hi = max(o, c) * (1.0 + abs(change) * 0.5)
            lo = min(o, c) * (1.0 - abs(change) * 0.5)
            bars.append(
                {
                    "ts": ts0 + i * step,
                    "open": float(round(o, 6)),
                    "high": float(round(hi, 6)),
                    "low": float(round(lo, 6)),
                    "close": float(round(c, 6)),
                    "volume": int((seed >> 24) % 1_000_000) + i * 10,
                }
            )
            price = c
        return bars

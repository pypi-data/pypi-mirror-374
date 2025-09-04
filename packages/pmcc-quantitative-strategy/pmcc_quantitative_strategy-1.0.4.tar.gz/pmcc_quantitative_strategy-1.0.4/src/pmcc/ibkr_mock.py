"""IBKR Market Data Mock (offline, deterministic, TTL-cached).

- get_quote(symbol): deterministic level-1 snapshot per symbol, cached by TTL
- get_ohlcv(symbol, timeframe, limit): deterministic OHLCV series, cached by TTL

Notes:
- No real network calls. For unit testing and dry-run only.
- Determinism is process-stable via md5-based seeds.
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
    # 非安全说明：仅用于离线确定性种子，不用于任何安全相关逻辑。
    h = md5()  # nosec B324: non-security deterministic seed
    for p in parts:
        h.update(p.encode("utf-8"))
    return int.from_bytes(h.digest()[:8], "big", signed=False)


@dataclass
class _CacheItem:
    ts: float
    value: Any


class IBKRMarketDataMock:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self._ttl = float(ttl_seconds)
        self._cache = TTLCache(self._ttl, now=time)
        # for tests: count actual generations (cache hits not counted)
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
        self._gen_counts[("quote", symbol)] = self._gen_counts.get(("quote", symbol), 0) + 1
        seed = _stable_seed("ibkr-quote", symbol)
        base = (seed % 10_000) / 10.0 + 50.0  # 50 ~ 1050
        spread_bps = 10  # 10 bps spread for stability
        bid = base * (1.0 - spread_bps / 10_000.0)
        ask = base * (1.0 + spread_bps / 10_000.0)
        last = base
        return {
            "symbol": symbol,
            "bid": float(round(bid, 4)),
            "ask": float(round(ask, 4)),
            "last": float(round(last, 4)),
            "volume": int(seed % 1_000_000),
            "ts": int(time()),
        }

    def _gen_ohlcv(self, symbol: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
        key = ("ohlcv", symbol, timeframe, limit)
        self._gen_counts[key] = self._gen_counts.get(key, 0) + 1
        seed = _stable_seed("ibkr-ohlcv", symbol, timeframe)
        price = 50.0 + (seed % 10_000) / 100.0
        drift = ((seed >> 8) % 200 - 100) / 10_000.0
        vol = max(0.1, ((seed >> 16) % 500) / 1000.0)
        ts0 = 1_700_000_000
        step = _tf_seconds(timeframe)

        bars: list[dict[str, Any]] = []
        for i in range(limit):
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

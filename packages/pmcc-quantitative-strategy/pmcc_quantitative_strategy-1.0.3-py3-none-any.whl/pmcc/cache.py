from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import time as _time
from typing import Any


@dataclass
class CacheItem:
    ts: float
    value: Any


class TTLCache:
    """Simple TTL cache for in-process deterministic providers.

    - Key is any hashable (tuples used by callers)
    - now() is injectable for tests
    """

    def __init__(self, ttl_seconds: float, *, now: Callable[[], float] | None = None) -> None:
        self._ttl = float(ttl_seconds)
        self._now: Callable[[], float] = now if now is not None else _time
        self._store: dict[Any, CacheItem] = {}

    def get(self, key: Any):
        item = self._store.get(key)
        if not item:
            return None
        if (self._now() - item.ts) <= self._ttl:
            return item.value
        # expired
        self._store.pop(key, None)
        return None

    def set(self, key: Any, value: Any) -> None:
        self._store[key] = CacheItem(ts=self._now(), value=value)

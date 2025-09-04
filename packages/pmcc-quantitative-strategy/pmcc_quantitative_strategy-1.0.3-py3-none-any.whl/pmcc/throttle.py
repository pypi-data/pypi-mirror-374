from __future__ import annotations

import time
from collections.abc import Callable


class TokenBucket:
    def __init__(
        self,
        rate_per_sec: float,
        capacity: int | float | None = None,
        *,
        now: Callable[[], float] | None = None,
    ) -> None:
        self.rate = float(max(0.0, rate_per_sec))
        self.capacity = float(capacity if capacity is not None else max(1.0, self.rate))
        self._tokens = self.capacity
        self._now = now or time.time
        self._ts = self._now()

    def allow(self) -> bool:
        now = self._now()
        delta = max(0.0, now - self._ts)
        self._ts = now
        self._tokens = min(self.capacity, self._tokens + delta * self.rate)
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False

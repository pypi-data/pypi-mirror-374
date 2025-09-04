from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry_with_backoff(
    func: Callable[[], T],
    *,
    retries: int = 3,
    base_delay: float = 0.01,
    sleep: Callable[[float], None] | None = None,
) -> T:
    """Call func with exponential backoff and return its result.

    The optional ``sleep`` allows tests to inject a no-op to avoid real waits.
    """
    import time as _t

    sl = sleep or _t.sleep
    last: BaseException | None = None
    for i in range(max(0, retries) + 1):
        try:
            return func()
        except BaseException as e:  # noqa: BLE001, PERF203
            last = e
            if i >= retries:
                break
            delay = base_delay * (2**i)
            sl(delay)
    if last is None:
        # Should not happen: loop guarantees last is set on failure paths
        raise RuntimeError("retry_with_backoff: no exception captured")  # pragma: no cover - defensive
    raise last

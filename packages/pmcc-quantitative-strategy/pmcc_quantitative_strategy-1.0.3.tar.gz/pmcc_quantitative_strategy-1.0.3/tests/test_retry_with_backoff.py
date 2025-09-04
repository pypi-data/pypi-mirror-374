from __future__ import annotations

from typing import List

import pytest

from pmcc.retry import retry_with_backoff


class SleepTracker:
    def __init__(self) -> None:
        self.calls: List[float] = []

    def __call__(self, seconds: float) -> None:
        # Track requested sleep durations without actually sleeping
        self.calls.append(float(seconds))


def test_retry_success_immediate():
    tracker = SleepTracker()

    def fn():
        return 42

    out = retry_with_backoff(fn, retries=3, base_delay=0.01, sleep=tracker)
    assert out == 42
    assert tracker.calls == []


def test_retry_then_success_after_two_attempts():
    tracker = SleepTracker()
    attempts = {"n": 0}

    def fn():
        attempts["n"] += 1
        if attempts["n"] <= 2:
            raise ValueError("temporary")
        return "ok"

    out = retry_with_backoff(fn, retries=3, base_delay=0.01, sleep=tracker)
    assert out == "ok"
    # backoff sequence: 0.01, 0.02 for the two failures
    assert tracker.calls == [0.01, 0.02]


def test_retry_then_failure_raises_last_exception():
    tracker = SleepTracker()

    def fn():  # noqa: D401 - simple failing callable
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        retry_with_backoff(fn, retries=2, base_delay=0.01, sleep=tracker)
    # two waits for two retries
    assert tracker.calls == [0.01, 0.02]

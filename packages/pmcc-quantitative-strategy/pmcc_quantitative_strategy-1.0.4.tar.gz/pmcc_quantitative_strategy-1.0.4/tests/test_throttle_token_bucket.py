from __future__ import annotations

from pmcc.throttle import TokenBucket


class Clock:
    def __init__(self, t: float) -> None:
        self.t = float(t)

    def now(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += float(dt)


def test_token_bucket_basic_allow_and_refill():
    clk = Clock(1000.0)
    b = TokenBucket(rate_per_sec=2.0, capacity=2.0, now=clk.now)

    # starts full: two immediate allows
    assert b.allow() is True
    assert b.allow() is True
    # drained: third immediate should be denied
    assert b.allow() is False

    # advance 0.5s → +1 token at 2 t/s
    clk.advance(0.5)
    assert b.allow() is True
    # no time progression, should be denied again
    assert b.allow() is False


def test_token_bucket_zero_rate_never_refills():
    clk = Clock(2000.0)
    b = TokenBucket(rate_per_sec=0.0, capacity=1.0, now=clk.now)

    # initial capacity grants one token
    assert b.allow() is True
    # advance arbitrarily; with zero rate, should not refill
    clk.advance(10.0)
    assert b.allow() is False


def test_token_bucket_time_rollback_is_clamped():
    clk = Clock(3000.0)
    b = TokenBucket(rate_per_sec=1.0, capacity=1.0, now=clk.now)

    # consume initial token
    assert b.allow() is True
    # move time backwards; delta should clamp to 0, no refill
    clk.advance(-100.0)
    assert b.allow() is False

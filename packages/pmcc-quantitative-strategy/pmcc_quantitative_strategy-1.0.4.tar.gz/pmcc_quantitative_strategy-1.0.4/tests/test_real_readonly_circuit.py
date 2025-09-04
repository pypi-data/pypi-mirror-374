from __future__ import annotations

from time import time  # noqa: F401 - imported for context, patched time()

from pmcc.contracts import PMCCErrorCode, QuoteRequest
from pmcc.real_readonly import RealReadonlyMarket
from pmcc.throttle import TokenBucket


def _bucket_full_now(now_val: float) -> TokenBucket:
    return TokenBucket(rate_per_sec=100.0, capacity=100.0, now=lambda: now_val)


def test_circuit_blocks_after_burst_and_cools_down(monkeypatch):
    now = {"t": 1000.0}
    # patch time() used by real_readonly to deterministic clock
    monkeypatch.setattr("pmcc.real_readonly.time", lambda: now["t"], raising=True)

    # fetcher that always raises to count errors
    def fetch_raise(_ep: str, _params: dict):
        raise RuntimeError("downstream")

    # thresholds: block after 3 consecutive errors; cool_down=10s
    mkt = RealReadonlyMarket(
        fetcher=fetch_raise,
        endpoint="/q",
        bucket=_bucket_full_now(now["t"]),
        thresholds={"block_burst": 3},
        cool_down=10.0,
    )

    # first 3 calls: errors but not yet blocked until reaching burst
    for _ in range(3):
        r = mkt.get_quote(QuoteRequest(symbol="SPY"))
        assert r.ok is False and r.error and r.error.code == PMCCErrorCode.NETWORK_ERROR

    # next call should be blocked by circuit
    r_block = mkt.get_quote(QuoteRequest(symbol="SPY"))
    assert r_block.ok is False and r_block.error and r_block.error.code == PMCCErrorCode.RATE_LIMIT
    assert r_block.error.detail and r_block.error.detail.get("retry_after") >= 0

    # advance time beyond cool_down → circuit opens
    now["t"] += 11.0
    r_after = mkt.get_quote(QuoteRequest(symbol="SPY"))
    assert r_after.ok is False and r_after.error and r_after.error.code == PMCCErrorCode.NETWORK_ERROR


def test_options_circuit_blocks_after_burst_and_cools_down(monkeypatch):
    now = {"t": 2000.0}
    monkeypatch.setattr("pmcc.real_readonly.time", lambda: now["t"], raising=True)

    def fetch_raise(_ep: str, _params: dict):
        raise RuntimeError("downstream")

    from pmcc.contracts import OptionChainRequest
    from pmcc.real_readonly import RealReadonlyOptions

    opt = RealReadonlyOptions(
        fetcher=fetch_raise,
        endpoint="/opt",
        bucket=_bucket_full_now(now["t"]),
        thresholds={"block_burst": 3},
        cool_down=10.0,
    )

    for _ in range(3):
        r = opt.get_chain(OptionChainRequest(symbol="SPY"))
        assert r.ok is False and r.error and r.error.code == PMCCErrorCode.NETWORK_ERROR

    # next call blocked by circuit
    r_block = opt.get_chain(OptionChainRequest(symbol="SPY"))
    assert r_block.ok is False and r_block.error and r_block.error.code == PMCCErrorCode.RATE_LIMIT
    assert r_block.error.detail and r_block.error.detail.get("retry_after") >= 0

    now["t"] += 11.0
    r_after = opt.get_chain(OptionChainRequest(symbol="SPY"))
    assert r_after.ok is False and r_after.error and r_after.error.code == PMCCErrorCode.NETWORK_ERROR

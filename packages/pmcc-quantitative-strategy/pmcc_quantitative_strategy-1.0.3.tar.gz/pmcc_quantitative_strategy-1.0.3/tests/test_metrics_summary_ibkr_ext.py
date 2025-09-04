from __future__ import annotations

import json
from pathlib import Path

from pmcc import metrics
from pmcc.real_readonly import RealReadonlyMarket
from pmcc.throttle import TokenBucket


def test_summary_includes_runtime_counters(monkeypatch, tmp_path: Path):
    # reset metrics
    metrics.reset()

    # Build a market provider that will succeed then rate-limit
    def fetcher(_ep: str, params: dict[str, object]):  # noqa: D401 - test stub
        return {"symbol": params.get("symbol", "SPY"), "bid": 10.0, "ask": 10.2, "last": 10.1, "ts": 1}

    class OneTokenBucket(TokenBucket):
        def __init__(self) -> None:
            super().__init__(rate_per_sec=0.0, capacity=1.0, now=lambda: 0.0)

    mkt = RealReadonlyMarket(fetcher=fetcher, endpoint="/q", bucket=OneTokenBucket())
    _ = mkt.get_quote(type("Q", (), {"symbol": "SPY"})())  # success
    _ = mkt.get_quote(type("Q", (), {"symbol": "SPY"})())  # rate limit

    # Run main in-process and capture stdout
    import sys
    from io import StringIO

    import pmcc.main as main_mod

    cfg_dir = Path(__file__).resolve().parents[1] / "config"
    argv = [
        "pmcc",
        "--config-dir",
        str(cfg_dir),
        "--summary-json",
    ]
    old = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    try:
        monkeypatch.setattr(sys, "argv", argv, raising=False)
        main_mod.main()
    except SystemExit as e:
        assert e.code == 0
    finally:
        sys.stdout = old
    out = buf.getvalue()
    lines = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("{") and ln.strip().endswith("}")]
    data = json.loads(lines[-1])
    counters = data.get("ibkr", {}).get("ext", {}).get("counters", {})
    assert counters.get("success", 0) >= 1 and counters.get("error", 0) >= 1

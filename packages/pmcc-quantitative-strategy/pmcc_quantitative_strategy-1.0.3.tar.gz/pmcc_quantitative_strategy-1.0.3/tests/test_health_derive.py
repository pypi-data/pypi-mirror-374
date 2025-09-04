from __future__ import annotations

from pmcc.health import derive_health


def test_derive_health_rates_and_bursts():
    th = {"warn_error_rate": 0.1, "block_error_rate": 0.5, "block_burst": 3}
    assert derive_health({"success": 100, "error": 0}, th) == "ok"
    assert derive_health({"success": 9, "error": 1}, th) == "ok"  # 10%
    assert derive_health({"success": 8, "error": 2}, th) == "warn"  # 20%
    assert derive_health({"success": 1, "error": 1}, th) == "blocked"  # 50%
    assert derive_health({"success": 100, "error": 3}, th) == "blocked"  # burst

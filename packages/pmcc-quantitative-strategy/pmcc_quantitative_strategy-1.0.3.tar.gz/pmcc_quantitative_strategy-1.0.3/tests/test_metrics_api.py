from __future__ import annotations

from pmcc import metrics


def test_metrics_counters_and_reset():
    metrics.reset()
    metrics.inc_success()
    metrics.inc_error()
    metrics.inc_success("market")
    metrics.inc_error("options")

    total = metrics.get_counters()
    by_kind = metrics.get_counters_by_kind()

    assert total["success"] >= 2 and total["error"] >= 2
    assert by_kind.get("market", {}).get("success", 0) >= 1
    assert by_kind.get("options", {}).get("error", 0) >= 1

    metrics.reset()
    total2 = metrics.get_counters()
    by_kind2 = metrics.get_counters_by_kind()
    assert total2 == {"success": 0, "error": 0}
    assert all(v == {"success": 0, "error": 0} for v in by_kind2.values())

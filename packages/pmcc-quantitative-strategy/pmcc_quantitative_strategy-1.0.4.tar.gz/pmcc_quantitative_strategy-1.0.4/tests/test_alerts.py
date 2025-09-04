from __future__ import annotations

from types import SimpleNamespace

import pmcc.alerts as alerts


def test_alerts_notify_success(monkeypatch):
    class Resp:
        status_code = 200

    def post(url, **kw):  # noqa: D401 - stub
        assert url == "http://webhook"
        assert kw.get("json", {}).get("event") == "test"
        return Resp()

    fake_requests = SimpleNamespace(post=post)
    import importlib

    monkeypatch.setenv("PMCC_ALERT_WEBHOOK", "http://webhook")
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda n: fake_requests if n == "requests" else importlib.import_module(n),
        raising=True,
    )
    ok = alerts.notify("test", {"x": 1})
    assert ok is True


def test_alerts_notify_missing_requests(monkeypatch):
    import importlib

    monkeypatch.setenv("PMCC_ALERT_WEBHOOK", "http://webhook")
    monkeypatch.setattr(
        importlib, "import_module", lambda n: (_ for _ in ()).throw(RuntimeError("no requests")), raising=True
    )
    ok = alerts.notify("test", {"x": 1})
    assert ok is False


def test_alerts_notify_no_env_returns_false(monkeypatch):
    # Ensure env is absent → early return False
    monkeypatch.delenv("PMCC_ALERT_WEBHOOK", raising=False)
    ok = alerts.notify("test", {"x": 1})
    assert ok is False

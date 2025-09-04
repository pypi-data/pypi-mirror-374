from __future__ import annotations

from pmcc.cache import TTLCache


def test_ttlcache_get_set_and_expiry():
    t = {"now": 100.0}

    def now():
        return t["now"]

    c = TTLCache(10.0, now=now)
    k = ("k", 1)
    assert c.get(k) is None
    c.set(k, 123)
    assert c.get(k) == 123

    # within ttl
    t["now"] = 105.0
    assert c.get(k) == 123

    # after ttl -> expired
    t["now"] = 200.0
    assert c.get(k) is None

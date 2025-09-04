from __future__ import annotations

from pmcc.pretrade import DefaultPretradeChecks, run_pretrade_checks


def test_pretrade_protocol_impl_matches_function(cfgs_default):
    impl = DefaultPretradeChecks()
    r1 = run_pretrade_checks(cfgs_default)
    r2 = impl.run(cfgs_default, context={})
    assert r1.ok == r2.ok
    assert bool(r1.data and r1.data.ok) == bool(r2.data and r2.data.ok)

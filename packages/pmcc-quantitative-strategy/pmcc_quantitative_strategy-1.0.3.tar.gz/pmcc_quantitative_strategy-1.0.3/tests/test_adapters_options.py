from __future__ import annotations

import pmcc.adapters as adp
import pmcc.contracts as c


def test_options_adapter_not_implemented():
    oa = adp.OptionsAdapter()
    r = oa.get_chain(c.OptionChainRequest(symbol="SPY"))
    assert r.ok is False and r.error and r.error.code == c.PMCCErrorCode.NOT_IMPLEMENTED

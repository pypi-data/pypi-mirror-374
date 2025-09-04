from __future__ import annotations

from pmcc.contracts import OptionChainRequest
from pmcc.data import MockMarketDataProvider
from pmcc.options_synth import SyntheticOptionsProvider


def test_synthetic_options_chain_shape():
    prov = SyntheticOptionsProvider(MockMarketDataProvider())
    r = prov.get_chain(OptionChainRequest(symbol="SPY"))
    assert r.ok and r.data and len(r.data) == 10
    c0 = r.data[0]
    assert c0.type == "C" and c0.dte > 0 and c0.bid > 0 and c0.ask > c0.bid

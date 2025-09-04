from __future__ import annotations

from pmcc.providers import MarketDataProvider, OptionsProvider
from pmcc.real_spec import RealMarketDataProviderSpec, RealOptionsProviderSpec


def test_real_specs_conform_to_protocols():
    assert isinstance(RealMarketDataProviderSpec(), MarketDataProvider)
    assert isinstance(RealOptionsProviderSpec(), OptionsProvider)

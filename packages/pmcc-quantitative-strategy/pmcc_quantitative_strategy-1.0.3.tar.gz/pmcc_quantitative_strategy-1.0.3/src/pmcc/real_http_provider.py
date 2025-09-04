from __future__ import annotations

from typing import Any

from pmcc.connectors import (
    _http_fetcher as __http_fetcher,
    _make_bucket as __make_bucket,
)
from pmcc.providers import MarketDataProvider, OptionsProvider
from pmcc.real_readonly import RealReadonlyMarket, RealReadonlyOptions


def make_market_provider(cfgs: dict[str, Any] | None = None) -> MarketDataProvider:
    return RealReadonlyMarket(fetcher=__http_fetcher, endpoint="/quote", bucket=__make_bucket(cfgs or {}))


def make_options_provider(cfgs: dict[str, Any] | None = None) -> OptionsProvider:
    return RealReadonlyOptions(fetcher=__http_fetcher, endpoint="/options", bucket=__make_bucket(cfgs or {}))

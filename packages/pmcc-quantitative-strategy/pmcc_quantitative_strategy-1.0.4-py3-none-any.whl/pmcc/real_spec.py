from __future__ import annotations

from pmcc.contracts import (
    APIResult,
    MultiQuote,
    OptionChainRequest,
    OptionContract,
    Quote,
    QuoteRequest,
    SymbolsRequest,
)
from pmcc.providers import MarketDataProvider, OptionsProvider


class RealMarketDataProviderSpec(MarketDataProvider):
    """只读行情真实连接器方案草图（占位，不做 I/O）。

    说明：
    - 方法签名与协议一致；
    - 实现留空（raise NotImplementedError），用于规划与集成测试的占位；
    - 后续接入时替换为真实 IBKR/TWS/Gateway 只读实现，并严格遵循安全与节流策略。
    """

    def get_quote(self, req: QuoteRequest) -> APIResult[Quote]:  # pragma: no cover - skeleton
        raise NotImplementedError

    def get_quotes(self, req: SymbolsRequest) -> APIResult[MultiQuote]:  # pragma: no cover - skeleton
        raise NotImplementedError


class RealOptionsProviderSpec(OptionsProvider):
    """只读期权链真实连接器方案草图（占位，不做 I/O）。"""

    def get_chain(self, req: OptionChainRequest) -> APIResult[list[OptionContract]]:  # pragma: no cover - skeleton
        raise NotImplementedError

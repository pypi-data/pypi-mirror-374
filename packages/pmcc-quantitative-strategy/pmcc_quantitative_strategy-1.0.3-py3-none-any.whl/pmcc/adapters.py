from __future__ import annotations

from pmcc.contracts import (
    APIError,
    APIResult,
    MultiQuote,
    OptionChainRequest,
    OptionContract,
    PMCCErrorCode,
    Quote,
    QuoteRequest,
    SymbolsRequest,
)
from pmcc.data import MockMarketDataProvider
from pmcc.providers import MarketDataProvider, OptionsProvider


class MarketDataAdapter(MarketDataProvider):
    """Adapter: wrap MockMarketDataProvider to conform to MarketDataProvider Protocol."""

    def __init__(self, backend: MockMarketDataProvider | None = None) -> None:
        self._b = backend or MockMarketDataProvider()
        self._succ = 0
        self._err = 0

    def get_quote(self, req: QuoteRequest) -> APIResult[Quote]:
        try:
            q = self._b.get_quote(req.symbol)
            data = Quote(
                symbol=str(q["symbol"]),
                bid=float(q["bid"]),
                ask=float(q["ask"]),
                last=float(q["last"]),
                ts=int(q["ts"]),
            )
            self._succ += 1
            return APIResult(ok=True, data=data)
        except Exception as e:  # noqa: BLE001
            self._err += 1
            return APIResult(
                ok=False,
                error=APIError(code=PMCCErrorCode.NETWORK_ERROR, message=str(e), detail={"op": "get_quote"}),
            )

    def get_quotes(self, req: SymbolsRequest) -> APIResult[MultiQuote]:
        try:
            quotes: list[Quote] = []
            for sym in list(req.symbols):
                q = self._b.get_quote(str(sym))
                quotes.append(
                    Quote(
                        symbol=str(q["symbol"]),
                        bid=float(q["bid"]),
                        ask=float(q["ask"]),
                        last=float(q["last"]),
                        ts=int(q["ts"]),
                    )
                )
            self._succ += len(quotes)
            return APIResult(ok=True, data=MultiQuote(quotes=quotes, page=None))
        except Exception as e:  # noqa: BLE001
            self._err += 1
            return APIResult(
                ok=False,
                error=APIError(
                    code=PMCCErrorCode.NETWORK_ERROR,
                    message=str(e),
                    detail={"op": "get_quotes", "count": len(req.symbols)},
                ),
            )

    # Counters (lightweight, no I/O)
    def get_counters(self) -> dict[str, int]:
        return {"success": int(self._succ), "error": int(self._err)}


class OptionsAdapter(OptionsProvider):
    """Placeholder adapter for options provider (not implemented in mock stage)."""

    def get_chain(self, req: OptionChainRequest) -> APIResult[list[OptionContract]]:
        return APIResult[list[OptionContract]](
            ok=False,
            error=APIError(
                code=PMCCErrorCode.NOT_IMPLEMENTED,
                message="Options chain provider not implemented in mock stage",
                detail={"symbol": getattr(req, "symbol", None)},
            ),
        )

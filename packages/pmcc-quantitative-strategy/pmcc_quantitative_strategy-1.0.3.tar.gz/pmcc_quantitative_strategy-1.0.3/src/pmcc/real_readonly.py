from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from time import time
from typing import Any

from pmcc import metrics as _metrics
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
from pmcc.retry import retry_with_backoff
from pmcc.throttle import TokenBucket

Fetcher = Callable[[str, dict[str, Any]], dict[str, Any]]


@dataclass
class RealReadonlyMarket:
    fetcher: Fetcher
    endpoint: str
    bucket: TokenBucket
    # health/circuit thresholds (optional): warn_error_rate, block_error_rate, block_burst
    thresholds: dict[str, float | int] | None = None
    cool_down: float = 30.0  # seconds
    _err_burst: int = field(default=0, init=False)
    _cool_until: float = field(default=0.0, init=False)

    def get_quote(self, req: QuoteRequest) -> APIResult[Quote]:
        now = time()
        if self._cool_until and now < self._cool_until:
            _metrics.inc_error("market")
            return APIResult(
                ok=False,
                error=APIError(
                    code=PMCCErrorCode.RATE_LIMIT,
                    message="circuit blocked",
                    detail={"retry_after": float(self._cool_until - now)},
                ),
            )
        if not self.bucket.allow():
            _metrics.inc_error("market")
            return APIResult(ok=False, error=APIError(code=PMCCErrorCode.RATE_LIMIT, message="rate limit"))
        try:

            def _call():
                return self.fetcher(self.endpoint, {"symbol": req.symbol})

            data = retry_with_backoff(_call, retries=2, base_delay=0.0, sleep=lambda _s: None)
            q = Quote(
                symbol=str(data["symbol"]),
                bid=float(data["bid"]),
                ask=float(data["ask"]),
                last=float(data["last"]),
                ts=int(data["ts"]),
            )
            _metrics.inc_success("market")
            # success resets burst and circuit
            self._err_burst = 0
            self._cool_until = 0.0
            return APIResult(ok=True, data=q)
        except KeyError as e:
            _metrics.inc_error("market")
            self._err_burst += 1
            self._maybe_block(now)
            return APIResult(ok=False, error=APIError(code=PMCCErrorCode.SCHEMA_ERROR, message=str(e)))
        except Exception as e:  # noqa: BLE001
            _metrics.inc_error("market")
            self._err_burst += 1
            self._maybe_block(now)
            return APIResult(ok=False, error=APIError(code=PMCCErrorCode.NETWORK_ERROR, message=str(e)))

    def get_quotes(self, req: SymbolsRequest) -> APIResult[MultiQuote]:
        quotes: list[Quote] = []
        for s in req.symbols:
            r = self.get_quote(QuoteRequest(symbol=str(s)))
            if not r.ok or not r.data:
                return APIResult(ok=False, error=r.error)  # bubble first failure
            quotes.append(r.data)
        return APIResult(ok=True, data=MultiQuote(quotes=quotes, page=None))

    def _maybe_block(self, now: float) -> None:
        th = self.thresholds or {}
        block_burst = int(th.get("block_burst", 5)) if isinstance(th, dict) else 5
        if self._err_burst >= block_burst:
            self._cool_until = now + float(self.cool_down)


@dataclass
class RealReadonlyOptions:
    fetcher: Fetcher
    endpoint: str
    bucket: TokenBucket
    thresholds: dict[str, float | int] | None = None
    cool_down: float = 30.0
    _err_burst: int = field(default=0, init=False)
    _cool_until: float = field(default=0.0, init=False)

    def get_chain(self, req: OptionChainRequest) -> APIResult[list[OptionContract]]:
        now = time()
        if self._cool_until and now < self._cool_until:
            _metrics.inc_error("options")
            return APIResult(
                ok=False,
                error=APIError(
                    code=PMCCErrorCode.RATE_LIMIT,
                    message="circuit blocked",
                    detail={"retry_after": float(self._cool_until - now)},
                ),
            )
        if not self.bucket.allow():
            _metrics.inc_error("options")
            return APIResult(ok=False, error=APIError(code=PMCCErrorCode.RATE_LIMIT, message="rate limit"))
        try:

            def _call():
                return self.fetcher(self.endpoint, {"symbol": req.symbol})

            data = retry_with_backoff(_call, retries=2, base_delay=0.0, sleep=lambda _s: None)
            out: list[OptionContract] = [
                OptionContract(
                    symbol=str(it["symbol"]),
                    type=str(it.get("type", "C")),
                    dte=int(it["dte"]),
                    strike=float(it["strike"]),
                    bid=float(it["bid"]),
                    ask=float(it["ask"]),
                    last=float(it.get("last", (it["bid"] + it["ask"]) / 2.0)),
                    iv=float(it.get("iv", 0.0)),
                    oi=int(it.get("oi", 0)),
                    delta=float(it.get("delta", 0.0)),
                    gamma=float(it.get("gamma", 0.0)),
                )
                for it in data.get("chain", [])
            ]
            _metrics.inc_success("options")
            self._err_burst = 0
            self._cool_until = 0.0
            return APIResult(ok=True, data=out)
        except KeyError as e:
            _metrics.inc_error("options")
            self._err_burst += 1
            self._maybe_block(now)
            return APIResult(ok=False, error=APIError(code=PMCCErrorCode.SCHEMA_ERROR, message=str(e)))
        except Exception as e:  # noqa: BLE001
            _metrics.inc_error("options")
            self._err_burst += 1
            self._maybe_block(now)
            return APIResult(ok=False, error=APIError(code=PMCCErrorCode.NETWORK_ERROR, message=str(e)))

    def _maybe_block(self, now: float) -> None:
        th = self.thresholds or {}
        block_burst = int(th.get("block_burst", 5)) if isinstance(th, dict) else 5
        if self._err_burst >= block_burst:
            self._cool_until = now + float(self.cool_down)

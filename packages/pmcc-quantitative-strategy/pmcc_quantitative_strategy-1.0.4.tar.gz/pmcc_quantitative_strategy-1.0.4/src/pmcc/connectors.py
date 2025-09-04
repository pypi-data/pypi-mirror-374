from __future__ import annotations

import os
from typing import Any

from pmcc.adapters import MarketDataAdapter
from pmcc.contracts import APIResult, MultiQuote, PMCCErrorCode, Quote, QuoteRequest, SymbolsRequest
from pmcc.data import MockMarketDataProvider
from pmcc.options_synth import SyntheticOptionsProvider
from pmcc.providers import MarketDataProvider, OptionsProvider
from pmcc.real_readonly import RealReadonlyMarket, RealReadonlyOptions
from pmcc.throttle import TokenBucket


def _env_bool(name: str, default: bool = False) -> bool:
    import os

    v = os.environ.get(name)
    if v is None:
        return bool(default)
    return str(v).strip().lower() in {"1", "true", "yes", "on", "y"}


def _default_fetcher(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """Default HTTP fetcher used by real-readonly stub.

    This is only used when tests or runtime enable PMCC_REAL_STUB=1. In unit
    tests, this function is monkeypatched to avoid real network I/O.
    """
    import json
    import os
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen

    base = os.environ.get("PMCC_REAL_BASE_URL", "http://127.0.0.1:0")
    url = base.rstrip("/") + "/" + endpoint.lstrip("/") + ("?" + urlencode(params) if params else "")
    req = Request(url, method="GET")
    with urlopen(req, timeout=2.0) as resp:  # nosec B310: not used in production
        return json.loads(resp.read().decode("utf-8"))


def _http_fetcher(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """HTTP fetcher using requests (read-only adapter).

    - Base URL: PMCC_REAL_BASE_URL (default http://127.0.0.1:0)
    - Timeout: PMCC_REAL_TIMEOUT (seconds, default 3.0)
    - Headers (optional): PMCC_REAL_HEADERS_JSON (JSON object)
    """
    import importlib
    import json as _json
    import os as _os

    try:
        _rq = importlib.import_module("requests")
    except Exception as _e:  # noqa: BLE001
        # Raise to be mapped by RealReadonly* as NETWORK_ERROR
        raise RuntimeError(f"requests missing: {_e}") from _e

    base = _os.environ.get("PMCC_REAL_BASE_URL", "http://127.0.0.1:0").rstrip("/")
    url = base + "/" + endpoint.lstrip("/")
    timeout = float(_os.environ.get("PMCC_REAL_TIMEOUT", "3.0"))
    headers_env = _os.environ.get("PMCC_REAL_HEADERS_JSON")
    headers: dict[str, str] | None = None
    if headers_env:
        try:
            obj = _json.loads(headers_env)
            if isinstance(obj, dict):
                headers = {str(k): str(v) for k, v in obj.items()}
        except Exception:
            headers = None
    r = _rq.get(url, params=params, timeout=timeout, headers=headers)
    status = int(getattr(r, "status_code", 0))
    if 200 <= status < 300:
        try:
            return r.json()
        except Exception as _ee:  # noqa: BLE001
            raise RuntimeError(f"invalid json: {_ee}") from _ee
    raise RuntimeError(f"http status {status}")


def _make_bucket(cfgs: dict[str, Any] | None) -> TokenBucket:
    ds = cfgs.get("data_sources.json", {}) if isinstance(cfgs, dict) else {}
    th = ds.get("throttle", {}) if isinstance(ds, dict) else {}
    rps = float(th.get("requests_per_sec", 1.0)) if isinstance(th, dict) else 1.0
    cap = float(th.get("capacity", max(1.0, rps))) if isinstance(th, dict) else max(1.0, rps)
    return TokenBucket(rate_per_sec=rps, capacity=cap)


def _health_thresholds(cfgs: dict[str, Any] | None) -> dict[str, float | int]:
    ds = cfgs.get("data_sources.json", {}) if isinstance(cfgs, dict) else {}
    ht = ds.get("health_thresholds", {}) if isinstance(ds, dict) else {}
    # defaults align with pmcc.health.derive_health
    out: dict[str, float | int] = {
        "warn_error_rate": float(ht.get("warn_error_rate", 0.05)) if isinstance(ht, dict) else 0.05,
        "block_error_rate": float(ht.get("block_error_rate", 0.2)) if isinstance(ht, dict) else 0.2,
        "block_burst": int(ht.get("block_burst", 5)) if isinstance(ht, dict) else 5,
    }
    return out


class _NotImplementedMarketData(MarketDataProvider):
    def get_quote(self, req: QuoteRequest) -> APIResult[Quote]:
        from pmcc.contracts import APIError

        return APIResult(
            ok=False,
            error=APIError(code=PMCCErrorCode.NOT_IMPLEMENTED, message="real provider not available"),
        )

    def get_quotes(self, req: SymbolsRequest) -> APIResult[MultiQuote]:
        from pmcc.contracts import APIError

        return APIResult(
            ok=False,
            error=APIError(code=PMCCErrorCode.NOT_IMPLEMENTED, message="real provider not available"),
        )


def get_market_data_provider(cfgs: dict[str, Any] | None = None) -> MarketDataProvider:
    backend = str(os.environ.get("PMCC_DATA_BACKEND", "mock")).strip().lower()
    if backend == "real":
        # Optional stub for contract integration (no real trading/data). Enable via PMCC_REAL_STUB=1
        if _env_bool("PMCC_REAL_HTTP", False):
            ep = os.environ.get("PMCC_REAL_MARKET_EP", "/quote")
            return RealReadonlyMarket(
                fetcher=_http_fetcher,
                endpoint=str(ep),
                bucket=_make_bucket(cfgs or {}),
                thresholds=_health_thresholds(cfgs or {}),
            )
        if _env_bool("PMCC_REAL_STUB", False):
            ep = os.environ.get("PMCC_REAL_MARKET_EP", "/quote")
            return RealReadonlyMarket(
                fetcher=_default_fetcher,
                endpoint=str(ep),
                bucket=_make_bucket(cfgs or {}),
                thresholds=_health_thresholds(cfgs or {}),
            )
        return _NotImplementedMarketData()
    return MarketDataAdapter(MockMarketDataProvider())


def get_throttle(cfgs: dict[str, Any]) -> dict[str, Any]:
    ds = cfgs.get("data_sources.json", {}) if isinstance(cfgs, dict) else {}
    th = ds.get("throttle", {}) if isinstance(ds, dict) else {}
    return th if isinstance(th, dict) else {}


def get_options_provider(cfgs: dict[str, Any] | None = None) -> OptionsProvider:
    backend = str(os.environ.get("PMCC_DATA_BACKEND", "mock")).strip().lower()
    if backend == "real":
        if _env_bool("PMCC_REAL_HTTP", False):
            ep = os.environ.get("PMCC_REAL_OPTIONS_EP", "/options")
            return RealReadonlyOptions(
                fetcher=_http_fetcher,
                endpoint=str(ep),
                bucket=_make_bucket(cfgs or {}),
                thresholds=_health_thresholds(cfgs or {}),
            )
        if _env_bool("PMCC_REAL_STUB", False):
            ep = os.environ.get("PMCC_REAL_OPTIONS_EP", "/options")
            return RealReadonlyOptions(
                fetcher=_default_fetcher,
                endpoint=str(ep),
                bucket=_make_bucket(cfgs or {}),
                thresholds=_health_thresholds(cfgs or {}),
            )

        # Placeholder real provider (not implemented in M1)
        class _NotImpl(OptionsProvider):
            from pmcc.contracts import OptionChainRequest

            def get_chain(self, req: OptionChainRequest) -> APIResult[list]:
                from pmcc.contracts import APIError, APIResult as _R, PMCCErrorCode as _C

                return _R(
                    ok=False,
                    error=APIError(
                        code=_C.NOT_IMPLEMENTED,
                        message="real options provider not available",
                    ),
                )

        return _NotImpl()
    return SyntheticOptionsProvider(MockMarketDataProvider())

"""PMCC Strategy enumeration and scoring (TDD-driven, offline).

Exports:
- enumerate_pmcc_candidates(cfg, chain, quote) -> list[dict]
- filter_and_score_pmcc_candidates(cfg, chain, quote) -> dict

This module is deterministic and pure (no I/O). It expects the option chain as a
list of dicts with fields: {symbol, type, dte, strike, bid, ask, last, iv, oi, delta, gamma}.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypedDict

from pmcc.utils import is_number


class _Opt(TypedDict, total=False):
    symbol: str
    type: str
    dte: int
    strike: float
    bid: float
    ask: float
    last: float
    iv: float
    oi: int
    delta: float
    gamma: float


def _mid(bid: Any, ask: Any) -> float:
    if not (is_number(bid) and is_number(ask)):
        return 0.0
    b = float(bid)
    a = float(ask)
    if a <= 0 or b <= 0:
        return 0.0
    return (a + b) / 2.0


def _spread_ratio(bid: Any, ask: Any) -> float:
    m = _mid(bid, ask)
    if m <= 0:
        return 9e9
    return (float(ask) - float(bid)) / m


def _select_leaps(cfg: dict[str, Any], chain: Sequence[_Opt]) -> list[_Opt]:
    min_dte = int(cfg.get("min_leaps_dte", 360))
    lo, hi = cfg.get("leaps_delta_range", (0.6, 0.8))
    out: list[_Opt] = []
    for o in chain:
        if o.get("type") != "C":
            continue
        dte = int(o.get("dte", 0))
        delta = float(o.get("delta", 0.0))
        bid = o.get("bid")
        ask = o.get("ask")
        if dte < min_dte:
            continue
        if not (lo <= delta <= hi):
            continue
        if _mid(bid, ask) <= 0:
            continue
        out.append(o)
    return out


def _select_shorts(cfg: dict[str, Any], chain: Sequence[_Opt]) -> list[_Opt]:
    tgt = int(cfg.get("target_short_dte", 30))
    lo, hi = cfg.get("short_delta_range", (0.15, 0.35))
    # window: [tgt-10, tgt+15] -> matches tests 20..45 when tgt=30
    lo_dte = max(1, tgt - 10)
    hi_dte = tgt + 15
    out: list[_Opt] = []
    for o in chain:
        if o.get("type") != "C":
            continue
        dte = int(o.get("dte", 0))
        delta = float(o.get("delta", 0.0))
        bid = o.get("bid")
        ask = o.get("ask")
        if not (lo_dte <= dte <= hi_dte):
            continue
        if not (lo <= delta <= hi):
            continue
        if _mid(bid, ask) <= 0:
            continue
        out.append(o)
    return out


def enumerate_pmcc_candidates(
    cfg: dict[str, Any], chain: Sequence[_Opt], quote: dict[str, Any]
) -> list[dict[str, Any]]:
    """Enumerate PMCC candidates by pairing eligible LEAPS with eligible short calls.

    Returns a list of candidate dicts with keys: {symbol, leaps, short}.
    """
    symbol = str(quote.get("symbol", ""))
    leaps_list = _select_leaps(cfg, chain)
    short_list = _select_shorts(cfg, chain)

    cands: list[dict[str, Any]] = []
    for leaps in leaps_list:
        for short in short_list:
            if leaps.get("symbol") != symbol or short.get("symbol") != symbol:
                # only pair same underlying symbol as quote
                continue
            cands.append(
                {
                    "symbol": symbol,
                    "leaps": leaps,
                    "short": short,
                }
            )
    return cands


def _annualized_yield(short_mid: float, under_price: float, dte: int) -> float:
    if short_mid <= 0 or under_price <= 0 or dte <= 0:
        return 0.0
    return (short_mid / under_price) * (365.0 / float(dte))


def _score_candidate(cfg: dict[str, Any], cand: dict[str, Any], quote: dict[str, Any]) -> float:
    under = float(quote.get("last", 0.0))
    s = cand["short"]
    short_mid = _mid(s.get("bid"), s.get("ask"))
    dte = int(s.get("dte", 0))
    iv = float(s.get("iv", 0.0))

    yld = _annualized_yield(short_mid, under, dte)
    # weights: prioritize yield, then IV; both positive
    w_yield = float(cfg.get("w_yield", 1.0))
    w_iv = float(cfg.get("w_iv", 0.2))
    score = w_yield * yld + w_iv * iv
    return score


def filter_and_score_pmcc_candidates(
    cfg: dict[str, Any], chain: Sequence[_Opt], quote: dict[str, Any]
) -> dict[str, Any]:
    """Filter candidates by liquidity rules and attach scores; return sorted desc.

    Applies:
    - max_spread_ratio: on short leg
    - min_oi: on short leg
    - top_k: optional truncation after sorting by score desc
    """
    cands = enumerate_pmcc_candidates(cfg, chain, quote)

    max_spread = float(cfg.get("max_spread_ratio", 0.10))
    min_oi = int(cfg.get("min_oi", 0))

    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for c in cands:
        s = c["short"]
        sr = _spread_ratio(s.get("bid"), s.get("ask"))
        oi = int(s.get("oi", 0))
        if sr > max_spread or oi < min_oi:
            dropped.append(c)
            continue
        c = dict(c)
        c["score"] = _score_candidate(cfg, c, quote)
        kept.append(c)

    kept.sort(key=lambda x: x.get("score", 0.0), reverse=True)

    top_k = cfg.get("top_k")
    if isinstance(top_k, int) and top_k > 0:
        kept = kept[:top_k]

    return {
        "kept": kept,
        "dropped": dropped,
        "max_spread_ratio": max_spread,
        "min_oi": min_oi,
    }

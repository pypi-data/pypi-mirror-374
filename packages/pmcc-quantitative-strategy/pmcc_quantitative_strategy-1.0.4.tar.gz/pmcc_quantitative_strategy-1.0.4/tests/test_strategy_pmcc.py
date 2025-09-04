from __future__ import annotations

import math
from typing import Literal, TypedDict

from pmcc.strategy import (
    enumerate_pmcc_candidates,
    filter_and_score_pmcc_candidates,
)


class Opt(TypedDict, total=False):
    symbol: str
    type: Literal["C", "P"]
    dte: int
    strike: float
    bid: float
    ask: float
    last: float
    iv: float
    oi: int
    delta: float
    gamma: float


def make_chain(underlying: str) -> list[Opt]:
    # Construct a small synthetic chain
    chain: list[Opt] = []
    # LEAPS-like call (eligible)
    chain.append(
        Opt(
            symbol=underlying,
            type="C",
            dte=400,
            strike=90.0,
            bid=22.0,
            ask=22.6,
            last=22.3,
            iv=0.35,
            oi=500,
            delta=0.7,
            gamma=0.01,
        )
    )
    # LEAPS but too short DTE (not eligible)
    chain.append(
        Opt(
            symbol=underlying,
            type="C",
            dte=200,
            strike=92.0,
            bid=19.0,
            ask=19.8,
            last=19.4,
            iv=0.34,
            oi=800,
            delta=0.7,
            gamma=0.015,
        )
    )
    # Short candidates around 30 DTE
    chain.append(
        Opt(
            symbol=underlying,
            type="C",
            dte=30,
            strike=105.0,
            bid=1.9,
            ask=2.1,
            last=2.0,
            iv=0.45,
            oi=1000,
            delta=0.25,
            gamma=0.05,
        )
    )
    chain.append(
        Opt(
            symbol=underlying,
            type="C",
            dte=28,
            strike=107.0,
            bid=1.2,
            ask=1.3,
            last=1.25,
            iv=0.40,
            oi=1200,
            delta=0.18,
            gamma=0.045,
        )
    )
    # A short leg with wide spread (should be filtered out)
    chain.append(
        Opt(
            symbol=underlying,
            type="C",
            dte=30,
            strike=110.0,
            bid=0.5,
            ask=1.2,  # wide
            last=0.9,
            iv=0.42,
            oi=50,  # low OI
            delta=0.15,
            gamma=0.04,
        )
    )
    return chain


def test_enumerate_basic_and_shapes():
    cfg = {
        "min_leaps_dte": 360,
        "leaps_delta_range": [0.6, 0.8],
        "target_short_dte": 30,
        "short_delta_range": [0.15, 0.35],
    }
    quote = {"symbol": "XYZ", "last": 100.0}
    chain = make_chain("XYZ")

    cands = enumerate_pmcc_candidates(cfg, chain, quote)
    assert isinstance(cands, list) and len(cands) >= 1
    c = cands[0]
    assert set(c) >= {"leaps", "short"}
    assert c["leaps"]["dte"] >= 360 and 0.6 <= c["leaps"]["delta"] <= 0.8
    assert 20 <= c["short"]["dte"] <= 45 and 0.15 <= c["short"]["delta"] <= 0.35


def test_filters_spread_and_oi_and_sorting():
    cfg = {
        "min_leaps_dte": 360,
        "leaps_delta_range": [0.6, 0.8],
        "target_short_dte": 30,
        "short_delta_range": [0.15, 0.35],
        "max_spread_ratio": 0.06,
        "min_oi": 100,
        "top_k": 5,
    }
    quote = {"symbol": "XYZ", "last": 100.0}
    chain = make_chain("XYZ")

    ranked = filter_and_score_pmcc_candidates(cfg, chain, quote)
    # ensure wide-spread/low-OI short leg is not in kept set
    kept = ranked["kept"]
    for c in kept:
        mid = (c["short"]["bid"] + c["short"]["ask"]) / 2
        spread = c["short"]["ask"] - c["short"]["bid"]
        assert spread / mid <= cfg["max_spread_ratio"]
        assert c["short"]["oi"] >= cfg["min_oi"]

    # sorting by score desc
    scores = [c["score"] for c in kept]
    assert scores == sorted(scores, reverse=True)


def test_scoring_prefers_higher_yield_and_iv():
    cfg = {
        "min_leaps_dte": 360,
        "leaps_delta_range": [0.6, 0.8],
        "target_short_dte": 30,
        "short_delta_range": [0.15, 0.35],
        "max_spread_ratio": 0.10,
        "min_oi": 10,
    }
    quote = {"symbol": "XYZ", "last": 100.0}
    chain = make_chain("XYZ")

    # modify two short candidates: one with higher mid and iv
    for opt in chain:
        if opt["type"] == "C" and opt["dte"] == 30 and math.isclose(opt["strike"], 105.0):
            opt["bid"], opt["ask"], opt["iv"] = 2.2, 2.4, 0.50  # higher yield + IV
        if opt["type"] == "C" and opt["dte"] == 28 and math.isclose(opt["strike"], 107.0):
            opt["bid"], opt["ask"], opt["iv"] = 1.0, 1.1, 0.35  # lower yield + IV

    ranked = filter_and_score_pmcc_candidates(cfg, chain, quote)
    kept = ranked["kept"]
    assert len(kept) >= 2

    # The 105 short (higher yield+IV) should rank above 107 short
    strikes = [c["short"]["strike"] for c in kept]
    assert strikes[0] == 105.0

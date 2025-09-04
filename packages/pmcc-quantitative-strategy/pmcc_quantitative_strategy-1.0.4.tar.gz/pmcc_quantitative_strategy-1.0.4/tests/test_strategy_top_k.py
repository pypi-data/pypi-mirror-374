from pmcc.strategy import filter_and_score_pmcc_candidates


def test_top_k_truncates_to_best_candidate():
    cfg = {
        "min_leaps_dte": 360,
        "leaps_delta_range": [0.6, 0.8],
        "target_short_dte": 30,
        "short_delta_range": [0.15, 0.35],
        "max_spread_ratio": 0.10,
        "min_oi": 0,
        "top_k": 1,
    }

    symbol = "S"
    quote = {"symbol": symbol, "last": 100.0}

    chain = [
        # LEAPS
        {
            "symbol": symbol,
            "type": "C",
            "dte": 400,
            "strike": 90.0,
            "bid": 20.0,
            "ask": 22.0,
            "last": 21.0,
            "iv": 0.30,
            "oi": 500,
            "delta": 0.7,
            "gamma": 0.01,
        },
        # Shorts (both eligible), first has higher mid and iv
        {
            "symbol": symbol,
            "type": "C",
            "dte": 30,
            "strike": 105.0,
            "bid": 2.0,
            "ask": 2.2,
            "last": 2.1,
            "iv": 0.40,
            "oi": 1000,
            "delta": 0.25,
            "gamma": 0.05,
        },
        {
            "symbol": symbol,
            "type": "C",
            "dte": 30,
            "strike": 110.0,
            "bid": 1.0,
            "ask": 1.1,
            "last": 1.05,
            "iv": 0.30,
            "oi": 2000,
            "delta": 0.25,
            "gamma": 0.04,
        },
    ]

    ranked = filter_and_score_pmcc_candidates(cfg, chain, quote)
    kept = ranked["kept"]
    assert len(kept) == 1
    assert kept[0]["short"]["strike"] == 105.0

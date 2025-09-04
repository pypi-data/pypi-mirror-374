"""Portfolio construction and optimization (Phase 4).

Initial scope:
- propose_allocation(): equal-weight allocation with per-name cap and count cap.
- optimize_portfolio_greedy(): risk/correlation-aware selection and equal-weighting
- monitor_portfolio(): detect violations and propose non-invasive actions

This module is deterministic and pure (no I/O).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pmcc.utils import is_number


def propose_allocation(
    cfg: dict[str, Any],
    candidates: Sequence[dict[str, Any]],
    capital: float,
    risk_limits: dict[str, Any],
) -> dict[str, Any]:
    """Propose an initial allocation from ranked candidates.

    Strategy:
    - Take top-N by score where N<=max_positions
    - Equal-weight across selected names
    - Clip each weight by max_weight_per_underlying
    - Allocate capital = weight * capital

    Returns: {status: str, proposal: [{ticker, weight, allocated_capital}]}
    """
    _ = cfg  # reserved for future strategies

    if not is_number(capital) or capital <= 0:
        return {"status": "block", "reason": "invalid_capital"}

    max_w = risk_limits.get("max_weight_per_underlying")
    max_n = risk_limits.get("max_positions")
    if not isinstance(max_n, int) or max_n <= 0:
        return {"status": "block", "reason": "invalid_risk_limits"}
    if not is_number(max_w):
        return {"status": "block", "reason": "invalid_risk_limits"}
    max_wf = float(max_w)

    # sanitize candidates
    valid: list[dict[str, Any]] = []
    for c in candidates:
        sym = c.get("symbol") or c.get("ticker")
        sc = c.get("score")
        if isinstance(sym, str) and is_number(sc):
            valid.append({"ticker": sym, "score": float(sc)})
    if not valid:
        return {"status": "block", "reason": "no_candidates"}

    # rank by score desc and take top-N
    valid.sort(key=lambda x: x["score"], reverse=True)
    selected = valid[:max_n]
    k = len(selected)

    eq_w = 1.0 / float(k)
    w = min(eq_w, max_wf)

    proposal = [
        {
            "ticker": s["ticker"],
            "weight": w,
            "allocated_capital": w * float(capital),
        }
        for s in selected
    ]

    return {"status": "ok", "proposal": proposal}


def propose_allocation_risk_balanced(
    cfg: dict[str, Any],
    candidates: Sequence[dict[str, Any]],
    capital: float,
    risk_limits: dict[str, Any],
) -> dict[str, Any]:
    """Propose allocation weighted by inverse risk among top-N by score.

    Strategy:
    - Rank candidates by score and keep top-N (N<=max_positions)
    - Compute raw weight ~ 1 / max(risk, epsilon)
    - Normalize raw weights to sum to 1.0, then cap per-name by max_weight
    - Optional redistribution: if cfg["redistribute_leftover"] is True, redistribute
      remaining weight (1 - sum(capped)) to names with headroom proportionally to
      their raw weights, respecting caps (water-filling). Otherwise, do not
      redistribute leftover after capping (sum may be < 1.0).

    Returns: {status: str, proposal: [{ticker, weight, allocated_capital}]}
    """
    if not is_number(capital) or capital <= 0:
        return {"status": "block", "reason": "invalid_capital"}

    max_w = risk_limits.get("max_weight_per_underlying")
    max_n = risk_limits.get("max_positions")
    if not isinstance(max_n, int) or max_n <= 0:
        return {"status": "block", "reason": "invalid_risk_limits"}
    if not is_number(max_w):
        return {"status": "block", "reason": "invalid_risk_limits"}
    max_wf = float(max_w)

    # sanitize candidates
    items: list[dict[str, Any]] = []
    for c in candidates:
        sym = c.get("symbol") or c.get("ticker")
        sc = c.get("score")
        rk = c.get("risk")
        if isinstance(sym, str) and is_number(sc) and is_number(rk):
            items.append({"ticker": sym, "score": float(sc), "risk": float(rk)})
    if not items:
        return {"status": "block", "reason": "no_candidates"}

    # Rank by score and take top-N
    items.sort(key=lambda x: x["score"], reverse=True)
    selected = items[:max_n]

    # Inverse-risk weighting
    eps = float(cfg.get("epsilon", 1e-6))
    bases = [1.0 / max(s["risk"], eps) for s in selected]
    total = sum(bases)
    if total <= 0.0:
        # fallback to equal weight if something pathological occurs
        k = float(len(selected))
        raw_weights = [1.0 / k for _ in selected]
    else:
        raw_weights = [b / total for b in bases]

    # Apply per-name cap and optional redistribution of leftover weight
    capped = [min(w, max_wf) for w in raw_weights]

    if bool(cfg.get("redistribute_leftover", False)):
        eps_w = 1e-12
        leftover = max(0.0, 1.0 - sum(capped))
        # Water-filling: distribute leftover among those with headroom
        while leftover > eps_w:
            eligible = [i for i, cw in enumerate(capped) if cw + eps_w < max_wf]
            if not eligible:
                break
            share_sum = sum(raw_weights[i] for i in eligible)
            progressed = False
            for i in eligible:
                share = raw_weights[i] / share_sum
                add = share * leftover
                headroom = max_wf - capped[i]
                delta = min(add, headroom)
                if delta > eps_w:
                    capped[i] += delta
                    progressed = True
            new_leftover = max(0.0, 1.0 - sum(capped))
            if not progressed or new_leftover >= leftover - eps_w:
                break
            leftover = new_leftover

    proposal = [
        {
            "ticker": s["ticker"],
            "weight": w,
            "allocated_capital": w * float(capital),
        }
        for s, w in zip(selected, capped, strict=True)
    ]

    return {"status": "ok", "proposal": proposal}


def _corr_lookup(pairs: Sequence[tuple[str, str, float]]) -> dict[tuple[str, str], float]:
    lut: dict[tuple[str, str], float] = {}
    for a, b, c in pairs:
        if isinstance(a, str) and isinstance(b, str) and is_number(c):
            v = float(c)
            lut[(a, b)] = v
            lut[(b, a)] = v
    return lut


def optimize_portfolio_greedy(
    cfg: dict[str, Any],
    candidates: Sequence[dict[str, Any]],
    pairwise_corr: Sequence[tuple[str, str, float]],
    capital: float,
    risk_limits: dict[str, Any],
) -> dict[str, Any]:
    """Greedy selection balancing score, risk, and pairwise correlation.

    Utility for a candidate i given current selection S:
        base = score_i - risk_aversion * risk_i
        corr_penalty = corr_penalty * avg_{j in S} corr(i, j)
        utility = base - corr_penalty

    Then equal-weight allocate across selected names, clipped by per-name cap.
    """
    if not is_number(capital) or capital <= 0:
        return {"status": "block", "reason": "invalid_capital"}

    max_w = risk_limits.get("max_weight_per_underlying")
    max_n = risk_limits.get("max_positions")
    if not isinstance(max_n, int) or max_n <= 0:
        return {"status": "block", "reason": "invalid_risk_limits"}
    if not is_number(max_w):
        return {"status": "block", "reason": "invalid_risk_limits"}
    max_wf = float(max_w)

    ra = float(cfg.get("risk_aversion", 0.5))
    cp = float(cfg.get("corr_penalty", 0.5))

    # sanitize candidates
    items: list[dict[str, Any]] = []
    for c in candidates:
        sym = c.get("symbol") or c.get("ticker")
        sc = c.get("score")
        rk = c.get("risk", 0.0)
        if isinstance(sym, str) and is_number(sc) and is_number(rk):
            items.append({"ticker": sym, "score": float(sc), "risk": float(rk)})
    if not items:
        return {"status": "block", "reason": "no_candidates"}

    # Precompute base utility
    for it in items:
        it["base"] = it["score"] - ra * it["risk"]

    corr = _corr_lookup(pairwise_corr)

    selected: list[dict[str, Any]] = []
    remaining = items.copy()

    while remaining and len(selected) < max_n:
        # Initialize best as the first remaining item (remaining is non-empty here)
        it0 = remaining[0]
        if not selected:
            best_u = it0["base"]
        else:
            avg_corr0 = 0.0
            for s in selected:
                avg_corr0 += corr.get((it0["ticker"], s["ticker"]), 0.0)
            avg_corr0 /= float(len(selected))
            best_u = it0["base"] - cp * avg_corr0
        best = it0

        for it in remaining[1:]:
            if not selected:
                u = it["base"]
            else:
                # average correlation to current selection
                avg_corr = 0.0
                for s in selected:
                    avg_corr += corr.get((it["ticker"], s["ticker"]), 0.0)
                avg_corr /= float(len(selected))
                u = it["base"] - cp * avg_corr
            if u > best_u:
                best_u = u
                best = it

        selected.append(best)
        remaining.remove(best)

    # selected is non-empty here by construction

    k = len(selected)
    eq_w = 1.0 / float(k)
    w = min(eq_w, max_wf)
    proposal = [
        {
            "ticker": s["ticker"],
            "weight": w,
            "allocated_capital": w * float(capital),
        }
        for s in selected
    ]

    return {"status": "ok", "proposal": proposal}


def monitor_portfolio(
    risk_limits: dict[str, Any],
    correlation_ctrl: dict[str, Any],
    positions: Sequence[dict[str, Any]],
    pairwise_corr: Sequence[tuple[str, str, float]],
) -> dict[str, Any]:
    """Detect overweight positions and high correlation pairs.

    Returns {status, actions}
    actions:
      - {action: "reduce_weight", ticker, current_weight, target_weight}
      - {action: "review_corr_pair", pair: (a,b), corr}
    """
    actions: list[dict[str, Any]] = []

    max_w = risk_limits.get("max_weight_per_underlying")
    if not is_number(max_w):
        return {"status": "block", "reason": "invalid_risk_limits"}
    max_wf = float(max_w)

    # overweight checks
    for p in positions:
        t = p.get("ticker")
        w = p.get("weight")
        if isinstance(t, str) and is_number(w):
            wf = float(w)
            if wf > max_wf:
                actions.append(
                    {
                        "action": "reduce_weight",
                        "ticker": t,
                        "current_weight": wf,
                        "target_weight": max_wf,
                    }
                )

    # correlation checks
    th = correlation_ctrl.get("max_pairwise")
    if is_number(th):
        thf = float(th)
        for a, b, c in pairwise_corr:
            if isinstance(a, str) and isinstance(b, str) and is_number(c):
                cf = float(c)
                if cf > thf:
                    actions.append(
                        {
                            "action": "review_corr_pair",
                            "pair": (a, b),
                            "corr": cf,
                        }
                    )

    # underweight (cash drag) check: suggest rebalance if total weight too low
    min_total = float(risk_limits.get("min_total_weight", 0.95))
    total_weight = 0.0
    for p in positions:
        w = p.get("weight")
        if is_number(w):
            total_weight += float(w)
    if total_weight < min_total:
        actions.append(
            {
                "action": "rebalance_underweight",
                "current_total_weight": total_weight,
                "target_total_weight": 1.0,
            }
        )

    status = "warn" if actions else "ok"
    return {"status": status, "actions": actions}

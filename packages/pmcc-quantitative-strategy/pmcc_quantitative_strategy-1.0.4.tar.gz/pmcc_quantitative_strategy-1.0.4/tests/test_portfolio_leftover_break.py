from __future__ import annotations

from pmcc.portfolio import propose_allocation_risk_balanced


def test_propose_allocation_redistribute_break_when_leftover_tiny():
    # 构造 raw 权重略微超过上限 0.5（超出量 < 1e-12），其余权重远低于上限，确保 eligible 非空
    # 目标 raw ≈ [0.5 + eps, 0.25, 0.25 - eps]，eps = 5e-13
    eps = 1.1e-12  # 略高于 eps_w=1e-12，确保进入 while 循环
    inv_w = [0.5 + eps, 0.25, 0.25 - eps]  # 归一化后直接作为 bases
    # 由 bases=1/risk 推出 risk
    risks = [1.0 / x for x in inv_w]

    candidates = [
        {"ticker": "AAA", "score": 1.0, "risk": risks[0]},
        {"ticker": "BBB", "score": 1.0, "risk": risks[1]},
        {"ticker": "CCC", "score": 1.0, "risk": risks[2]},
    ]

    cfg = {"redistribute_leftover": True}
    risk_limits = {"max_weight_per_underlying": 0.5, "max_positions": 3}

    out = propose_allocation_risk_balanced(cfg, candidates, capital=100_000.0, risk_limits=risk_limits)
    assert out["status"] == "ok"

    # 提取分配结果，验证：
    # 1) 第一只被 cap 到 0.5
    # 2) 总权重非常接近 1（仅小于 eps）
    # 3) 其他权重保持接近原始 raw（未发生有效 redistrib 进展）
    ws = {p["ticker"]: p["weight"] for p in out["proposal"]}
    assert abs(ws["AAA"] - 0.5) < 1e-15
    total_w = sum(ws.values())
    assert 1e-12 <= 1.0 - total_w < 2e-12
    assert abs(ws["BBB"] - inv_w[1]) < 1e-12
    assert abs(ws["CCC"] - inv_w[2]) < 1e-12

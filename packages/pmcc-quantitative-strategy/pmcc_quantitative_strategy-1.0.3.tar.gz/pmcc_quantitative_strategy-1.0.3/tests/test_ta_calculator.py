import json
from pathlib import Path

from pmcc.data import MockMarketDataProvider
from pmcc.ta import aggregate_divergence, compute_indicators

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TA_CFG = json.loads((PROJECT_ROOT / "config" / "technical_analysis.json").read_text(encoding="utf-8"))


def test_indicators_basic_shapes_and_ranges():
    p = MockMarketDataProvider()
    bars = p.get_ohlcv("AAPL", timeframe="1D", limit=200)
    div = TA_CFG["divergence"]

    ind = compute_indicators(bars, div)
    assert set(ind) == {"rsi", "macd"}

    rsi = ind["rsi"]
    macd = ind["macd"]
    assert isinstance(rsi, list) and len(rsi) == len(bars)
    assert isinstance(macd, dict)
    assert set(macd) == {"macd", "signal", "hist"}
    assert len(macd["macd"]) == len(bars)
    assert len(macd["signal"]) == len(bars)
    assert len(macd["hist"]) == len(bars)

    # RSI 范围 [0,100]
    assert all(0.0 <= x <= 100.0 for x in rsi)


def test_aggregate_divergence_weighting_and_event_scaling():
    p = MockMarketDataProvider()
    div = TA_CFG["divergence"]

    bars_by_tf = {}
    for tf in div["timeframes"]:
        bars_by_tf[tf] = p.get_ohlcv("QQQ", timeframe=tf, limit=240)

    s0 = aggregate_divergence(bars_by_tf, TA_CFG, in_event_window=False)
    se = aggregate_divergence(bars_by_tf, TA_CFG, in_event_window=True)

    assert 0.0 <= s0 <= 1.0
    assert 0.0 <= se <= 1.0
    assert se <= s0  # 事件窗缩放不应放大


def test_aggregate_is_deterministic_with_mock_provider():
    p = MockMarketDataProvider()
    div = TA_CFG["divergence"]

    bars_by_tf = {tf: p.get_ohlcv("SPY", timeframe=tf, limit=180) for tf in div["timeframes"]}
    s1 = aggregate_divergence(bars_by_tf, TA_CFG, in_event_window=False)
    s2 = aggregate_divergence(bars_by_tf, TA_CFG, in_event_window=False)
    assert s1 == s2


def test_aggregate_handles_empty_bars_gracefully():
    div = TA_CFG["divergence"]
    # 一个周期为空应当贡献 0 分，不报错
    some_tf = div["timeframes"][0]
    other = div["timeframes"][1]
    p = MockMarketDataProvider()
    bars_by_tf = {some_tf: [], other: p.get_ohlcv("DIA", timeframe=other, limit=120)}

    s = aggregate_divergence(bars_by_tf, TA_CFG, in_event_window=False)
    assert 0.0 <= s <= 1.0

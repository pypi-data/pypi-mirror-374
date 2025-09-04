import pytest

from pmcc.data import MockMarketDataProvider
from pmcc.filters import filter_abnormal_quote


def test_filter_abnormal_quote_by_last_vs_mid_deviation():
    p = MockMarketDataProvider()
    q = p.get_quote("AAPL")

    # Normal case: deviation small, should be kept
    res_ok = filter_abnormal_quote({"max_last_mid_dev_ratio": 0.02}, [q])
    assert len(res_ok["kept"]) == 1 and len(res_ok["dropped"]) == 0

    # Abnormal: force last far away from mid
    q_bad = dict(q)
    q_bad["last"] = q["ask"] * 1.2
    res_bad = filter_abnormal_quote({"max_last_mid_dev_ratio": 0.02}, [q_bad])
    assert len(res_bad["kept"]) == 0 and len(res_bad["dropped"]) == 1

    # Invalid fields: non-number or inverted book -> dropped
    q_inv = dict(q)
    q_inv["bid"], q_inv["ask"] = q_inv["ask"], q_inv["bid"]  # inverted
    res_inv = filter_abnormal_quote({"max_last_mid_dev_ratio": 0.02}, [q_inv])
    assert len(res_inv["kept"]) == 0 and len(res_inv["dropped"]) == 1


def test_filter_abnormal_requires_number():
    p = MockMarketDataProvider()
    q = p.get_quote("MSFT")
    with pytest.raises(ValueError):
        filter_abnormal_quote({"max_last_mid_dev_ratio": "bad"}, [q])

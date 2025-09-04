from __future__ import annotations

from dataclasses import asdict

import pmcc.contracts as c


def test_pagination_and_batch_contracts_shape():
    pr = c.PageRequest(cursor=None, limit=200)
    pi = c.PageInfo(next_cursor="abc", total=1234)
    sr = c.SymbolsRequest(symbols=["SPY", "QQQ"])
    mq = c.MultiQuote(quotes=[c.Quote(symbol="SPY", bid=1, ask=2, last=1.5, ts=1)], page=pi)
    assert pr.limit == 200 and pi.next_cursor == "abc" and len(sr.symbols) == 2
    d = asdict(mq)
    assert isinstance(d["quotes"], list) and d["page"]["next_cursor"] == "abc"


def test_error_detail_helper_shapes():
    rl = c.RateLimitDetail(retry_after=0.5, bucket="global")
    ve = c.ValidationErrorDetail(field="symbol", message="required", location="body")
    ne = c.NetworkErrorDetail(status_code=504, endpoint="/quotes")
    assert rl.retry_after > 0 and ve.field == "symbol" and ne.status_code == 504

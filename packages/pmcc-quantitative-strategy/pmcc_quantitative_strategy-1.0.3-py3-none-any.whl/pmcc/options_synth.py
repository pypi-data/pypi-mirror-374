from __future__ import annotations

from dataclasses import dataclass

from pmcc.contracts import APIResult, OptionChainRequest, OptionContract
from pmcc.data import MockMarketDataProvider
from pmcc.providers import OptionsProvider


@dataclass
class SyntheticOptionsProvider(OptionsProvider):
    mkt: MockMarketDataProvider

    def get_chain(self, req: OptionChainRequest) -> APIResult[list[OptionContract]]:
        sym = req.symbol
        q = self.mkt.get_quote(sym)
        under = float(q["last"]) if isinstance(q, dict) else 100.0
        # build 10 strikes around under
        strikes = [round(under * (0.9 + 0.02 * i), 2) for i in range(10)]
        out: list[OptionContract] = []
        for i, k in enumerate(strikes):
            dte = 20 + i * 5
            bid = max(0.01, round(0.02 * under * (10 - i) / 10.0, 2))
            ask = round(bid * 1.1, 2)
            iv = round(0.2 + 0.01 * i, 3)
            oi = 1000 + i * 50
            delta = round(0.1 + 0.05 * i, 3)
            gamma = round(0.01 + 0.001 * i, 4)
            out.append(
                OptionContract(
                    symbol=sym,
                    type="C",
                    dte=dte,
                    strike=float(k),
                    bid=float(bid),
                    ask=float(ask),
                    last=float((bid + ask) / 2.0),
                    iv=float(iv),
                    oi=int(oi),
                    delta=float(min(delta, 0.99)),
                    gamma=float(gamma),
                )
            )
        return APIResult(ok=True, data=out)

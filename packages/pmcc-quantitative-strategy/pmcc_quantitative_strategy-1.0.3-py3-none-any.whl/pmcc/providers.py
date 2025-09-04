from __future__ import annotations

from typing import Protocol, runtime_checkable

from pmcc.contracts import (
    APIResult,
    ApprovalDecision,
    ApprovalRequest,
    ExecutionPlan,
    MultiQuote,
    OptionChainRequest,
    OptionContract,
    PretradeResult,
    Quote,
    QuoteRequest,
    SymbolsRequest,
)


@runtime_checkable
class MarketDataProvider(Protocol):
    def get_quote(self, req: QuoteRequest) -> APIResult[Quote]: ...

    def get_quotes(self, req: SymbolsRequest) -> APIResult[MultiQuote]: ...


@runtime_checkable
class OptionsProvider(Protocol):
    def get_chain(self, req: OptionChainRequest) -> APIResult[list[OptionContract]]: ...


@runtime_checkable
class ExecutionPlanner(Protocol):
    def plan(self, cfgs: dict) -> APIResult[ExecutionPlan]: ...


@runtime_checkable
class PretradeChecks(Protocol):
    def run(self, cfgs: dict, context: dict) -> APIResult[PretradeResult]: ...


@runtime_checkable
class ApprovalService(Protocol):
    def request(self, req: ApprovalRequest) -> APIResult[ApprovalDecision]: ...

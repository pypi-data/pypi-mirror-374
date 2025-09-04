from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Generic, TypeVar


class PMCCErrorCode(str, Enum):
    CONFIG_ERROR = "CONFIG_ERROR"
    SCHEMA_ERROR = "SCHEMA_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT = "RATE_LIMIT"
    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"
    PRECHECK_BLOCKED = "PRECHECK_BLOCKED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


@dataclass
class APIError:
    code: PMCCErrorCode
    message: str
    detail: Mapping[str, Any] | None = None


T = TypeVar("T")


@dataclass
class APIResult(Generic[T]):
    ok: bool
    data: T | None = None
    error: APIError | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# -------- Data layer (read-only) contracts --------


@dataclass
class QuoteRequest:
    symbol: str


@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    last: float
    ts: int


@dataclass
class OptionChainRequest:
    symbol: str
    dte_min: int | None = None
    dte_max: int | None = None


@dataclass
class OptionContract:
    symbol: str
    type: str  # "C" or "P"
    dte: int
    strike: float
    bid: float
    ask: float
    last: float
    iv: float
    oi: int
    delta: float
    gamma: float


# -------- Execution planning (dry-run) contracts --------


@dataclass
class PreCheckDetail:
    name: str
    description: str
    applies: bool


@dataclass
class ExecutionPlan:
    order_template: str
    pre_checks: Sequence[str]
    pre_checks_verbose: Sequence[str]
    pre_checks_detail: Sequence[PreCheckDetail]


@dataclass
class PretradeResult:
    ok: bool
    reasons: Sequence[str]
    details: Mapping[str, Any]


# -------- Approval workflow contracts (dry-run stage) --------


@dataclass
class ApprovalRequest:
    plan_id: str
    summary: Mapping[str, Any]
    requested_by: str


@dataclass
class ApprovalDecision:
    approved: bool
    approver: str
    comment: str | None = None


# -------- Pagination & batch contracts --------


@dataclass
class PageRequest:
    cursor: str | None = None
    limit: int | None = None


@dataclass
class PageInfo:
    next_cursor: str | None = None
    total: int | None = None


@dataclass
class SymbolsRequest:
    symbols: Sequence[str]


@dataclass
class MultiQuote:
    quotes: Sequence[Quote]
    page: PageInfo | None = None


# -------- Standard error detail helpers (optional shapes) --------


@dataclass
class RateLimitDetail:
    retry_after: float
    bucket: str | None = None


@dataclass
class ValidationErrorDetail:
    field: str
    message: str
    location: str | None = None  # e.g., "body", "query"


@dataclass
class NetworkErrorDetail:
    status_code: int | None = None
    endpoint: str | None = None

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pmcc.contracts import (
    APIError,
    APIResult,
    ApprovalDecision,
    ApprovalRequest,
    PMCCErrorCode,
)


class InMemoryApprovalService:
    def request(self, req: ApprovalRequest) -> APIResult[ApprovalDecision]:
        # Minimal rule: approve if caller indicates pretrade ok in summary
        summ = dict(req.summary or {})
        pre_ok = bool(summ.get("pretrade_ok", True))
        dec = ApprovalDecision(approved=pre_ok, approver="auto", comment=None if pre_ok else "pretrade_failed")
        return APIResult(ok=True, data=dec)


class ApprovalFileService:
    def __init__(self, log_path: str | Path) -> None:
        self.path = Path(log_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # rotation thresholds via ENV (bytes) and keep count
        try:
            self._max_bytes = int(os.environ.get("PMCC_APPROVAL_MAX_BYTES", "5242880").strip())  # 5MB default
        except Exception:
            self._max_bytes = 5 * 1024 * 1024
        try:
            self._rotate_keep = int(os.environ.get("PMCC_APPROVAL_ROTATE_KEEP", "1").strip())
        except Exception:
            self._rotate_keep = 1

    def request(self, req: ApprovalRequest) -> APIResult[ApprovalDecision]:
        # auto-approve by pretrade_ok, record to file
        pre_ok = bool(dict(req.summary or {}).get("pretrade_ok", True))
        dec = ApprovalDecision(approved=pre_ok, approver="auto", comment=None if pre_ok else "pretrade_failed")
        rec = {"request": asdict(req), "decision": asdict(dec)}
        try:
            # rotate if exceeds max_bytes (simple single-suffix scheme: .1, .2, ... up to keep)
            if self._max_bytes > 0 and self.path.exists() and self.path.stat().st_size >= self._max_bytes:
                # delete oldest
                for k in range(self._rotate_keep, 0, -1):
                    bk = self.path.with_suffix(self.path.suffix + f".{k}")
                    nbk = self.path.with_suffix(self.path.suffix + f".{k+1}")
                    if bk.exists():
                        if k >= self._rotate_keep:
                            from contextlib import suppress

                            with suppress(Exception):
                                bk.unlink()
                        else:
                            from contextlib import suppress

                            with suppress(Exception):
                                if nbk.exists():
                                    nbk.unlink()
                            with suppress(Exception):
                                bk.rename(nbk)
                # rotate current to .1
                from contextlib import suppress

                with suppress(Exception):
                    self.path.rename(self.path.with_suffix(self.path.suffix + ".1"))

            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception as e:  # noqa: BLE001
            return APIResult(ok=False, error=APIError(code=PMCCErrorCode.NETWORK_ERROR, message=str(e)))
        return APIResult(ok=True, data=dec)

    def replay_last(self, n: int = 1) -> list[dict[str, Any]]:
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []
        out: list[dict[str, Any]] = []
        for line in lines[-n:]:
            try:
                out.append(json.loads(line))
            except Exception:  # noqa: PERF203  # nosec B112 - tolerant replay for partially written lines
                continue
        return out


class HTTPApprovalService:
    """HTTP-based approval service adapter (dry-run stage).

    Sends a POST with ApprovalRequest JSON and expects a JSON body containing
    {approved: bool, approver: str, comment?: str}. Does not raise; maps
    transport and non-2xx responses to NETWORK_ERROR.
    """

    def __init__(self, url: str, timeout: float = 5.0, *, retries: int = 0, base_delay: float = 0.1) -> None:
        self.url = str(url)
        self.timeout = float(timeout)
        self.retries = int(max(0, retries))
        self.base_delay = float(max(0.0, base_delay))

    def request(self, req: ApprovalRequest) -> APIResult[ApprovalDecision]:
        try:
            import importlib

            _rq = importlib.import_module("requests")
        except Exception as e:  # noqa: BLE001
            return APIResult(
                ok=False, error=APIError(code=PMCCErrorCode.NETWORK_ERROR, message=f"requests missing: {e}")
            )
        from pmcc.retry import retry_with_backoff

        class _HTTPStatusError(RuntimeError):
            def __init__(self, status: int):
                super().__init__(f"http status {status}")
                self.status = int(status)

        def _call():
            r = _rq.post(self.url, json=asdict(req), timeout=self.timeout)
            status = int(getattr(r, "status_code", 0))
            if 200 <= status < 300:
                try:
                    body = r.json()
                except Exception:
                    body = {}
                approved = bool(body.get("approved", False))
                approver = str(body.get("approver", "http"))
                comment = body.get("comment")
                return ApprovalDecision(approved=approved, approver=approver, comment=comment)
            raise _HTTPStatusError(status)

        try:
            dec = retry_with_backoff(_call, retries=self.retries, base_delay=self.base_delay, sleep=lambda _s: None)
            return APIResult(ok=True, data=dec)
        except _HTTPStatusError as e:  # type: ignore[unused-ignore]
            return APIResult(
                ok=False,
                error=APIError(
                    code=PMCCErrorCode.NETWORK_ERROR,
                    message=str(e),
                    detail={"status_code": int(getattr(e, "status", 0)), "attempts": self.retries + 1},
                ),
            )
        except Exception as e:  # noqa: BLE001
            err_detail: dict[str, object] = {"attempts": self.retries + 1}
            try:
                _exc = getattr(_rq, "exceptions", None)
                timeout_cls = getattr(_exc, "Timeout", ()) if _exc else ()
                conn_cls = getattr(_exc, "ConnectionError", ()) if _exc else ()
                if isinstance(e, timeout_cls):
                    err_detail["error"] = "timeout"
                elif isinstance(e, conn_cls):
                    err_detail["error"] = "connection"
            except Exception:  # nosec B110 - best-effort mapping for requests exceptions presence
                pass
            return APIResult(
                ok=False, error=APIError(code=PMCCErrorCode.NETWORK_ERROR, message=str(e), detail=err_detail)
            )


class ApprovalS3Service:
    """S3-backed approval recorder (append-as-objects, best-effort).

    Each request/decision pair is uploaded as an individual JSON object.
    This avoids non-atomic append-on-object issues and works with minimal
    permissions (PutObject only on a given prefix). Intended for audit storage.
    """

    def __init__(
        self,
        bucket: str,
        *,
        prefix: str | None = None,
        kms_key_id: str | None = None,
    ) -> None:
        if not bucket:
            raise ValueError("bucket is required")
        self.bucket = bucket
        self.prefix = (prefix or "approvals").strip("/")
        self.kms_key_id = kms_key_id
        # lazy boto3 import via importlib to keep mypy and optional deps clean
        import importlib

        self._boto3 = importlib.import_module("boto3")
        self._uuid4 = __import__("uuid").uuid4
        self._time = __import__("time").time

    def _key(self) -> str:
        ts = int(self._time())
        uid = str(self._uuid4())
        return f"{self.prefix}/{ts}-{uid}.json"

    def request(self, req: ApprovalRequest) -> APIResult[ApprovalDecision]:
        pre_ok = bool(dict(req.summary or {}).get("pretrade_ok", True))
        dec = ApprovalDecision(approved=pre_ok, approver="auto", comment=None if pre_ok else "pretrade_failed")
        rec = {"request": asdict(req), "decision": asdict(dec)}
        body = json.dumps(rec, ensure_ascii=False).encode("utf-8")
        key = self._key()
        try:
            client = self._boto3.client("s3")
            extra: dict[str, Any] = {"ServerSideEncryption": "aws:kms"} if self.kms_key_id else {}
            if self.kms_key_id:
                extra["SSEKMSKeyId"] = self.kms_key_id
            client.put_object(Bucket=self.bucket, Key=key, Body=body, ContentType="application/json", **extra)
        except Exception as e:  # noqa: BLE001
            return APIResult(
                ok=False,
                error=APIError(
                    code=PMCCErrorCode.NETWORK_ERROR,
                    message=str(e),
                    detail={"bucket": self.bucket, "key": key},
                ),
            )
        return APIResult(ok=True, data=dec)

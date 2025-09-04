from __future__ import annotations

from dataclasses import asdict

import pmcc.contracts as c
import pmcc.providers as p


class DummyApproval:
    def request(self, req: c.ApprovalRequest) -> c.APIResult[c.ApprovalDecision]:
        dec = c.ApprovalDecision(approved=True, approver="ops", comment="ok")
        return c.APIResult(ok=True, data=dec)


def test_approval_contract_shapes_and_protocol():
    req = c.ApprovalRequest(plan_id="p1", summary={"k": 1}, requested_by="ai")
    dec = c.ApprovalDecision(approved=False, approver="ops", comment=None)
    assert asdict(req)["plan_id"] == "p1" and dec.approver == "ops"

    svc = DummyApproval()
    assert isinstance(svc, p.ApprovalService)
    res = svc.request(req)
    assert res.ok and res.data and res.data.approved is True

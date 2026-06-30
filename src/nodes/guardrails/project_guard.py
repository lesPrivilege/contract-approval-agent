"""Project guard — block if linked project hasn't passed investment review."""

import time

from src.state import AuditEntry, ContractState, ContractStatus, GuardrailResult
from src.tools import check_project_approved


def project_guard(state: ContractState) -> dict:
    """Check if the linked project has been approved."""
    start = time.time()
    contract = state.contract

    approved = check_project_approved(contract.关联项目id)
    duration = int((time.time() - start) * 1000)

    result = GuardrailResult(
        guard_name="project_guard",
        passed=approved,
        reason=None if approved else f"关联项目 {contract.关联项目id} 未通过评审",
    )

    audit = AuditEntry(
        node="guardrail",
        action="check_project",
        input_summary=f"项目ID: {contract.关联项目id}",
        output_summary="项目已通过" if approved else "项目未通过",
        decision="passed" if approved else "blocked",
        duration_ms=duration,
    )

    updates = {
        "project_approved": approved,
        "guardrail_results": state.guardrail_results + [result],
        "audit_log": state.audit_log + [audit],
    }

    if not approved:
        updates["status"] = ContractStatus.BLOCKED
        updates["block_reason"] = result.reason
        updates["current_step"] = "blocked"

    return updates

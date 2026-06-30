"""Isolation guard — block cross-business contracts that need compliance review."""

import time

from src.state import AuditEntry, ContractState, ContractStatus, GuardrailResult
from src.tools import check_cross_business


def isolation_guard(state: ContractState) -> dict:
    """Check if contract crosses regulated business boundaries."""
    start = time.time()
    contract = state.contract

    is_cross = check_cross_business(contract.model_dump())
    duration = int((time.time() - start) * 1000)

    # Cross-business contracts need compliance review — block for demo
    passed = not is_cross

    result = GuardrailResult(
        guard_name="isolation_guard",
        passed=passed,
        reason=None if passed else "跨业务合同需合规审查，已阻断",
    )

    audit = AuditEntry(
        node="guardrail",
        action="check_isolation",
        input_summary=f"跨业务标记: {is_cross}",
        output_summary="通过" if passed else "阻断: 需合规审查",
        decision="passed" if passed else "blocked",
        duration_ms=duration,
    )

    updates = {
        "is_cross_business": is_cross,
        "guardrail_results": state.guardrail_results + [result],
        "audit_log": state.audit_log + [audit],
    }

    if not passed:
        updates["status"] = ContractStatus.BLOCKED
        updates["block_reason"] = result.reason
        updates["current_step"] = "blocked"

    return updates

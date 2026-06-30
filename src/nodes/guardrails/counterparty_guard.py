"""Counterparty guard — block contracts with blacklisted or high-risk counterparties."""

import time

from src.state import AuditEntry, ContractState, ContractStatus, GuardrailResult


def counterparty_guard(state: ContractState) -> dict:
    """Check if counterparty is blacklisted or has poor credit."""
    start = time.time()
    contract = state.contract

    status = contract.条款标记.get("对方状态", "正常")
    passed = status not in ("黑名单", "资信不良")

    result = GuardrailResult(
        guard_name="counterparty_guard",
        passed=passed,
        reason=None if passed else f"交易对方标记为「{status}」，签约前需完成资信审查",
    )

    audit = AuditEntry(
        node="guardrail",
        action="check_counterparty",
        input_summary=f"对方状态: {status}",
        output_summary="通过" if passed else f"阻断: {status}",
        decision="passed" if passed else "blocked",
        duration_ms=int((time.time() - start) * 1000),
    )

    updates = {
        "guardrail_results": state.guardrail_results + [result],
        "audit_log": state.audit_log + [audit],
    }

    if not passed:
        updates["status"] = ContractStatus.BLOCKED
        updates["block_reason"] = result.reason
        updates["current_step"] = "blocked"

    return updates

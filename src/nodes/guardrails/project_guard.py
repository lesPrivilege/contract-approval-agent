"""Project guard — block if linked project hasn't passed investment review or exceeds budget."""

import time

from src.state import AuditEntry, ContractState, ContractStatus, GuardrailResult
from src.tools import check_project_approved, get_project_budget


def project_guard(state: ContractState) -> dict:
    """Check if the linked project has been approved and contract is within budget."""
    start = time.time()
    contract = state.contract

    approved = check_project_approved(contract.关联项目id)
    duration = int((time.time() - start) * 1000)

    if not approved:
        result = GuardrailResult(
            guard_name="project_guard",
            passed=False,
            reason=f"关联项目 {contract.关联项目id} 未通过评审",
        )
        audit = AuditEntry(
            node="guardrail",
            action="check_project",
            input_summary=f"项目ID: {contract.关联项目id}",
            output_summary="项目未通过",
            decision="blocked",
            duration_ms=duration,
        )
        updates = {
            "project_approved": False,
            "guardrail_results": state.guardrail_results + [result],
            "audit_log": state.audit_log + [audit],
            "status": ContractStatus.BLOCKED,
            "block_reason": result.reason,
            "current_step": "blocked",
        }
        return updates

    # Project approved — check budget ceiling
    budget = get_project_budget(contract.关联项目id)
    if budget is not None and contract.金额 > budget:
        result = GuardrailResult(
            guard_name="project_guard",
            passed=False,
            reason=f"合同金额 ¥{contract.金额:,} 超投资评审批复预算上限 ¥{budget:,}",
        )
        audit = AuditEntry(
            node="guardrail",
            action="check_project_budget",
            input_summary=f"项目ID: {contract.关联项目id}, 合同金额: ¥{contract.金额:,}, 预算上限: ¥{budget:,}",
            output_summary="超预算上限",
            decision="blocked",
            duration_ms=duration,
        )
        updates = {
            "project_approved": True,
            "guardrail_results": state.guardrail_results + [result],
            "audit_log": state.audit_log + [audit],
            "status": ContractStatus.BLOCKED,
            "block_reason": result.reason,
            "current_step": "blocked",
        }
        return updates

    # Both approved and within budget
    result = GuardrailResult(
        guard_name="project_guard",
        passed=True,
        reason=None,
    )
    audit = AuditEntry(
        node="guardrail",
        action="check_project",
        input_summary=f"项目ID: {contract.关联项目id}",
        output_summary="项目已通过，预算合规",
        decision="passed",
        duration_ms=duration,
    )
    return {
        "project_approved": True,
        "guardrail_results": state.guardrail_results + [result],
        "audit_log": state.audit_log + [audit],
    }

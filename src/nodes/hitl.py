"""HITL node — pause for human approval via interrupt()."""

import time

from langgraph.types import interrupt

from src.state import AuditEntry, ContractState, ContractStatus
from src.tools import needs_hitl


def hitl_node(state: ContractState) -> dict:
    """Check if HITL is needed; if so, pause and wait for human decision."""
    start = time.time()
    contract = state.contract

    # Check if this contract needs human approval
    required = needs_hitl(contract.板块, contract.合同类型, contract.金额)

    # Also check for irreversible clauses
    has_irreversible = contract.条款标记.get("不可逆", False)
    has_guarantee = contract.条款标记.get("担保", False)

    if required or has_irreversible or has_guarantee:
        # Build reason
        reasons = []
        if required:
            reasons.append(f"金额 ¥{contract.金额:,} 超过自动审批阈值")
        if has_irreversible:
            reasons.append("包含不可撤销条款")
        if has_guarantee:
            reasons.append("包含担保条款")
        reason = "; ".join(reasons)

        # Build payload for human reviewer
        payload = {
            "contract_id": contract.id,
            "board": contract.板块,
            "contract_type": contract.合同类型,
            "amount": contract.金额,
            "approval_chain": state.approval_chain,
            "risks": state.risks,
            "reason": reason,
            "question": "请审批此合同",
        }

        # Pause — this returns when human resumes with Command(resume=...)
        decision = interrupt(payload)

        duration = int((time.time() - start) * 1000)

        audit = AuditEntry(
            node="hitl",
            action="human_review",
            input_summary=f"需人工确认: {reason}",
            output_summary=f"人工决策: {decision}",
            decision=str(decision),
            duration_ms=duration,
        )

        if decision in ("approved", "approve", True):
            return {
                "human_decision": "approved",
                "status": ContractStatus.APPROVED,
                "current_step": "approved",
                "audit_log": state.audit_log + [audit],
            }
        else:
            return {
                "human_decision": "rejected",
                "status": ContractStatus.REJECTED,
                "current_step": "rejected",
                "audit_log": state.audit_log + [audit],
            }
    else:
        # No HITL needed — auto-approve
        duration = int((time.time() - start) * 1000)

        audit = AuditEntry(
            node="hitl",
            action="auto_approve",
            input_summary="无需人工确认",
            output_summary="自动通过",
            decision="auto_approved",
            duration_ms=duration,
        )

        return {
            "human_decision": "auto_approved",
            "status": ContractStatus.APPROVED,
            "current_step": "approved",
            "audit_log": state.audit_log + [audit],
        }

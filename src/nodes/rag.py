"""RAG node — retrieve SOP/template for the contract type."""

import time

from src.state import AuditEntry, ContractState, ContractStatus
from src.tools import get_sop


def rag_node(state: ContractState) -> dict:
    """Retrieve SOP template for this contract type."""
    start = time.time()
    contract = state.contract

    sop = get_sop(contract.合同类型)
    sop_missing = sop is None

    duration = int((time.time() - start) * 1000)

    audit = AuditEntry(
        node="rag",
        action="retrieve_sop",
        input_summary=f"合同类型: {contract.合同类型}",
        output_summary="SOP 已检索" if not sop_missing else "SOP 未找到",
        decision="found" if not sop_missing else "missing",
        duration_ms=duration,
    )

    result = {
        "current_step": "retrieved",
        "status": ContractStatus.RETRIEVED,
        "sop_missing": sop_missing,
        "audit_log": state.audit_log + [audit],
    }
    if sop:
        result["sop_content"] = sop
    return result

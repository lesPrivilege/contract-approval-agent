"""Route node — look up approval chain from the matrix."""

import time

from src.state import AuditEntry, ContractState, ContractStatus
from src.tools import get_approval_chain


def route_node(state: ContractState) -> dict:
    """Look up the approval chain for this contract."""
    start = time.time()
    contract = state.contract

    chain = get_approval_chain(contract.板块, contract.合同类型, contract.金额, contract.合同成熟度)
    if chain is None:
        chain = ["（未找到匹配的审批链）"]

    duration = int((time.time() - start) * 1000)

    audit = AuditEntry(
        node="route",
        action="lookup_approval_chain",
        input_summary=f"{contract.板块}-{contract.合同类型}, ¥{contract.金额:,}",
        output_summary=f"审批链: {' → '.join(chain)}",
        decision="routed",
        duration_ms=duration,
    )

    return {
        "approval_chain": chain,
        "current_step": "routed",
        "status": ContractStatus.ROUTED,
        "audit_log": state.audit_log + [audit],
    }

"""Triage node — classify contract board and type.

Uses rule-based lookup for known types, LLM fallback for ambiguous cases.
"""

import time

from src.state import ContractState


def triage_node(state: ContractState) -> dict:
    """Classify contract — rule-first, LLM fallback for unknown types."""
    start = time.time()
    contract = state.contract

    # Rule-based: board and type are already structured in our data
    # In a real system, this would handle NLP input from user
    known_boards = {"A", "B", "C", "D"}
    known_types = {"采购类", "服务类", "工程类", "担保类"}

    board = contract.板块
    ctype = contract.合同类型
    method = "rule"

    if board not in known_boards or ctype not in known_types:
        # LLM fallback — would call LLM here in production
        method = "llm_fallback"
        # For demo, keep original values
        pass

    duration = int((time.time() - start) * 1000)
    from src.state import AuditEntry, ContractStatus

    audit = AuditEntry(
        node="triage",
        action="classify",
        input_summary=f"合同 {contract.id}: {board}-{ctype}",
        output_summary=f"板块={board}, 类型={ctype}, 方法={method}",
        decision="classified",
        duration_ms=duration,
    )

    return {
        "current_step": "triaged",
        "status": ContractStatus.TRIAGED,
        "audit_log": state.audit_log + [audit],
    }

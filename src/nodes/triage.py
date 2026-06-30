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
    known_boards = {"燃气", "综合能源", "智慧家居", "行政"}
    known_types = {"设备采购", "供气设施安装", "运营维保", "工程施工", "能源管理", "借款担保", "社区服务"}

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

"""Clause extraction node — LLM-powered semantic extraction from contract descriptions."""

import time

from src.config import get_llm
from src.state import (
    AuditEntry,
    ClauseExtraction,
    ContractInfo,
    ContractState,
    ContractStatus,
)


def clause_extraction_node(state: ContractState) -> dict:
    """Extract clause flags from free-text description using LLM.

    Skips if 条款描述 is empty (preserves deterministic path for existing tests).
    """
    start = time.time()
    contract = state.contract

    # Skip if no free text — keep existing hand-written flags
    if not contract.条款描述:
        duration = int((time.time() - start) * 1000)
        audit = AuditEntry(
            node="clause_extraction",
            action="skip",
            input_summary="条款描述为空，跳过 LLM 抽取",
            output_summary="沿用已有标记",
            decision="skipped",
            duration_ms=duration,
        )
        return {
            "current_step": "clause_extracted",
            "audit_log": state.audit_log + [audit],
        }

    # Call LLM with structured output
    llm = get_llm().with_structured_output(ClauseExtraction)
    result = llm.invoke(
        f"请从以下合同条款描述中提取风险标记。\n\n"
        f"合同ID: {contract.id}\n"
        f"板块: {contract.板块}\n"
        f"合同类型: {contract.合同类型}\n"
        f"金额: {contract.金额:,}元\n\n"
        f"条款描述:\n{contract.条款描述}"
    )

    # Build updated contract info with LLM extraction results
    updated_contract = contract.model_copy(update={
        "条款标记": {
            "不可逆": result.不可逆,
            "担保": result.担保,
            "跨业务": result.跨业务,
        },
        "关联方标记": result.关联方标记,
        "对方状态": result.对方状态,
    })

    # Check confidence
    low_confidence = result.confidence < 0.8

    duration = int((time.time() - start) * 1000)

    summary_parts = [
        f"不可逆={result.不可逆}",
        f"担保={result.担保}",
        f"跨业务={result.跨业务}",
        f"关联方={result.关联方标记}",
        f"对方状态={result.对方状态}",
        f"置信度={result.confidence:.2f}",
    ]

    audit = AuditEntry(
        node="clause_extraction",
        action="llm_extract",
        input_summary=f"条款描述: {contract.条款描述[:60]}...",
        output_summary=", ".join(summary_parts),
        decision="low_confidence" if low_confidence else "extracted",
        duration_ms=duration,
    )

    updates = {
        "contract": updated_contract,
        "current_step": "clause_extracted",
        "extraction_low_confidence": low_confidence,
        "audit_log": state.audit_log + [audit],
    }

    return updates

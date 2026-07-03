"""Triage node — classify contract board and type.

Uses rule-based lookup for known types, LLM fallback for ambiguous cases.
"""

import time

from src.config import get_llm
from src.state import AuditEntry, ContractState, ContractStatus, TriageClassification


KNOWN_BOARDS = {"A", "B", "C", "D"}
KNOWN_TYPES = {"采购类", "服务类", "工程类", "担保类", "投资合作类"}


def _duration_ms(start: float) -> int:
    return max(1, int((time.perf_counter() - start) * 1000))


def _usage_from_response(response) -> dict:
    usage = getattr(response, "usage_metadata", None) or {}
    if not usage:
        response_metadata = getattr(response, "response_metadata", {}) or {}
        usage = response_metadata.get("token_usage", {}) or {}
    return {
        "prompt_tokens": usage.get("input_tokens") or usage.get("prompt_tokens"),
        "completion_tokens": usage.get("output_tokens") or usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


def _llm_classify(contract) -> tuple[TriageClassification, dict]:
    llm = get_llm().with_structured_output(TriageClassification, include_raw=True)
    response = llm.invoke(
        "请将以下合同分类到板块 A/B/C/D 和合同类型。\n\n"
        "可选合同类型：采购类、服务类、工程类、担保类、投资合作类。\n"
        "如果原字段模糊或不在枚举中，请根据说明和条款语义选择最接近的类型。\n\n"
        f"合同ID: {contract.id}\n"
        f"原板块: {contract.板块}\n"
        f"原合同类型: {contract.合同类型}\n"
        f"金额: {contract.金额:,}元\n"
        f"说明: {contract.说明}\n"
        f"条款描述: {contract.条款描述 or '无'}"
    )
    parsed = response["parsed"]
    usage = _usage_from_response(response.get("raw"))
    return parsed, usage


def triage_node(state: ContractState) -> dict:
    """Classify contract — rule-first, LLM fallback for unknown types."""
    start = time.perf_counter()
    contract = state.contract

    board = contract.板块
    ctype = contract.合同类型
    method = "rule"
    confidence = None
    token_usage = {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}

    if board not in KNOWN_BOARDS or ctype not in KNOWN_TYPES:
        method = "llm_fallback"
        classification, token_usage = _llm_classify(contract)
        board = classification.板块
        ctype = classification.合同类型
        confidence = classification.confidence
        contract = contract.model_copy(update={"板块": board, "合同类型": ctype})

    summary = f"板块={board}, 类型={ctype}, 方法={method}"
    if confidence is not None:
        summary += f", 置信度={confidence:.2f}"

    audit = AuditEntry(
        node="triage",
        action="classify",
        input_summary=f"合同 {state.contract.id}: {state.contract.板块}-{state.contract.合同类型}",
        output_summary=summary,
        decision="classified",
        duration_ms=_duration_ms(start),
        **token_usage,
    )

    return {
        "contract": contract,
        "current_step": "triaged",
        "status": ContractStatus.TRIAGED,
        "audit_log": state.audit_log + [audit],
    }

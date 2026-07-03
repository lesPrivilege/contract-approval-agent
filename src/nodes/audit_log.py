"""Audit log node — write final audit trail to append-only JSONL."""

import json
import time
from datetime import datetime
from pathlib import Path

from src.state import AuditEntry, ContractState

AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "audit_log.jsonl"
TRACE_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "trace_log.jsonl"

KNOWN_TYPES = {"采购类", "服务类", "工程类", "担保类", "投资合作类"}


def _derive_trace(entry: AuditEntry, contract_id: str, step_idx: int) -> list[dict]:
    """Derive trace steps from a single audit entry."""
    steps = []
    node = entry.node
    action = entry.action
    dur = entry.duration_ms

    if node == "triage":
        steps.append({"case_id": contract_id, "step_idx": step_idx, "action": "reason",
                       "tool_name": "", "args_ok": None, "duration_ms": dur})
        step_idx += 1
        if "llm_fallback" in entry.output_summary:
            steps.append({"case_id": contract_id, "step_idx": step_idx, "action": "tool_call",
                           "tool_name": "llm_classify", "args_ok": True, "duration_ms": dur})
    elif node == "clause_extraction":
        steps.append({"case_id": contract_id, "step_idx": step_idx, "action": "reason",
                       "tool_name": "", "args_ok": None, "duration_ms": dur})
    elif node == "rag":
        ctype = entry.input_summary.replace("合同类型: ", "")
        steps.append({"case_id": contract_id, "step_idx": step_idx, "action": "tool_call",
                       "tool_name": "get_sop", "args_ok": ctype in KNOWN_TYPES, "duration_ms": dur})
    elif node == "route":
        steps.append({"case_id": contract_id, "step_idx": step_idx, "action": "route",
                       "tool_name": "", "args_ok": None, "duration_ms": dur})
    elif node in ("counterparty_guard", "project_guard", "isolation_guard", "guardrail", "hitl"):
        steps.append({"case_id": contract_id, "step_idx": step_idx, "action": "reason",
                       "tool_name": "", "args_ok": None, "duration_ms": dur})

    return steps


def audit_log_node(state: ContractState) -> dict:
    """Write the complete audit trail to JSONL file."""
    start = time.perf_counter()

    # Write each audit entry as a line
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        for entry in state.audit_log:
            record = entry.model_dump()
            record["timestamp"] = record["timestamp"].isoformat()
            record["contract_id"] = state.contract.id
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Derive and write trace log
    trace_steps = []
    step_idx = 0
    for entry in state.audit_log:
        derived = _derive_trace(entry, state.contract.id, step_idx)
        trace_steps.extend(derived)
        step_idx += len(derived)

    if trace_steps:
        with open(TRACE_LOG_PATH, "a", encoding="utf-8") as f:
            for step in trace_steps:
                f.write(json.dumps(step, ensure_ascii=False) + "\n")

    # Write summary entry
    duration = max(1, int((time.perf_counter() - start) * 1000))
    summary = AuditEntry(
        node="audit_log",
        action="write_log",
        input_summary=f"合同 {state.contract.id}, {len(state.audit_log)} 条记录",
        output_summary=f"写入 {AUDIT_LOG_PATH}",
        decision="logged",
        duration_ms=duration,
    )

    return {
        "current_step": "logged",
        "audit_log": state.audit_log + [summary],
    }

"""Audit log node — write final audit trail to append-only JSONL."""

import json
import time
from datetime import datetime
from pathlib import Path

from src.state import AuditEntry, ContractState

AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "audit_log.jsonl"


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

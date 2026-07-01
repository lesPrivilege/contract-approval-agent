"""Graph State — Pydantic model shared across all nodes."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ContractStatus(str, Enum):
    DRAFT = "draft"
    TRIAGED = "triaged"
    RETRIEVED = "retrieved"
    ROUTED = "routed"
    GUARD_CHECKED = "guard_checked"
    WAITING_HITL = "waiting_hitl"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class GuardrailResult(BaseModel):
    guard_name: str
    passed: bool
    reason: str | None = None
    checked_at: datetime = Field(default_factory=datetime.now)


class AuditEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    node: str
    action: str
    input_summary: str
    output_summary: str
    decision: str
    duration_ms: int = 0


class ContractInfo(BaseModel):
    id: str
    板块: str
    合同类型: str
    金额: int
    关联项目id: str | None = None
    发起人: str
    条款标记: dict[str, bool] = Field(default_factory=dict)
    关联方标记: bool = False
    合同成熟度: str | None = None
    对方状态: str = "正常"
    条款描述: str = ""
    说明: str = ""


class ClauseExtraction(BaseModel):
    """LLM structured output for clause extraction."""
    不可逆: bool
    担保: bool
    跨业务: bool
    关联方标记: bool
    对方状态: Literal["正常", "资信不良", "黑名单"]
    confidence: float
    reasoning: str


class ContractState(BaseModel):
    # Core data
    contract: ContractInfo
    project_approved: bool | None = None
    is_cross_business: bool = False

    # Processing results
    approval_chain: list[str] = Field(default_factory=list)
    sop_content: str | None = None
    sop_missing: bool = False
    risks: list[str] = Field(default_factory=list)
    guardrail_results: list[GuardrailResult] = Field(default_factory=list)
    extraction_low_confidence: bool = False

    # Flow control
    current_step: str = "draft"
    status: ContractStatus = ContractStatus.DRAFT
    block_reason: str | None = None

    # HITL
    interrupt_reason: str | None = None
    human_decision: str | None = None
    human_comment: str | None = None

    # Audit
    audit_log: list[AuditEntry] = Field(default_factory=list)

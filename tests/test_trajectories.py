"""Trajectory evaluation tests — verify agent behavior for all scenarios."""

import json
import os

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.graph import compile_graph
from src.state import ContractInfo, ContractState, ContractStatus


def _load_contract(contract_id: str) -> dict:
    with open("data/contracts.jsonl", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if c["id"] == contract_id:
                return c
    raise ValueError(f"Contract {contract_id} not found")


_checkpointer = MemorySaver()
_graph = compile_graph(checkpointer=_checkpointer)


def _run(contract_id: str, resume=None, thread_id=None):
    data = _load_contract(contract_id)
    config = {"configurable": {"thread_id": thread_id or f"test-{contract_id}"}}

    if resume is not None:
        result = _graph.invoke(Command(resume=resume), config=config)
    else:
        info = ContractInfo(**data)
        state = ContractState(contract=info)
        result = _graph.invoke(state, config=config)

    interrupts = result.get("__interrupt__", [])
    if interrupts:
        return {"interrupted": True, "payload": interrupts, "thread_id": config["configurable"]["thread_id"]}
    return result


class TestNormalRouting:
    """C001: standard contract — should auto-approve without HITL."""

    def test_status_approved(self):
        result = _run("C001")
        assert result["status"] == ContractStatus.APPROVED

    def test_approval_chain(self):
        result = _run("C001")
        assert "部门负责人" in result["approval_chain"]
        assert "分管副总" in result["approval_chain"]

    def test_no_hitl(self):
        result = _run("C001")
        assert result["human_decision"] == "auto_approved"

    def test_guardrails_passed(self):
        result = _run("C001")
        for g in result["guardrail_results"]:
            assert g.passed is True

    def test_audit_trajectory(self):
        result = _run("C001")
        nodes = [e.node for e in result["audit_log"]]
        assert "triage" in nodes
        assert "rag" in nodes
        assert "route" in nodes
        assert "guardrail" in nodes
        assert "hitl" in nodes
        assert "audit_log" in nodes


class TestAmountHitl:
    """C002: large amount — should trigger HITL interrupt."""

    def test_interrupt_triggered(self):
        result = _run("C002")
        assert result["interrupted"] is True

    def test_interrupt_payload(self):
        result = _run("C002")
        payload = result["payload"][0].value
        assert payload["contract_id"] == "C002"
        assert payload["amount"] == 6000000
        assert "金额" in payload["reason"]

    def test_resume_approved(self):
        result = _run("C002")
        thread = result["thread_id"]
        result2 = _run("C002", resume="approved", thread_id=thread)
        assert result2["status"] == ContractStatus.APPROVED

    def test_resume_rejected(self):
        result = _run("C002")
        thread = result["thread_id"]
        result2 = _run("C002", resume="rejected", thread_id=thread)
        assert result2["status"] == ContractStatus.REJECTED


class TestProjectBlock:
    """C003: project not approved — should be blocked by guardrail."""

    def test_status_blocked(self):
        result = _run("C003")
        assert result["status"] == ContractStatus.BLOCKED

    def test_block_reason(self):
        result = _run("C003")
        assert "未通过评审" in result["block_reason"]

    def test_project_guard_failed(self):
        result = _run("C003")
        project_guard = [g for g in result["guardrail_results"] if g.guard_name == "project_guard"]
        assert len(project_guard) == 1
        assert project_guard[0].passed is False

    def test_no_hitl(self):
        result = _run("C003")
        # Should not reach HITL node
        nodes = [e.node for e in result["audit_log"]]
        assert "hitl" not in nodes


class TestIsolationBlock:
    """C004: cross-business — should be blocked by isolation guard."""

    def test_status_blocked(self):
        result = _run("C004")
        assert result["status"] == ContractStatus.BLOCKED

    def test_block_reason(self):
        result = _run("C004")
        assert "合规审查" in result["block_reason"]

    def test_isolation_guard_failed(self):
        result = _run("C004")
        iso_guard = [g for g in result["guardrail_results"] if g.guard_name == "isolation_guard"]
        assert len(iso_guard) == 1
        assert iso_guard[0].passed is False

    def test_project_guard_passed(self):
        result = _run("C004")
        proj_guard = [g for g in result["guardrail_results"] if g.guard_name == "project_guard"]
        assert len(proj_guard) == 1
        assert proj_guard[0].passed is True


class TestCSectorRouting:
    """C005: C板块 standard service — should route normally without HITL."""

    def test_status_approved(self):
        result = _run("C005")
        assert result["status"] == ContractStatus.APPROVED

    def test_approval_chain(self):
        result = _run("C005")
        assert "部门负责人" in result["approval_chain"]
        assert "分管副总" in result["approval_chain"]

    def test_no_hitl(self):
        result = _run("C005")
        assert result["human_decision"] == "auto_approved"

    def test_guardrails_passed(self):
        result = _run("C005")
        for g in result["guardrail_results"]:
            assert g.passed is True


class TestDSectorGuarantee:
    """C006: D板块 guarantee contract — should trigger HITL via guarantee flag."""

    def test_interrupt_triggered(self):
        result = _run("C006")
        assert result["interrupted"] is True

    def test_interrupt_reason_guarantee(self):
        result = _run("C006")
        payload = result["payload"][0].value
        assert "担保" in payload["reason"]

    def test_approval_chain(self):
        result = _run("C006")
        payload = result["payload"][0].value
        assert "财务负责人" in payload["approval_chain"]
        assert "法务负责人" in payload["approval_chain"]

    def test_resume_approved(self):
        result = _run("C006")
        thread = result["thread_id"]
        result2 = _run("C006", resume="approved", thread_id=thread)
        assert result2["status"] == ContractStatus.APPROVED


class TestMaturityHigh:
    """C007: B板块 investment cooperation, high maturity — efficient approval chain."""

    def test_status_approved(self):
        result = _run("C007")
        assert result["status"] == ContractStatus.APPROVED

    def test_approval_chain_high_maturity(self):
        result = _run("C007")
        assert "投资板块负责人" in result["approval_chain"]
        assert "财务负责人" in result["approval_chain"]
        assert "分管副总" in result["approval_chain"]
        assert "总经理" not in result["approval_chain"]

    def test_no_hitl(self):
        result = _run("C007")
        assert result["human_decision"] == "auto_approved"


class TestMaturityLow:
    """C008: B板块 investment cooperation, low maturity — cautious chain + HITL."""

    def test_interrupt_triggered(self):
        result = _run("C008")
        assert result["interrupted"] is True

    def test_approval_chain_low_maturity(self):
        result = _run("C008")
        # Low maturity goes through 审慎链 — check from interrupt payload
        payload = result["payload"][0].value
        assert "投资板块负责人" in payload["approval_chain"]
        assert "总经理" in payload["approval_chain"]
        assert "上级" in payload["approval_chain"]

    def test_interrupt_reason_amount(self):
        result = _run("C008")
        payload = result["payload"][0].value
        assert "金额" in payload["reason"]

    def test_resume_approved(self):
        result = _run("C008")
        thread = result["thread_id"]
        result2 = _run("C008", resume="approved", thread_id=thread)
        assert result2["status"] == ContractStatus.APPROVED


class TestBudgetExceeded:
    """C009: B板块 project approved but contract exceeds budget ceiling."""

    def test_status_blocked(self):
        result = _run("C009")
        assert result["status"] == ContractStatus.BLOCKED

    def test_block_reason_budget(self):
        result = _run("C009")
        assert "预算上限" in result["block_reason"]

    def test_project_guard_failed(self):
        result = _run("C009")
        project_guard = [g for g in result["guardrail_results"] if g.guard_name == "project_guard"]
        assert len(project_guard) == 1
        assert project_guard[0].passed is False

    def test_no_hitl(self):
        result = _run("C009")
        nodes = [e.node for e in result["audit_log"]]
        assert "hitl" not in nodes


class TestRelatedPartyHitl:
    """C010: A板块 related party contract — triggers HITL for enhanced review."""

    def test_interrupt_triggered(self):
        result = _run("C010")
        assert result["interrupted"] is True

    def test_interrupt_reason_related_party(self):
        result = _run("C010")
        payload = result["payload"][0].value
        assert "关联" in payload["reason"]
        assert "增强审查" in payload["reason"]

    def test_approval_chain_normal(self):
        result = _run("C010")
        payload = result["payload"][0].value
        assert "部门负责人" in payload["approval_chain"]
        assert "分管副总" in payload["approval_chain"]

    def test_resume_approved(self):
        result = _run("C010")
        thread = result["thread_id"]
        result2 = _run("C010", resume="approved", thread_id=thread)
        assert result2["status"] == ContractStatus.APPROVED


class TestBlacklistBlock:
    """C011: blacklisted counterparty — should be blocked by counterparty_guard."""

    def test_status_blocked(self):
        result = _run("C011")
        assert result["status"] == ContractStatus.BLOCKED

    def test_block_reason_blacklist(self):
        result = _run("C011")
        assert "黑名单" in result["block_reason"]

    def test_counterparty_guard_failed(self):
        result = _run("C011")
        cp_guard = [g for g in result["guardrail_results"] if g.guard_name == "counterparty_guard"]
        assert len(cp_guard) == 1
        assert cp_guard[0].passed is False


_has_api_key = bool(os.getenv("OPENAI_API_KEY"))


class TestServiceSopTemplate:
    """Service contracts should retrieve an explicit SOP template."""

    def test_service_sop_found_for_c_sector(self):
        result = _run("C005")
        assert result["sop_missing"] is False
        assert "服务类合同审批 SOP" in result["sop_content"]


@pytest.mark.skipif(not _has_api_key, reason="需要真实 API key")
class TestLLMTriageFallback:
    """Unknown structured labels should use LLM fallback classification."""

    def test_unknown_type_uses_llm_fallback(self):
        data = _load_contract("C005")
        data["合同类型"] = "技术服务安排"
        config = {"configurable": {"thread_id": "test-triage-llm-fallback"}}
        state = ContractState(contract=ContractInfo(**data))

        result = _graph.invoke(state, config=config)

        triage_entries = [e for e in result["audit_log"] if e.node == "triage"]
        assert triage_entries
        assert "方法=llm_fallback" in triage_entries[0].output_summary
        assert result["contract"].合同类型 in {"采购类", "服务类", "工程类", "担保类", "投资合作类"}


@pytest.mark.skipif(not _has_api_key, reason="需要真实 API key")
class TestLLMClauseClear:
    """C012: clear clause description — LLM should extract with high confidence."""

    def test_status_approved(self):
        result = _run("C012")
        assert result["status"] == ContractStatus.APPROVED

    def test_no_low_confidence(self):
        result = _run("C012")
        assert result["extraction_low_confidence"] is False

    def test_extraction_applied(self):
        result = _run("C012")
        contract = result["contract"]
        assert contract.条款标记.get("不可逆") is True
        assert contract.对方状态 in ("正常", "资信不良", "黑名单")


@pytest.mark.skipif(not _has_api_key, reason="需要真实 API key")
class TestLLMClauseAmbiguous:
    """C013: ambiguous clause — LLM should flag low confidence, triggering HITL."""

    def test_interrupt_triggered(self):
        result = _run("C013")
        assert result["interrupted"] is True

    def test_low_confidence_reason(self):
        result = _run("C013")
        payload = result["payload"][0].value
        assert "置信度" in payload["reason"]


@pytest.mark.skipif(not _has_api_key, reason="需要真实 API key")
class TestLLMClauseBlacklist:
    """C014: blacklist in clause text — LLM should extract, counterparty_guard blocks."""

    def test_status_blocked(self):
        result = _run("C014")
        assert result["status"] == ContractStatus.BLOCKED

    def test_block_reason_blacklist(self):
        result = _run("C014")
        assert "黑名单" in result["block_reason"]


class TestTraceOutput:
    """Verify trace_log.jsonl is generated with well-formed entries."""

    def test_trace_file_exists(self):
        _run("C001")
        import os
        assert os.path.exists("data/trace_log.jsonl")

    def test_trace_entries_valid(self):
        _run("C002")
        import os
        valid_actions = {"reason", "tool_call", "route"}
        with open("data/trace_log.jsonl", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                assert "case_id" in entry
                assert "step_idx" in entry
                assert entry["action"] in valid_actions

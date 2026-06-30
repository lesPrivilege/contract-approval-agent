"""Trajectory evaluation tests — verify agent behavior for all 4 scenarios."""

import json

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

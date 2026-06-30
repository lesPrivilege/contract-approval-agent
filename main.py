"""Contract Approval Agent — Entry point."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("contract-agent")

DATA_DIR = Path(__file__).parent / "data"


def load_contract(contract_id: str) -> dict | None:
    """Load a contract by ID from contracts.jsonl."""
    with open(DATA_DIR / "contracts.jsonl", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if c["id"] == contract_id:
                return c
    return None


def list_contracts():
    """List all available contracts."""
    with open(DATA_DIR / "contracts.jsonl", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            print(f"  {c['id']} | {c['test_case']:15s} | {c['板块']:4s} | ¥{c['金额']:>10,} | {c['说明']}")


_checkpointer = None
_graph = None


def _get_graph():
    """Lazy-init graph with persistent checkpointer."""
    global _checkpointer, _graph
    if _graph is None:
        from langgraph.checkpoint.memory import MemorySaver
        from src.graph import compile_graph
        _checkpointer = MemorySaver()
        _graph = compile_graph(checkpointer=_checkpointer)
    return _graph


def run_contract(contract_data: dict, resume_value=None, thread_id=None):
    """Run a contract through the approval graph."""
    from src.state import ContractInfo, ContractState

    contract_info = ContractInfo(**contract_data)
    graph = _get_graph()
    config = {"configurable": {"thread_id": thread_id or f"demo-{contract_info.id}"}}

    logger.info(f"Running contract {contract_info.id}: {contract_info.板块}-{contract_info.合同类型}, ¥{contract_info.金额:,}")

    if resume_value is not None:
        from langgraph.types import Command
        result = graph.invoke(Command(resume=resume_value), config=config)
    else:
        state = ContractState(contract=contract_info)
        result = graph.invoke(state, config=config)

    # Check for interrupt
    interrupts = result.get("__interrupt__", [])
    if interrupts:
        return {
            "interrupted": True,
            "interrupt_payload": interrupts,
            "thread_id": config["configurable"]["thread_id"],
            "partial_state": result,
        }

    return result


def print_result(result):
    """Print the result in a readable format."""
    print("\n" + "=" * 60)

    # Handle HITL interrupt
    if result.get("interrupted"):
        print("⏸  HITL 中断 — 等待人工审批")
        for interrupt in result.get("interrupt_payload", []):
            payload = interrupt.value
            if isinstance(payload, dict):
                print(f"\n审批请求:")
                for k, v in payload.items():
                    print(f"  {k}: {v}")
            else:
                print(f"  {payload}")
        print(f"\n恢复命令:")
        print(f"  python main.py --contract <ID> --resume approved --thread {result.get('thread_id', 'demo')}")
        print("=" * 60)
        return

    print(f"合同 ID: {result['contract'].id}")
    print(f"状态: {result['status'].value}")
    print(f"当前步骤: {result['current_step']}")

    if result.get("approval_chain"):
        print(f"审批链: {' → '.join(result['approval_chain'])}")

    if result.get("block_reason"):
        print(f"阻断原因: {result['block_reason']}")

    if result.get("human_decision"):
        print(f"人工决策: {result['human_decision']}")

    if result.get("sop_content"):
        print(f"SOP: 已检索")

    print(f"\n审计日志 ({len(result.get('audit_log', []))} 条):")
    for entry in result.get("audit_log", []):
        print(f"  [{entry.node:12s}] {entry.action:20s} | {entry.decision:15s} | {entry.output_summary}")

    print("=" * 60)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Contract Approval Agent")
    parser.add_argument("--list", action="store_true", help="List available contracts")
    parser.add_argument("--contract", type=str, help="Contract ID to process")
    parser.add_argument("--resume", type=str, help="Resume value for HITL (approved/rejected)")
    parser.add_argument("--thread", type=str, default="demo-thread", help="Thread ID for resume")
    args = parser.parse_args()

    if args.list:
        print("Available contracts:")
        list_contracts()
        return

    if not args.contract:
        print("Usage: python main.py --contract <ID> | --list")
        print("Example: python main.py --contract C001")
        return

    contract_data = load_contract(args.contract)
    if contract_data is None:
        print(f"Contract {args.contract} not found.")
        return

    result = run_contract(contract_data, resume_value=args.resume, thread_id=args.thread)
    print_result(result)


if __name__ == "__main__":
    main()

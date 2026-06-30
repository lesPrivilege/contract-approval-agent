"""Graph assembly — LangGraph StateGraph with conditional edges."""

from langgraph.graph import END, START, StateGraph

from src.nodes.audit_log import audit_log_node
from src.nodes.guardrails.counterparty_guard import counterparty_guard
from src.nodes.guardrails.isolation_guard import isolation_guard
from src.nodes.guardrails.project_guard import project_guard
from src.nodes.hitl import hitl_node
from src.nodes.rag import rag_node
from src.nodes.route import route_node
from src.nodes.triage import triage_node
from src.state import ContractState, ContractStatus


def _should_continue_to_guard(state: ContractState) -> str:
    """After routing, check guardrails unless already blocked."""
    if state.status == ContractStatus.BLOCKED:
        return "end"
    return "counterparty_guard"


def _after_counterparty_guard(state: ContractState) -> str:
    """After counterparty guard, proceed to project guard or end if blocked."""
    if state.status == ContractStatus.BLOCKED:
        return "end"
    return "project_guard"


def _after_project_guard(state: ContractState) -> str:
    """After project guard, proceed to isolation guard or end if blocked."""
    if state.status == ContractStatus.BLOCKED:
        return "end"
    return "isolation_guard"


def _after_isolation_guard(state: ContractState) -> str:
    """After isolation guard, proceed to HITL or end if blocked."""
    if state.status == ContractStatus.BLOCKED:
        return "end"
    return "hitl"


def build_graph() -> StateGraph:
    """Build the contract approval routing graph."""
    graph = StateGraph(ContractState)

    # Add nodes
    graph.add_node("triage", triage_node)
    graph.add_node("rag", rag_node)
    graph.add_node("route", route_node)
    graph.add_node("counterparty_guard", counterparty_guard)
    graph.add_node("project_guard", project_guard)
    graph.add_node("isolation_guard", isolation_guard)
    graph.add_node("hitl", hitl_node)
    graph.add_node("audit_log", audit_log_node)

    # Edges
    graph.add_edge(START, "triage")
    graph.add_edge("triage", "rag")
    graph.add_edge("rag", "route")

    # After route: guardrails chain
    graph.add_conditional_edges(
        "route",
        _should_continue_to_guard,
        {"counterparty_guard": "counterparty_guard", "end": "audit_log"},
    )

    graph.add_conditional_edges(
        "counterparty_guard",
        _after_counterparty_guard,
        {"project_guard": "project_guard", "end": "audit_log"},
    )

    graph.add_conditional_edges(
        "project_guard",
        _after_project_guard,
        {"isolation_guard": "isolation_guard", "end": "audit_log"},
    )

    graph.add_conditional_edges(
        "isolation_guard",
        _after_isolation_guard,
        {"hitl": "hitl", "end": "audit_log"},
    )

    # After HITL: audit log
    graph.add_edge("hitl", "audit_log")

    # After audit log: end
    graph.add_edge("audit_log", END)

    return graph


def compile_graph(checkpointer=None):
    """Compile the graph, optionally with a checkpointer for HITL."""
    graph = build_graph()
    return graph.compile(checkpointer=checkpointer)

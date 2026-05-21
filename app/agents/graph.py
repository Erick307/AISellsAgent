from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agents.orchestrator import orchestrator_node, route_after_orchestrator
from app.agents.stock_catalog import stock_catalog_node
from app.agents.order import order_node
from app.agents.escalation import escalation_node
from app.agents.state import AgentState
from app.config import settings


def build_graph(checkpointer: AsyncPostgresSaver) -> StateGraph:
    graph = StateGraph(AgentState)

    # ── Nodes ──────────────────────────────────────────────────────────────
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("stock_catalog", stock_catalog_node)
    graph.add_node("order", order_node)
    graph.add_node("escalation", escalation_node)

    # ── Entry point ────────────────────────────────────────────────────────
    graph.set_entry_point("orchestrator")

    # ── Routing from orchestrator (LLM decides) ────────────────────────────
    graph.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "stock_catalog": "stock_catalog",
            "order": "order",
            "escalation": "escalation",
            "end": END,
        },
    )

    # ── Specialized agents always return to orchestrator ───────────────────
    # This allows multi-step flows:
    # e.g. stock_catalog answers → orchestrator asks customer to confirm → order registers
    graph.add_edge("stock_catalog", "orchestrator")
    graph.add_edge("order", "orchestrator")

    # ── Escalation ends the graph (human takes over) ───────────────────────
    graph.add_edge("escalation", END)

    return graph.compile(checkpointer=checkpointer)


async def get_graph():
    """Returns a compiled graph with async Postgres checkpointing."""
    checkpointer = AsyncPostgresSaver.from_conn_string(settings.postgres_url)
    await checkpointer.setup()  # Creates checkpoint tables if they don't exist
    return build_graph(checkpointer)

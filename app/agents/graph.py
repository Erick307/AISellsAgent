from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agents.supervisor import supervisor_node, route_after_supervisor
from app.agents.stock_catalog import stock_catalog_node
from app.agents.order import order_node
from app.agents.escalation import escalation_node
from app.agents.state import AgentState
from app.config import settings


def build_graph(checkpointer: AsyncPostgresSaver) -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("stock_catalog", stock_catalog_node)
    graph.add_node("order", order_node)
    graph.add_node("escalation", escalation_node)

    # Entry point
    graph.set_entry_point("supervisor")

    # Conditional routing from supervisor
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "stock_catalog": "stock_catalog",
            "order": "order",
            "escalation": "escalation",
            "end": END,
        },
    )

    # All specialized agents return to supervisor after running
    graph.add_edge("stock_catalog", "supervisor")
    graph.add_edge("order", "supervisor")
    # Escalation ends the graph (human takes over)
    graph.add_edge("escalation", END)

    return graph.compile(checkpointer=checkpointer)


async def get_graph():
    """Returns a compiled graph with Postgres checkpointing."""
    checkpointer = AsyncPostgresSaver.from_conn_string(settings.postgres_url)
    await checkpointer.setup()  # Creates checkpoint tables if they don't exist
    return build_graph(checkpointer)

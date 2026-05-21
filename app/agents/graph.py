import psycopg
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
    graph.add_edge("stock_catalog", "orchestrator")
    graph.add_edge("order", "orchestrator")

    # ── Escalation ends the graph (human takes over) ───────────────────────
    graph.add_edge("escalation", END)

    return graph.compile(checkpointer=checkpointer)


def _pg_url() -> str:
    """Convert SQLAlchemy URL to plain psycopg URL."""
    return settings.postgres_url.replace("postgresql+asyncpg://", "postgresql://")


class GraphManager:
    """
    Manages the LangGraph graph and its Postgres checkpointer.
    Initialized once at app startup and reused across requests.
    """

    def __init__(self):
        self._graph = None
        self._conn = None

    async def setup(self):
        self._conn = await psycopg.AsyncConnection.connect(_pg_url(), autocommit=True)
        checkpointer = AsyncPostgresSaver(self._conn)
        await checkpointer.setup()
        self._graph = build_graph(checkpointer)

    async def teardown(self):
        if self._conn:
            await self._conn.close()

    @property
    def graph(self):
        if self._graph is None:
            raise RuntimeError("GraphManager not initialized. Call setup() first.")
        return self._graph


# Singleton — shared across the whole app
graph_manager = GraphManager()

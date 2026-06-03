from typing import Annotated, Optional
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Shared state passed between all agents in the graph."""
    messages: Annotated[list, add_messages]  # Full conversation history
    conversation_id: str                      # Chatwoot conversation ID
    customer_id: str                           # Chatwoot contact ID (= thread_id, channel-agnostic)
    next_agent: str                           # Set by orchestrator to route to next agent
    escalated_at: Optional[float]             # Timestamp when escalation happened (None if not escalated)

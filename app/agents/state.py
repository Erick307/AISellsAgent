from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Shared state passed between all agents in the graph."""
    messages: Annotated[list, add_messages]  # Full conversation history
    conversation_id: str                      # Chatwoot conversation ID
    customer_phone: str                       # Customer's phone number (= thread_id)
    next_agent: str                           # Set by supervisor to route to next agent

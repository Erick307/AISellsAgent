from langgraph.types import interrupt
from app.agents.state import AgentState
from app.services.chatwoot import open_conversation_for_human


def escalation_node(state: AgentState) -> AgentState:
    """
    Pauses the graph and hands off to a human agent.

    1. Opens the Chatwoot conversation so a human can see and reply.
    2. Calls interrupt() — the graph is paused and state is saved in Postgres.
    3. The graph resumes when explicitly triggered (e.g. customer sends a new message
       after the human marks the conversation as resolved).
    """
    open_conversation_for_human(state["conversation_id"])
    interrupt("Waiting for human agent to handle the conversation.")
    return {}

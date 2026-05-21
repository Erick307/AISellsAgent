import time
from langgraph.types import interrupt
from app.agents.state import AgentState
from app.services.chatwoot import open_conversation_for_human


def escalation_node(state: AgentState) -> AgentState:
    """
    Pauses the graph and hands off to a human agent.

    1. Opens the Chatwoot conversation so a human can see and reply.
    2. Records the escalation timestamp in state.
    3. Calls interrupt() — the graph is paused and full state is saved in Postgres.

    Resume condition: customer sends a new message after ESCALATION_RESUME_HOURS
    hours of human inactivity (checked in the webhook handler).
    """
    open_conversation_for_human(state["conversation_id"])
    interrupt("Waiting for human agent to handle the conversation.")
    return {"escalated_at": time.time()}

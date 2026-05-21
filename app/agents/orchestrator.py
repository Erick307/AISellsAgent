from typing import Literal
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage
from app.agents.state import AgentState
from app.prompts.loader import load_prompt


llm = ChatAnthropic(model="claude-sonnet-4-6")
prompt = load_prompt("orchestrator")


class RouteDecision(BaseModel):
    """Structured output the orchestrator uses to decide what to do next."""
    next: Literal["stock_catalog", "order", "escalation", "end"]
    message: str  # Reply to send to the customer, or context/instructions for the next agent


def orchestrator_node(state: AgentState) -> AgentState:
    """
    Central orchestrator — reads the conversation and decides:
    - Reply directly and end the turn (greetings, FAQs, confirmations)
    - Route to stock_catalog for stock/price queries
    - Route to order when the customer confirms they want to place an order
    - Route to escalation when human intervention is needed

    If the last message is already an AI response (i.e. a specialized agent just
    finished), we end the turn immediately — no need to call the LLM again with a
    conversation that ends in an assistant message (Anthropic rejects that).
    """
    messages = state["messages"]

    # A specialized agent already produced the final reply — end the turn.
    last = messages[-1] if messages else None
    if isinstance(last, AIMessage) and not getattr(last, "tool_calls", None):
        return {"messages": [], "next_agent": "end"}

    # Normal path: ask the LLM to decide what to do next.
    structured_llm = llm.with_structured_output(RouteDecision)
    chain = prompt | structured_llm

    decision: RouteDecision = chain.invoke({"messages": messages})

    # If ending the turn directly, add the reply to the conversation.
    new_messages = []
    if decision.next == "end":
        new_messages = [{"role": "assistant", "content": decision.message}]

    return {
        "messages": new_messages,
        "next_agent": decision.next,
    }


def route_after_orchestrator(state: AgentState) -> str:
    """Conditional edge: returns which node to run next."""
    return state.get("next_agent", "end")

from typing import Literal
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
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

    Uses Claude with structured output to make the routing decision.
    """
    structured_llm = llm.with_structured_output(RouteDecision)
    chain = prompt | structured_llm

    decision: RouteDecision = chain.invoke({"messages": state["messages"]})

    # If ending the turn, add the reply to the conversation
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

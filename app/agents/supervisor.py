from langchain_anthropic import ChatAnthropic
from app.agents.state import AgentState
from app.prompts.loader import load_prompt


llm = ChatAnthropic(model="claude-sonnet-4-6")
prompt = load_prompt("supervisor")


def supervisor_node(state: AgentState) -> AgentState:
    """
    Reads the latest customer message and decides:
    - Reply directly (simple greetings, FAQs)
    - Route to stock_catalog, order, or escalation agent
    """
    chain = prompt | llm
    response = chain.invoke({
        "messages": state["messages"],
    })
    # TODO: parse response to extract routing decision
    return {"messages": [response], "next_agent": "end"}


def route_after_supervisor(state: AgentState) -> str:
    """Conditional edge: returns which node to run next."""
    return state.get("next_agent", "end")

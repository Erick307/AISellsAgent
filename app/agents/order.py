from langchain_anthropic import ChatAnthropic
from app.agents.state import AgentState
from app.prompts.loader import load_prompt
from app.tools.database import get_database_tools


llm = ChatAnthropic(model="claude-sonnet-4-6")
prompt = load_prompt("order_agent")


def order_node(state: AgentState) -> AgentState:
    """
    Handles order registration.
    Uses database tools to write confirmed orders and unmet demand to Postgres.
    """
    db_tools = get_database_tools()
    chain = prompt | llm.bind_tools(db_tools)
    response = chain.invoke({
        "messages": state["messages"],
    })
    return {"messages": [response]}

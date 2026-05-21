from langchain_anthropic import ChatAnthropic
from app.agents.state import AgentState
from app.prompts.loader import load_prompt
from app.tools.drive import get_drive_tools


llm = ChatAnthropic(model="claude-sonnet-4-6")
prompt = load_prompt("stock_catalog_agent")


def stock_catalog_node(state: AgentState) -> AgentState:
    """
    Handles stock and price queries.
    Uses GoogleDriveTool to read the client's Drive files.
    """
    drive_tools = get_drive_tools()
    chain = prompt | llm.bind_tools(drive_tools)
    response = chain.invoke({
        "messages": state["messages"],
    })
    return {"messages": [response]}

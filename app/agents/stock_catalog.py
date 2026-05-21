from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ToolMessage
from app.agents.state import AgentState
from app.prompts.loader import load_prompt
from app.tools.drive import get_drive_tools


llm = ChatAnthropic(model="claude-sonnet-4-6")
prompt = load_prompt("stock_catalog_agent")


def stock_catalog_node(state: AgentState) -> AgentState:
    """
    Handles stock and price queries.
    Uses GoogleDriveTool to search and read the client's Drive files.
    Runs a full tool loop — calls tools until the LLM produces a plain text response.
    Returns result to the orchestrator — never ends the turn directly.
    """
    drive_tools = get_drive_tools()
    tools_by_name = {t.name: t for t in drive_tools}
    llm_with_tools = llm.bind_tools(drive_tools)

    # Get initial LLM response (with prompt applied)
    messages = list(state["messages"])
    response = (prompt | llm_with_tools).invoke({"messages": messages})
    new_messages = [response]

    # Tool loop: execute any tool calls and feed results back until we get plain text
    while response.tool_calls:
        for tc in response.tool_calls:
            tool_result = tools_by_name[tc["name"]].invoke(tc["args"])
            new_messages.append(
                ToolMessage(content=str(tool_result), tool_call_id=tc["id"])
            )
        # Call the LLM again with the full updated history
        response = llm_with_tools.invoke(messages + new_messages)
        new_messages.append(response)

    return {"messages": new_messages}

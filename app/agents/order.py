from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ToolMessage
from app.agents.state import AgentState
from app.prompts.loader import load_prompt
from app.tools.database import get_database_tools


llm = ChatAnthropic(model="claude-sonnet-4-6")
prompt = load_prompt("order_agent")


def order_node(state: AgentState) -> AgentState:
    """
    Handles order registration.
    Only triggered after the customer has explicitly confirmed they want to place an order.
    Runs a full tool loop — calls database tools until the LLM produces a plain text response.
    Returns result to the orchestrator — never ends the turn directly.
    """
    db_tools = get_database_tools()
    tools_by_name = {t.name: t for t in db_tools}
    llm_with_tools = llm.bind_tools(db_tools)

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

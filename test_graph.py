"""
Quick test to run the LangGraph graph directly without Chatwoot.
Usage: uv run python test_graph.py

Each run uses a unique thread ID so stale checkpoints from previous
runs never pollute the conversation history.
"""
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

from app.agents.graph import graph_manager

# Unique session ID per run — avoids loading stale checkpoints
_SESSION_ID = f"test-{int(time.time())}"


async def test(message: str):
    phone = _SESSION_ID
    print(f"\n{'='*50}")
    print(f"Customer: {message}")
    print(f"{'='*50}")

    graph = graph_manager.graph
    config = {"configurable": {"thread_id": phone}}

    state = {
        "messages": [{"role": "user", "content": message}],
        "conversation_id": "test-001",
        "customer_phone": phone,
    }

    result = await graph.ainvoke(state, config=config)

    last = result["messages"][-1]
    response = last.content if hasattr(last, "content") else str(last)
    print(f"Agent:    {response}")


async def main():
    await graph_manager.setup()

    # Test 1 — simple greeting
    await test("Hi! Are you open?")

    # Test 2 — stock query (same session, so the agent has context from test 1)
    await test("Do you have Nike Air Max size 42?")

    await graph_manager.teardown()


if __name__ == "__main__":
    asyncio.run(main())

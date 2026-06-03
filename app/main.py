from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from app.webhooks.chatwoot import router as chatwoot_router
from app.agents.graph import graph_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — initialize the graph and Postgres checkpointer
    await graph_manager.setup()
    yield
    # Shutdown — close the Postgres connection
    await graph_manager.teardown()


app = FastAPI(title="WhatsApp Sales Agent", lifespan=lifespan)

app.include_router(chatwoot_router, prefix="/webhooks")


@app.get("/health")
async def health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    phone: str
    message: str


@app.post("/chat")
async def chat(req: ChatRequest):
    graph = graph_manager.graph
    config = {"configurable": {"thread_id": req.phone}}

    state = {
        "messages": [{"role": "user", "content": req.message}],
        "conversation_id": "dev-chat",
        "customer_id": req.phone,
    }

    result = await graph.ainvoke(state, config=config)

    last = result["messages"][-1]
    reply = last.content if hasattr(last, "content") else str(last)
    return {"reply": reply}

from contextlib import asynccontextmanager
from fastapi import FastAPI
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

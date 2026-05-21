from fastapi import FastAPI
from app.webhooks.chatwoot import router as chatwoot_router

app = FastAPI(title="WhatsApp Sales Agent")

app.include_router(chatwoot_router, prefix="/webhooks")


@app.get("/health")
async def health():
    return {"status": "ok"}

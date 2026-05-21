import asyncio
import hashlib
import hmac
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.config import settings
from app.agents.graph import get_graph
from app.services.chatwoot import send_message

router = APIRouter()

# Debounce timers: { conversation_id: asyncio.Task }
_debounce_timers: dict[str, asyncio.Task] = {}


def verify_signature(payload: bytes, signature: str) -> bool:
    """Validates the HMAC signature sent by Chatwoot."""
    expected = hmac.new(
        settings.chatwoot_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/chatwoot")
async def chatwoot_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()
    signature = request.headers.get("X-Chatwoot-Signature", "")

    if not verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()

    # Only process incoming customer messages
    event = data.get("event")
    if event != "message_created":
        return {"status": "ignored"}

    message_type = data.get("message_type")
    if message_type != "incoming":
        return {"status": "ignored"}

    conversation_id = str(data["conversation"]["id"])
    customer_phone = data["meta"]["sender"]["phone_number"]
    message_content = data["content"]

    # Cancel existing debounce timer for this conversation if any
    if conversation_id in _debounce_timers:
        _debounce_timers[conversation_id].cancel()

    # Start a new debounce timer
    task = asyncio.create_task(
        _debounced_process(conversation_id, customer_phone, message_content)
    )
    _debounce_timers[conversation_id] = task

    return {"status": "accepted"}


async def _debounced_process(
    conversation_id: str,
    customer_phone: str,
    message: str,
):
    """Waits for the debounce window, then processes the message."""
    await asyncio.sleep(settings.message_debounce_seconds)

    graph = await get_graph()
    config = {"configurable": {"thread_id": customer_phone}}

    state = {
        "messages": [{"role": "user", "content": message}],
        "conversation_id": conversation_id,
        "customer_phone": customer_phone,
    }

    result = await graph.ainvoke(state, config=config)

    # Extract the last AI message and send it back via Chatwoot
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, "content") else str(last_message)

    await send_message(conversation_id, response_text)

import asyncio
import hashlib
import hmac
import time
from fastapi import APIRouter, Request, HTTPException
from app.config import settings
from app.agents.graph import graph_manager
from app.models.schemas import ChatwootWebhookPayload
from app.services.chatwoot import send_message

router = APIRouter()

# Debounce timers: { conversation_id: asyncio.Task }
_debounce_timers: dict[str, asyncio.Task] = {}

# Tracks last human agent activity per conversation: { conversation_id: timestamp }
# TODO: move to Postgres for persistence across server restarts
_last_human_activity: dict[str, float] = {}


def verify_signature(payload: bytes, signature: str) -> bool:
    """Validates the HMAC-SHA256 signature sent by Chatwoot."""
    expected = hmac.new(
        settings.chatwoot_webhook_secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/chatwoot")
async def chatwoot_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Chatwoot-Signature", "")

    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()

    # Parse and validate the payload with Pydantic
    try:
        payload = ChatwootWebhookPayload(**data)
    except Exception:
        # Unknown payload shape — ignore gracefully
        return {"status": "ignored"}

    # Track last human agent activity for escalation resume logic
    if (
        payload.event == "message_created"
        and payload.message_type == "outgoing"
        and payload.sender
        and payload.sender.type != "agent_bot"
        and payload.conversation
    ):
        conversation_id = str(payload.conversation.id)
        _last_human_activity[conversation_id] = time.time()

    # Only process incoming customer messages
    if payload.event != "message_created":
        return {"status": "ignored"}

    if payload.message_type != "incoming":
        return {"status": "ignored"}

    # Validate required fields
    if not payload.conversation or not payload.sender or not payload.content:
        return {"status": "ignored"}

    conversation_id = str(payload.conversation.id)
    customer_phone = payload.sender.phone_number

    if not customer_phone:
        # No phone number — can't identify the customer
        return {"status": "ignored", "reason": "no_phone_number"}

    message_content = payload.content

    # Check escalation resume condition
    graph = graph_manager.graph
    config = {"configurable": {"thread_id": customer_phone}}
    current_state = await graph.aget_state(config)

    is_escalated = (
        current_state.values.get("escalated_at") is not None
        if current_state and current_state.values
        else False
    )

    if is_escalated:
        last_human = _last_human_activity.get(conversation_id)
        hours_since_human = (
            (time.time() - last_human) / 3600 if last_human else float("inf")
        )

        if hours_since_human < settings.escalation_resume_hours:
            # Human is still active — bot stays out
            return {"status": "escalated_human_active"}

        # Human has been inactive long enough — clear escalation and let bot resume
        await graph.aupdate_state(config, {"escalated_at": None})

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
    """Waits for the debounce window, then runs the LangGraph graph."""
    await asyncio.sleep(settings.message_debounce_seconds)

    graph = graph_manager.graph
    config = {"configurable": {"thread_id": customer_phone}}

    state = {
        "messages": [{"role": "user", "content": message}],
        "conversation_id": conversation_id,
        "customer_phone": customer_phone,
    }

    result = await graph.ainvoke(state, config=config)

    # Extract the last AI message and send it via Chatwoot
    last_message = result["messages"][-1]
    response_text = (
        last_message.content
        if hasattr(last_message, "content")
        else str(last_message)
    )

    await send_message(conversation_id, response_text)

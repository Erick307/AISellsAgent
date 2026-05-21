import httpx
from app.config import settings


async def send_message(conversation_id: str, message: str) -> None:
    """Sends a message to a Chatwoot conversation."""
    url = f"{settings.chatwoot_base_url}/api/v1/accounts/1/conversations/{conversation_id}/messages"
    headers = {"api_access_token": settings.chatwoot_api_token}
    payload = {"content": message, "message_type": "outgoing", "private": False}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()


async def open_conversation_for_human(conversation_id: str) -> None:
    """Marks a Chatwoot conversation as open so a human agent can take over."""
    url = f"{settings.chatwoot_base_url}/api/v1/accounts/1/conversations/{conversation_id}/toggle_status"
    headers = {"api_access_token": settings.chatwoot_api_token}
    payload = {"status": "open"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

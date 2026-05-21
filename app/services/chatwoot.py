import httpx
from app.config import settings


def _base_url() -> str:
    return f"{settings.chatwoot_base_url}/api/v1/accounts/{settings.chatwoot_account_id}"


def _headers() -> dict:
    return {"api_access_token": settings.chatwoot_api_token}


async def send_message(conversation_id: str, message: str) -> None:
    """Sends an outgoing message to a Chatwoot conversation."""
    url = f"{_base_url()}/conversations/{conversation_id}/messages"
    payload = {"content": message, "message_type": "outgoing", "private": False}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=_headers())
        response.raise_for_status()


async def open_conversation_for_human(conversation_id: str) -> None:
    """Marks a Chatwoot conversation as open so a human agent can take over."""
    url = f"{_base_url()}/conversations/{conversation_id}/toggle_status"
    payload = {"status": "open"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=_headers())
        response.raise_for_status()

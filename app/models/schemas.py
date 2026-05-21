from pydantic import BaseModel
from typing import Optional


class ChatwootSender(BaseModel):
    phone_number: Optional[str] = None
    name: Optional[str] = None


class ChatwootMeta(BaseModel):
    sender: ChatwootSender


class ChatwootConversation(BaseModel):
    id: int


class ChatwootWebhookPayload(BaseModel):
    event: str
    message_type: Optional[str] = None
    content: Optional[str] = None
    conversation: Optional[ChatwootConversation] = None
    meta: Optional[ChatwootMeta] = None

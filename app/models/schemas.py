from pydantic import BaseModel
from typing import Optional


class ChatwootSender(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None        # "contact" for customer messages, "agent_bot" for bot
    phone_number: Optional[str] = None


class ChatwootInbox(BaseModel):
    id: int
    name: Optional[str] = None


class ChatwootConversation(BaseModel):
    id: int
    display_id: Optional[int] = None
    status: Optional[str] = None


class ChatwootAccount(BaseModel):
    id: int
    name: Optional[str] = None


class ChatwootWebhookPayload(BaseModel):
    event: str
    id: Optional[int] = None
    content: Optional[str] = None
    message_type: Optional[str] = None   # "incoming" | "outgoing" | "activity"
    content_type: Optional[str] = None
    created_at: Optional[str] = None
    sender: Optional[ChatwootSender] = None
    inbox: Optional[ChatwootInbox] = None
    conversation: Optional[ChatwootConversation] = None
    account: Optional[ChatwootAccount] = None

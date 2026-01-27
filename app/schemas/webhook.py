from pydantic import BaseModel
from typing import Optional


# Webhook payload schemas
class WebhookMessage(BaseModel):
    channel: str
    instance_id: str
    contact_id: str
    message: str
    message_type: str = "text"
    external_message_id: Optional[str] = None
    from_me: bool = False


# n8n payload schemas
class N8nIncoming(BaseModel):
    channel: str
    instance_id: str
    contact_id: str
    conversation_id: str
    message: str
    message_type: str = "text"
    external_message_id: Optional[str] = None


class N8nOutgoing(BaseModel):
    conversation_id: str
    message: str
    message_type: str = "text"
    external_message_id: Optional[str] = None

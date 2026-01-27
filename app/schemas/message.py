from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


# Message Schemas
class MessageBase(BaseModel):
    sender: str  # user | bot | human
    message_type: str  # text | audio | image | video | document
    content: str  # Always transcribed text
    external_message_id: Optional[str] = None


class MessageCreate(MessageBase):
    conversation_id: UUID4


class MessageInDB(MessageBase):
    id: UUID4
    conversation_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True


class Message(MessageInDB):
    pass

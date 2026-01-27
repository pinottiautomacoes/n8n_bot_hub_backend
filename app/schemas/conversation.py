from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


# Conversation Schemas
class ConversationBase(BaseModel):
    status: str = "bot"  # bot | human


class ConversationCreate(ConversationBase):
    instance_id: UUID4
    contact_id: UUID4


class ConversationUpdate(BaseModel):
    status: Optional[str] = None
    last_human_message_at: Optional[datetime] = None


class ConversationInDB(ConversationBase):
    id: UUID4
    instance_id: UUID4
    contact_id: UUID4
    last_human_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Conversation(ConversationInDB):
    pass

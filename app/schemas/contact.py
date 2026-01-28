from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional
from uuid import UUID

class ContactBase(BaseModel):
    phone: str
    name: Optional[str] = None

class ContactCreate(ContactBase):
    pass  # bot_id is passed in path parameter usually

class ContactUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None

class ContactInDBBase(ContactBase):
    id: UUID
    bot_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class Contact(ContactInDBBase):
    pass

class ContactResponse(ContactInDBBase):
    pass

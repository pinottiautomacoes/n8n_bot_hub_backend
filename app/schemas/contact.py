from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


# Contact Schemas
class ContactBase(BaseModel):
    external_contact_id: str
    name: Optional[str] = None


class ContactCreate(ContactBase):
    instance_id: UUID4


class ContactUpdate(BaseModel):
    name: Optional[str] = None


class ContactInDB(ContactBase):
    id: UUID4
    instance_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True


class Contact(ContactInDB):
    pass

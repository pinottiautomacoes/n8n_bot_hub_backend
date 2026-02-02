from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime

class DoctorBase(BaseModel):
    name: str
    email: EmailStr
    specialties: str
    crm: Optional[str] = None

class DoctorCreate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):
    id: UUID4
    bot_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

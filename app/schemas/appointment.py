from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


# Appointment Schemas
class AppointmentBase(BaseModel):
    start_time: datetime
    end_time: datetime
    status: str = "active"  # active | cancelled


class AppointmentCreate(BaseModel):
    contact_id: UUID4
    start_time: datetime


class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class AppointmentInDB(AppointmentBase):
    id: UUID4
    bot_id: UUID4
    contact_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Appointment(AppointmentInDB):
    pass

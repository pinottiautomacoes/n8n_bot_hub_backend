from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional
from uuid import UUID

class AppointmentBase(BaseModel):
    contact_id: UUID
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str = "active"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None

class AppointmentInDBBase(AppointmentBase):
    id: UUID
    bot_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Appointment(AppointmentInDBBase):
    pass

class AppointmentResponse(AppointmentInDBBase):
    pass

class AvailableTimeSlot(BaseModel):
    start: datetime
    end: datetime

class AvailableSlotsResponse(BaseModel):
    available_slots: list[AvailableTimeSlot]

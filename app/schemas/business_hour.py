from pydantic import BaseModel, UUID4
from datetime import time
from uuid import UUID

class BusinessHourBase(BaseModel):
    weekday: int
    start_time: time
    end_time: time
    is_available: bool = True

class BusinessHourCreate(BusinessHourBase):
    pass

class BusinessHourUpdate(BusinessHourBase):
    pass

class BusinessHourInDBBase(BusinessHourBase):
    id: UUID
    bot_id: UUID

    class Config:
        from_attributes = True

class BusinessHour(BusinessHourInDBBase):
    pass

class BusinessHourResponse(BusinessHourInDBBase):
    pass

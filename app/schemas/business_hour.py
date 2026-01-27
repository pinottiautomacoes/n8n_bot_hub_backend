from pydantic import BaseModel, UUID4
from datetime import time
from typing import Optional


# BusinessHour Schemas
class BusinessHourBase(BaseModel):
    weekday: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time


class BusinessHourCreate(BusinessHourBase):
    pass


class BusinessHourUpdate(BaseModel):
    weekday: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class BusinessHourInDB(BusinessHourBase):
    id: UUID4
    bot_id: UUID4
    
    class Config:
        from_attributes = True


class BusinessHour(BusinessHourInDB):
    pass

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class BlockedPeriodBase(BaseModel):
    start_time: datetime
    end_time: datetime
    reason: Optional[str] = None

class BlockedPeriodCreate(BlockedPeriodBase):
    bot_id: UUID

class BlockedPeriodUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reason: Optional[str] = None

class BlockedPeriodInDBBase(BlockedPeriodBase):
    id: UUID
    bot_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BlockedPeriod(BlockedPeriodInDBBase):
    pass

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class BlockedPeriodBase(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = None
    
    @field_validator('end_datetime')
    @classmethod
    def validate_end_after_start(cls, v, info):
        if 'start_datetime' in info.data and v <= info.data['start_datetime']:
            raise ValueError('end_datetime must be after start_datetime')
        return v


class BlockedPeriodCreate(BlockedPeriodBase):
    pass


class BlockedPeriodUpdate(BaseModel):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    reason: Optional[str] = None
    
    @field_validator('end_datetime')
    @classmethod
    def validate_end_after_start(cls, v, info):
        if v and 'start_datetime' in info.data and info.data['start_datetime']:
            if v <= info.data['start_datetime']:
                raise ValueError('end_datetime must be after start_datetime')
        return v


class BlockedPeriodInDB(BlockedPeriodBase):
    id: UUID
    bot_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BlockedPeriod(BlockedPeriodInDB):
    pass

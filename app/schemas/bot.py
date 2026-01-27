from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


# Bot Schemas
class BotBase(BaseModel):
    name: str
    personality: Optional[str] = None
    company_info: Optional[str] = None
    target_audience: Optional[str] = None
    service_duration_minutes: int = 30


class BotCreate(BotBase):
    pass


class BotUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    company_info: Optional[str] = None
    target_audience: Optional[str] = None
    service_duration_minutes: Optional[int] = None


class BotInDB(BotBase):
    id: UUID4
    instance_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Bot(BotInDB):
    pass

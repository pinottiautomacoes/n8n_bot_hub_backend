from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, time
from uuid import UUID

# Shared properties
class BotBase(BaseModel):
    name: str
    description: Optional[str] = None
    
    # Instance Info
    instance_name: Optional[str] = None
    instance_token: Optional[str] = None
    
    # Settings
    greeting_message: Optional[str] = None
    fallback_message: Optional[str] = None
    personality: Optional[str] = None
    company_info: Optional[str] = None
    auto_reply_enabled: bool = True
    enabled: bool = True
    timezone: str = "UTC"

# Properties to receive via API on creation
class BotCreate(BotBase):
    pass

# Properties to receive via API on update
class BotUpdate(BotBase):
    name: Optional[str] = None
    auto_reply_enabled: Optional[bool] = None
    enabled: Optional[bool] = None
    personality: Optional[str] = None
    company_info: Optional[str] = None

# Properties shared by models stored in DB
class BotInDBBase(BotBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Additional properties to return via API
class Bot(BotInDBBase):
    pass

class BotResponse(BotInDBBase):
    pass

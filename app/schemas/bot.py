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
    
    # Settings
    personality: Optional[str] = None
    company_info: Optional[str] = None
    enabled: bool = True
    timezone: str = "America/Sao_Paulo"

# Properties to receive via API on creation
class BotCreate(BotBase):
    pass

# Properties to receive via API on update
class BotUpdate(BotBase):
    name: Optional[str] = None
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

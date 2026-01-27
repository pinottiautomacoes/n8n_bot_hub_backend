from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional


# Instance Schemas
class InstanceBase(BaseModel):
    name: str
    channel: str
    external_instance_id: Optional[str] = None
    active: bool = True


class InstanceCreate(InstanceBase):
    pass


class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    channel: Optional[str] = None
    external_instance_id: Optional[str] = None
    active: Optional[bool] = None


class InstanceInDB(InstanceBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Instance(InstanceInDB):
    pass

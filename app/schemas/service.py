from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int
    price: Optional[float] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: UUID4
    doctor_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

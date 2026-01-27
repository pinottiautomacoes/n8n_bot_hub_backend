from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Optional


# User Schemas
class UserBase(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None


class UserCreate(UserBase):
    firebase_uid: str


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    id: UUID4
    firebase_uid: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass

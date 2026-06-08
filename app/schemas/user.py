from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserType


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    user_type: UserType


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    user_type: UserType
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: Optional[str] = None
    pending: bool = False  # True quando vet/clínica aguarda aprovação


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    user_type: Optional[UserType] = None

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TutorBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class TutorCreate(TutorBase):
    email: str
    password: str


class TutorResponse(TutorBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

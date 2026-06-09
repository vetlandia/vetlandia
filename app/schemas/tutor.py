from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PetInfo(BaseModel):
    name: str
    species: str


class TutorBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=255)
    cpf: Optional[str] = Field(None, max_length=14)
    phone: Optional[str] = Field(None, max_length=20)
    state: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    complement: Optional[str] = Field(None, max_length=200)
    pets: Optional[str] = None  # JSON string
    photo_url: Optional[str] = None


class TutorCreate(TutorBase):
    email: str
    password: str


class TutorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=255)
    cpf: Optional[str] = Field(None, max_length=14)
    phone: Optional[str] = Field(None, max_length=20)
    state: Optional[str] = Field(None, max_length=2)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    complement: Optional[str] = Field(None, max_length=200)
    pets: Optional[str] = None
    photo_url: Optional[str] = None


class TutorResponse(TutorBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

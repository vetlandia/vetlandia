from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.validators import validate_brazilian_state


class ClinicBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)  # Nome fantasia
    razao_social: Optional[str] = Field(None, max_length=255)
    cnpj: Optional[str] = Field(None, max_length=18)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    complement: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=500)
    convenios: Optional[str] = None       # JSON string
    animal_species: Optional[str] = None  # JSON string
    specialties: Optional[str] = None     # JSON string
    photo_url: Optional[str] = None  # data URL ou https URL
    cover_photo_url: Optional[str] = None
    is_24h: bool = False
    aplica_vacinas: bool = False
    num_veterinarios: Optional[str] = None
    open_hiring: bool = False
    open_internship: bool = False

    @field_validator("state")
    @classmethod
    def validate_state_code(cls, v: str) -> str:
        if not validate_brazilian_state(v):
            raise ValueError("Código de estado inválido")
        return v.upper()


class ClinicCreate(ClinicBase):
    email_user: str
    password: str


class ClinicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    razao_social: Optional[str] = Field(None, max_length=255)
    cnpj: Optional[str] = Field(None, max_length=18)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    complement: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = None
    photo_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    convenios: Optional[str] = None
    animal_species: Optional[str] = None
    specialties: Optional[str] = None
    is_24h: Optional[bool] = None
    aplica_vacinas: Optional[bool] = None
    num_veterinarios: Optional[str] = None
    consulta_faixa: Optional[str] = Field(None, max_length=20)
    procedimento_faixa: Optional[str] = Field(None, max_length=20)
    open_hiring: Optional[bool] = None
    open_internship: Optional[bool] = None


class ClinicResponse(ClinicBase):
    id: UUID
    user_id: UUID
    slug: str
    logo_url: Optional[str]
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClinicListItem(BaseModel):
    id: UUID
    name: str
    slug: str
    city: str
    state: str
    logo_url: Optional[str]

    class Config:
        from_attributes = True

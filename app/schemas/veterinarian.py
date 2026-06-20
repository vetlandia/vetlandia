from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.utils.validators import validate_brazilian_state, validate_crmv


class VeterinarianBase(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=255)
    cpf: Optional[str] = Field(None, max_length=14)
    crmv: str = Field(..., min_length=10, max_length=20)
    specialty: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    complement: Optional[str] = Field(None, max_length=200)
    animal_species: Optional[str] = None  # JSON string
    photo_url: Optional[str] = None  # data URL ou https URL
    cover_photo_url: Optional[str] = None
    is_24h: bool = False
    aplica_vacinas: bool = False
    # ── Módulo 1: enriquecimento do perfil ──────────────────────────────
    specialties: Optional[str] = None  # JSON array (especialidades múltiplas)
    website: Optional[str] = Field(None, max_length=500)
    linkedin: Optional[str] = Field(None, max_length=255)
    instagram: Optional[str] = Field(None, max_length=255)
    lattes: Optional[str] = Field(None, max_length=255)
    crmv_card_url: Optional[str] = None  # data URL ou https URL (carteira)

    @field_validator("crmv")
    @classmethod
    def validate_crmv_format(cls, v: str) -> str:
        if not validate_crmv(v):
            raise ValueError("CRMV inválido. Formato esperado: CRMV-UF XXXXX")
        return v

    @field_validator("state")
    @classmethod
    def validate_state_code(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_brazilian_state(v):
            raise ValueError("Código de estado inválido")
        return v.upper() if v else v


class VeterinarianCreate(VeterinarianBase):
    email: str
    password: str
    clinic_id: Optional[UUID] = None


class VeterinarianUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=255)
    cpf: Optional[str] = Field(None, max_length=14)
    specialty: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    photo_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    complement: Optional[str] = Field(None, max_length=200)
    animal_species: Optional[str] = None
    is_24h: Optional[bool] = None
    aplica_vacinas: Optional[bool] = None
    clinic_id: Optional[UUID] = None
    # ── Módulo 1 ────────────────────────────────────────────────────────
    specialties: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    linkedin: Optional[str] = Field(None, max_length=255)
    instagram: Optional[str] = Field(None, max_length=255)
    lattes: Optional[str] = Field(None, max_length=255)
    crmv_card_url: Optional[str] = None
    # ── Módulo 2: disponibilidades profissionais ────────────────────────
    disp_plantao: Optional[bool] = None
    disp_volante: Optional[bool] = None
    disp_oportunidades: Optional[bool] = None
    disp_parcerias: Optional[bool] = None


class EducationItem(BaseModel):
    """Uma formação acadêmica do veterinário."""
    tipo: str = Field(..., max_length=50)
    instituicao: str = Field(..., min_length=1, max_length=255)
    curso: Optional[str] = Field(None, max_length=255)
    area: Optional[str] = Field(None, max_length=255)
    ano_conclusao: Optional[str] = Field(None, max_length=4)


class EducationResponse(EducationItem):
    id: UUID

    class Config:
        from_attributes = True


class VeterinarianResponse(VeterinarianBase):
    id: UUID
    user_id: UUID
    slug: str
    photo_url: Optional[str]
    clinic_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VeterinarianListItem(BaseModel):
    id: UUID
    full_name: str
    crmv: str
    specialty: Optional[str]
    slug: str
    photo_url: Optional[str]
    city: Optional[str]
    state: Optional[str]

    class Config:
        from_attributes = True

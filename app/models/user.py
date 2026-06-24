import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class UserType(str, PyEnum):
    TUTOR = "tutor"
    VETERINARIAN = "veterinarian"
    CLINIC = "clinic"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def display_name(self) -> str:
        """Nome de exibição resolvido a partir do perfil relacionado."""

        def _first(rel):
            value = getattr(self, rel, None)
            if isinstance(value, list):
                return value[0] if value else None
            return value

        for rel in ("tutor", "veterinarian", "administrator"):
            profile = _first(rel)
            if profile and getattr(profile, "full_name", None):
                return profile.full_name

        clinic = _first("clinic")
        if clinic and getattr(clinic, "name", None):
            return clinic.name

        return self.email

    @property
    def photo_url(self):
        """Foto de perfil resolvida a partir do perfil relacionado."""

        def _first(rel):
            value = getattr(self, rel, None)
            if isinstance(value, list):
                return value[0] if value else None
            return value

        for rel in ("tutor", "veterinarian"):
            profile = _first(rel)
            if profile and getattr(profile, "photo_url", None):
                return profile.photo_url

        clinic = _first("clinic")
        if clinic:
            return getattr(clinic, "photo_url", None) or getattr(clinic, "logo_url", None)

        return None

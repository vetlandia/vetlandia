import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Veterinarian(Base):
    __tablename__ = "veterinarians"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=True)
    crmv = Column(String(20), unique=True, nullable=False, index=True)
    specialty = Column(String(100))
    bio = Column(Text)
    phone = Column(String(20))
    whatsapp = Column(String(20), nullable=True)
    photo_url = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    clinic_id = Column(UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=True)
    city = Column(String(100), index=True)
    state = Column(String(2), index=True)
    complement = Column(String(200), nullable=True)
    animal_species = Column(Text(), nullable=True)  # JSON array
    is_24h = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    is_rejected = Column(Boolean, default=False, nullable=False)  # reprovado (reversível) — Módulo 9
    is_founder = Column(Boolean, default=False, nullable=False)
    cover_photo_url = Column(Text, nullable=True)
    aplica_vacinas = Column(Boolean, default=False, nullable=False)
    # ── Módulo 1: enriquecimento do perfil ──────────────────────────────
    specialties = Column(Text(), nullable=True)        # JSON array (especialidades múltiplas)
    website = Column(String(500), nullable=True)       # site pessoal
    linkedin = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    lattes = Column(String(255), nullable=True)        # Currículo Lattes
    crmv_card_url = Column(Text, nullable=True)         # upload da carteira (validação manual)
    is_verified = Column(Boolean, default=False, nullable=False)  # selo "Perfil Verificado"
    # ── Módulo 2: disponibilidades profissionais (recrutamento, opcionais) ──
    disp_plantao = Column(Boolean, default=False, nullable=False)
    disp_volante = Column(Boolean, default=False, nullable=False)
    disp_oportunidades = Column(Boolean, default=False, nullable=False)
    disp_parcerias = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", backref="veterinarian", uselist=False)
    clinic = relationship("Clinic", backref="veterinarians", foreign_keys=[clinic_id])
    educations = relationship(
        "VetEducation",
        back_populates="veterinarian",
        cascade="all, delete-orphan",
        order_by="VetEducation.created_at",
    )
    clinic_links = relationship(
        "VetClinicLink",
        back_populates="veterinarian",
        cascade="all, delete-orphan",
        order_by="VetClinicLink.is_current.desc()",
    )
    contents = relationship(
        "VetContent",
        back_populates="veterinarian",
        cascade="all, delete-orphan",
        order_by="VetContent.created_at",
    )

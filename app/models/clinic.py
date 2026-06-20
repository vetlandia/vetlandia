import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(255), nullable=False)          # Nome fantasia
    razao_social = Column(String(255), nullable=True)   # Razão social
    cnpj = Column(String(18), nullable=True)
    description = Column(Text)
    address = Column(String(500))
    complement = Column(String(200), nullable=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    zip_code = Column(String(10))
    phone = Column(String(20))
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(255))
    website = Column(String(500))
    logo_url = Column(Text, nullable=True)
    photo_url = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    convenios = Column(Text(), nullable=True)       # JSON array
    animal_species = Column(Text(), nullable=True)  # JSON array
    specialties = Column(Text(), nullable=True)     # JSON array
    is_24h = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    is_rejected = Column(Boolean, default=False, nullable=False)  # reprovado (reversível) — Módulo 9
    is_founder = Column(Boolean, default=False, nullable=False)
    cover_photo_url = Column(Text, nullable=True)
    aplica_vacinas = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # selo "Perfil Verificado"
    # Módulo 6: acesso a recrutamento (ver disponibilidades/histórico dos vets).
    # Módulo 8 generaliza isto numa estrutura de entitlements.
    has_recruitment_access = Column(Boolean, default=False, nullable=False)
    # Módulo 7: faixas de preço (NUNCA valor exato): economica | intermediaria | premium
    consulta_faixa = Column(String(20), nullable=True)
    procedimento_faixa = Column(String(20), nullable=True)
    num_veterinarios = Column(String(10), nullable=True)  # qtd manual do responsável
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", backref="clinic", uselist=False)
    vet_links = relationship(
        "VetClinicLink",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )
    entitlements = relationship(
        "ClinicEntitlement",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )

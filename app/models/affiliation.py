import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VetClinicLink(Base):
    """Vínculo profissional entre veterinário e clínica (grafo N:N).

    Permite múltiplos vínculos simultâneos (corpo clínico atual) e também
    histórico profissional (vínculos passados, is_current=False).
    Responde: em quais clínicas o vet atua / quais vets atuam na clínica /
    quais especialidades existem na clínica (derivado dos vets vinculados).
    """

    __tablename__ = "vet_clinic_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    veterinarian_id = Column(
        UUID(as_uuid=True),
        ForeignKey("veterinarians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clinic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(120), nullable=True)        # cargo/função na clínica
    start_year = Column(String(4), nullable=True)
    end_year = Column(String(4), nullable=True)       # vazio = atual
    is_current = Column(Boolean, default=True, nullable=False)  # vínculo vigente?
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    veterinarian = relationship("Veterinarian", back_populates="clinic_links")
    clinic = relationship("Clinic", back_populates="vet_links")

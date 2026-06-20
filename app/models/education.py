import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VetEducation(Base):
    """Formação acadêmica do veterinário (múltiplas por profissional)."""

    __tablename__ = "vet_educations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    veterinarian_id = Column(
        UUID(as_uuid=True),
        ForeignKey("veterinarians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Graduação, Pós-graduação, Especialização, Residência, MBA, Mestrado, Doutorado
    tipo = Column(String(50), nullable=False)
    instituicao = Column(String(255), nullable=False)
    curso = Column(String(255), nullable=True)
    area = Column(String(255), nullable=True)
    ano_conclusao = Column(String(4), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    veterinarian = relationship("Veterinarian", back_populates="educations")

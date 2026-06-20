import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class VetContent(Base):
    """Conteúdo profissional do veterinário: links externos (sem upload).

    Substitui, na interface, os casos clínicos internos. Apenas links para
    artigos, casos publicados externamente, revistas, congressos, redes, etc.
    """

    __tablename__ = "vet_contents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    veterinarian_id = Column(
        UUID(as_uuid=True),
        ForeignKey("veterinarians.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Artigo, Caso clínico, Revista científica, Congresso, Publicação,
    # Instagram, LinkedIn, YouTube, Site
    tipo = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    url = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    veterinarian = relationship("Veterinarian", back_populates="contents")

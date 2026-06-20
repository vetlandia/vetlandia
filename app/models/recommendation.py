import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class RecommenderType(str, PyEnum):
    VETERINARIAN = "veterinarian"
    CLINIC = "clinic"


class RecommendationStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def _vals(enum):
    return [m.value for m in enum]


class Recommendation(Base):
    """Recomendação profissional: um veterinário ou clínica recomenda um vet.

    Aparece no perfil do veterinário recomendado (apenas aprovadas).
    Moderação obrigatória (status pending por padrão).
    """

    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # quem recomenda (vet ou clínica) — polimórfico, como Review
    author_type = Column(Enum(RecommenderType, values_callable=_vals), nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # veterinarians.id ou clinics.id
    # alvo recomendado (veterinário OU clínica) — polimórfico
    target_type = Column(Enum(RecommenderType, values_callable=_vals), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    # legado (mantido): FK para veterinário quando o alvo é vet
    target_vet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("veterinarians.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    content = Column(Text, nullable=False)
    status = Column(
        Enum(RecommendationStatus, values_callable=_vals),
        default=RecommendationStatus.PENDING,
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("author_type", "author_id", "target_type", "target_id", name="unique_recommendation_v2"),
        CheckConstraint("length(content) >= 10", name="min_recommendation_length"),
    )

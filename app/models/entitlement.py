import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

# Catálogo de produtos liberáveis por clínica (Módulo 8).
# Estrutura preparada para monetização futura; produtos ficam ocultos ao usuário.
# A ordem aqui é a usada na exibição do admin.
CLINIC_PRODUCTS = {
    "recrutamento": "Recrutamento",
    "banco_talentos": "Banco de talentos",
    "busca_avancada": "Busca avançada",
    "destaque": "Destaque",
}


class ClinicEntitlement(Base):
    """Liberação de um produto para uma clínica (sem cobrança nesta fase)."""

    __tablename__ = "clinic_entitlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clinic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product = Column(String(40), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    clinic = relationship("Clinic", back_populates="entitlements")

    __table_args__ = (
        UniqueConstraint("clinic_id", "product", name="unique_clinic_product"),
    )


def clinic_has_product(clinic, product: str) -> bool:
    """True se a clínica tem o produto liberado e ativo."""
    return any(e.product == product and e.is_active for e in clinic.entitlements)

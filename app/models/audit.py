import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class AuditLog(Base):
    """Histórico de exclusões e ações de moderação (quem, quando, o quê)."""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id = Column(UUID(as_uuid=True), nullable=True)  # quem fez (None = sistema)
    actor_label = Column(String(255), nullable=False)          # nome/papel cacheado p/ exibição
    action = Column(String(50), nullable=False)                # delete, approve, reject, verify...
    entity_type = Column(String(50), nullable=True)            # review, veterinarian, clinic...
    entity_id = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)                  # resumo legível
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


def log_action(db, actor, action, entity_type=None, entity_id=None, description=""):
    """Cria um registro de auditoria. `actor` é um User (ou None para sistema).
    Não faz commit — entra na transação corrente da operação."""
    label = "Sistema"
    if actor is not None:
        try:
            label = f"{actor.user_type.value}: {actor.display_name}"
        except Exception:
            label = str(getattr(actor, "email", "desconhecido"))
    db.add(
        AuditLog(
            actor_user_id=getattr(actor, "id", None),
            actor_label=label,
            action=action,
            entity_type=entity_type,
            entity_id=(str(entity_id) if entity_id else None),
            description=description,
        )
    )

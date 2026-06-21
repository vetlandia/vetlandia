import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ProfileView(Base):
    __tablename__ = "profile_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(20), nullable=False)   # "veterinarian" | "clinic"
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    viewer_ip_hash = Column(String(64), nullable=True)  # SHA-256 do IP (LGPD)
    viewer_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    viewed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_pv_entity_date", "entity_type", "entity_id", "viewed_at"),
        Index("idx_pv_date", "viewed_at"),
    )


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(String(200), nullable=True)
    specialty = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    entity_type = Column(String(20), nullable=True)   # "ambos" | "veterinario" | "clinica"
    result_count = Column(Integer, default=0)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    searched_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_sl_date", "searched_at"),
        Index("idx_sl_specialty", "specialty"),
        Index("idx_sl_city", "city"),
    )


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path = Column(String(500), nullable=False)
    ip_hash = Column(String(64), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_pgv_date", "occurred_at"),
        Index("idx_pgv_ip_date", "ip_hash", "occurred_at"),
    )

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
    photo_url = Column(String(500))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    clinic_id = Column(UUID(as_uuid=True), ForeignKey("clinics.id"), nullable=True)
    city = Column(String(100), index=True)
    state = Column(String(2), index=True)
    complement = Column(String(200), nullable=True)
    animal_species = Column(Text(), nullable=True)  # JSON array
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", backref="veterinarian", uselist=False)
    clinic = relationship("Clinic", backref="veterinarians", foreign_keys=[clinic_id])

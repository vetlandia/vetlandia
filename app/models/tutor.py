import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tutor(Base):
    __tablename__ = "tutors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    cpf = Column(String(14), nullable=True)
    phone = Column(String(20))
    state = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    complement = Column(String(200), nullable=True)
    pets = Column(Text(), nullable=True)  # JSON: [{name, species}]
    photo_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="tutor", uselist=False)

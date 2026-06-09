import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CaseStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ClinicalCase(Base):
    __tablename__ = "clinical_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("veterinarians.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    species = Column(String(50))
    breed = Column(String(100))
    specialty = Column(String(100), index=True)
    content = Column(Text, nullable=False)
    status = Column(
        Enum(CaseStatus, values_callable=lambda e: [m.value for m in e]),
        default=CaseStatus.PENDING,
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author = relationship("Veterinarian", backref="clinical_cases")
    comments = relationship("CaseComment", back_populates="case", cascade="all, delete-orphan")


class CaseComment(Base):
    __tablename__ = "case_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("clinical_cases.id"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("veterinarians.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    case = relationship("ClinicalCase", back_populates="comments")
    author = relationship("Veterinarian", backref="case_comments")

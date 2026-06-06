from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CaseCommentBase(BaseModel):
    content: str = Field(..., min_length=10)


class CaseCommentCreate(CaseCommentBase):
    pass


class CaseCommentResponse(CaseCommentBase):
    id: UUID
    case_id: UUID
    author_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CaseCommentWithAuthor(CaseCommentResponse):
    author_name: str
    author_crmv: str


class ClinicalCaseBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=255)
    species: Optional[str] = Field(None, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    specialty: Optional[str] = Field(None, max_length=100)
    content: str = Field(..., min_length=100)


class ClinicalCaseCreate(ClinicalCaseBase):
    pass


class ClinicalCaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    species: Optional[str] = Field(None, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    specialty: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = Field(None, min_length=100)


class ClinicalCaseResponse(ClinicalCaseBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClinicalCaseWithAuthor(ClinicalCaseResponse):
    author_name: str
    author_crmv: str
    author_slug: str


class ClinicalCaseDetail(ClinicalCaseWithAuthor):
    comments: List[CaseCommentWithAuthor] = []

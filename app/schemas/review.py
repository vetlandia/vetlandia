from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.review import RevieweeType


class ReviewBase(BaseModel):
    reviewee_type: RevieweeType
    reviewee_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=50)


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewWithAuthor(ReviewResponse):
    author_name: Optional[str] = None

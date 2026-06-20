from uuid import UUID

from pydantic import BaseModel, Field


class RecommendationCreate(BaseModel):
    target_vet_id: UUID
    content: str = Field(..., min_length=10, max_length=1000)

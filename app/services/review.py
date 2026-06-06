from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.review import Review, RevieweeType
from app.schemas.review import ReviewCreate


def create_review(db: Session, user_id: UUID, data: ReviewCreate) -> Review:
    existing = (
        db.query(Review)
        .filter(
            Review.author_id == user_id,
            Review.reviewee_type == data.reviewee_type,
            Review.reviewee_id == data.reviewee_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Você já avaliou este perfil",
        )

    review = Review(
        author_id=user_id,
        reviewee_type=data.reviewee_type,
        reviewee_id=data.reviewee_id,
        rating=data.rating,
        comment=data.comment,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def get_reviews_for_entity(
    db: Session,
    reviewee_type: RevieweeType,
    reviewee_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> List[Review]:
    return (
        db.query(Review)
        .filter(
            Review.reviewee_type == reviewee_type,
            Review.reviewee_id == reviewee_id,
        )
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def calculate_average_rating(
    db: Session,
    reviewee_type: RevieweeType,
    reviewee_id: UUID,
) -> dict:
    from sqlalchemy import func

    result = (
        db.query(
            func.avg(Review.rating).label("average"),
            func.count(Review.id).label("count"),
        )
        .filter(
            Review.reviewee_type == reviewee_type,
            Review.reviewee_id == reviewee_id,
        )
        .first()
    )

    return {
        "average": round(result.average, 1) if result.average else 0,
        "count": result.count or 0,
    }

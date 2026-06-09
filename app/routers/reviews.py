from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate
from app.services.review import create_review

router = APIRouter()


@router.post("/")
def submit_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça login para avaliar")
    if current_user.user_type.value != "tutor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas tutores podem enviar avaliações")
    review = create_review(db, current_user.id, data)
    return {"ok": True, "review_id": str(review.id)}

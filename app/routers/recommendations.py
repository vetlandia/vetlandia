from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.clinic import Clinic
from app.models.recommendation import Recommendation, RecommenderType
from app.models.user import User
from app.models.veterinarian import Veterinarian
from app.schemas.recommendation import RecommendationCreate

router = APIRouter()


@router.post("/")
def submit_recommendation(
    data: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça login para recomendar")

    utype = current_user.user_type.value
    if utype == "veterinarian":
        author = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
        author_type = RecommenderType.VETERINARIAN
    elif utype == "clinic":
        author = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
        author_type = RecommenderType.CLINIC
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas veterinários e clínicas podem recomendar")

    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    target = db.query(Veterinarian).filter(Veterinarian.id == data.target_vet_id).first()
    if not target or not target.is_approved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinário(a) não encontrado(a)")

    if author_type == RecommenderType.VETERINARIAN and author.id == target.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode recomendar a si mesmo")

    existing = (
        db.query(Recommendation)
        .filter(
            Recommendation.author_type == author_type,
            Recommendation.author_id == author.id,
            Recommendation.target_vet_id == target.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Você já recomendou este(a) profissional")

    rec = Recommendation(
        author_type=author_type,
        author_id=author.id,
        target_vet_id=target.id,
        content=data.content,
    )
    db.add(rec)
    db.commit()
    return {"ok": True}

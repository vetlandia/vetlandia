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
    """Veterinário ou clínica indica um veterinário OU uma clínica."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça login para indicar")

    utype = current_user.user_type.value
    if utype == "veterinarian":
        author = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
        author_type = RecommenderType.VETERINARIAN
    elif utype == "clinic":
        author = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
        author_type = RecommenderType.CLINIC
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas veterinários e clínicas podem indicar")
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil não encontrado")

    # Resolve o alvo (vet ou clínica)
    if data.target_type == "veterinarian":
        target = db.query(Veterinarian).filter(Veterinarian.id == data.target_id).first()
        target_type = RecommenderType.VETERINARIAN
    else:
        target = db.query(Clinic).filter(Clinic.id == data.target_id).first()
        target_type = RecommenderType.CLINIC
    if not target or not target.is_approved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil a indicar não encontrado")

    if author_type == target_type and author.id == target.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Você não pode indicar a si mesmo")

    existing = (
        db.query(Recommendation)
        .filter(
            Recommendation.author_type == author_type,
            Recommendation.author_id == author.id,
            Recommendation.target_type == target_type,
            Recommendation.target_id == target.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Você já indicou este perfil")

    rec = Recommendation(
        author_type=author_type,
        author_id=author.id,
        target_type=target_type,
        target_id=target.id,
        target_vet_id=(target.id if target_type == RecommenderType.VETERINARIAN else None),
        content=data.content,
    )
    db.add(rec)
    db.commit()
    return {"ok": True}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.audit import log_action
from app.models.clinic import Clinic
from app.models.review import Review, RevieweeType
from app.models.user import User
from app.models.veterinarian import Veterinarian
from app.schemas.review import ReviewCreate
from app.services.review import create_review
from app.services.email import send_email, tpl_nova_avaliacao

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
    # Notifica o vet ou clínica que recebeu a avaliação
    if data.reviewee_type == RevieweeType.VETERINARIAN:
        reviewee = db.query(Veterinarian).filter(Veterinarian.id == data.reviewee_id).first()
        if reviewee:
            reviewee_user = db.query(User).filter(User.id == reviewee.user_id).first()
            if reviewee_user:
                profile_url = f"https://vetlandia.com.br/veterinario/{reviewee.slug}"
                send_email(
                    reviewee_user.email,
                    f"Você recebeu uma nova avaliação — VetLândia",
                    tpl_nova_avaliacao(reviewee.full_name, current_user.display_name or current_user.email,
                                       review.rating, review.comment, profile_url),
                )
    else:
        reviewee = db.query(Clinic).filter(Clinic.id == data.reviewee_id).first()
        if reviewee:
            reviewee_user = db.query(User).filter(User.id == reviewee.user_id).first()
            if reviewee_user:
                profile_url = f"https://vetlandia.com.br/clinica/{reviewee.slug}"
                send_email(
                    reviewee_user.email,
                    f"Você recebeu uma nova avaliação — VetLândia",
                    tpl_nova_avaliacao(reviewee.name, current_user.display_name or current_user.email,
                                       review.rating, review.comment, profile_url),
                )
    return {"ok": True, "review_id": str(review.id)}


@router.delete("/{review_id}")
def delete_own_review(
    review_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permite ao veterinário/clínica excluir uma avaliação do PRÓPRIO perfil.
    A exclusão fica registrada no histórico de auditoria."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça login")

    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avaliação não encontrada")

    utype = current_user.user_type.value
    owned = False
    if utype == "veterinarian" and review.reviewee_type == RevieweeType.VETERINARIAN:
        vet = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
        owned = bool(vet and vet.id == review.reviewee_id)
    elif utype == "clinic" and review.reviewee_type == RevieweeType.CLINIC:
        clinic = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
        owned = bool(clinic and clinic.id == review.reviewee_id)

    if not owned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você só pode excluir avaliações do seu próprio perfil")

    log_action(
        db, current_user, "delete", "review", review_id,
        f"Excluiu avaliação do próprio perfil (nota {review.rating}): {(review.comment or '')[:60]}",
    )
    db.delete(review)
    db.commit()
    return {"ok": True}

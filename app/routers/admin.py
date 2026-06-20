from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.core.assets import ASSET_VERSION
from app.core.database import get_db
from app.core.deps import require_admin
from app.models.case import CaseComment, CaseStatus, ClinicalCase
from app.models.clinic import Clinic
from app.models.comment import Comment
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.review import Review, ReviewStatus
from app.models.tutor import Tutor
from app.models.user import User, UserType
from app.models.veterinarian import Veterinarian

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["asset_v"] = ASSET_VERSION


def _admin_context(request: Request, db: Session, **kwargs):
    pending_vets = db.query(Veterinarian).filter(Veterinarian.is_approved == False).count()
    pending_clinics = db.query(Clinic).filter(Clinic.is_approved == False).count()
    pending_reviews = db.query(Review).filter(Review.status == ReviewStatus.PENDING).count()
    pending_cases_count = db.query(ClinicalCase).filter(ClinicalCase.status == CaseStatus.PENDING).count()
    pending_comments_count = db.query(CaseComment).filter(CaseComment.status == CaseStatus.PENDING).count()
    pending_recs_count = db.query(Recommendation).filter(Recommendation.status == RecommendationStatus.PENDING).count()
    return {
        "request": request,
        "pending_vets": pending_vets,
        "pending_clinics": pending_clinics,
        "pending_reviews": pending_reviews,
        "pending_cases_count": pending_cases_count,
        "pending_comments_count": pending_comments_count,
        "pending_recs_count": pending_recs_count,
        **kwargs,
    }


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    vets = db.query(Veterinarian).filter(Veterinarian.is_approved == False).order_by(Veterinarian.created_at.desc()).all()
    clinics = db.query(Clinic).filter(Clinic.is_approved == False).order_by(Clinic.created_at.desc()).all()
    approved_vets = db.query(Veterinarian).filter(Veterinarian.is_approved == True).order_by(Veterinarian.full_name).all()
    approved_clinics = db.query(Clinic).filter(Clinic.is_approved == True).order_by(Clinic.name).all()
    reviews = db.query(Review).filter(Review.status == ReviewStatus.PENDING).order_by(Review.created_at.desc()).all()
    published_reviews = db.query(Review).filter(Review.status == ReviewStatus.APPROVED).order_by(Review.created_at.desc()).all()
    pending_cases = (
        db.query(ClinicalCase)
        .options(joinedload(ClinicalCase.author))
        .filter(ClinicalCase.status == CaseStatus.PENDING)
        .order_by(ClinicalCase.created_at.desc())
        .all()
    )
    pending_comments = (
        db.query(CaseComment)
        .options(joinedload(CaseComment.author), joinedload(CaseComment.case))
        .filter(CaseComment.status == CaseStatus.PENDING)
        .order_by(CaseComment.created_at.desc())
        .all()
    )
    users = db.query(User).filter(User.user_type != UserType.ADMIN).order_by(User.created_at.desc()).all()

    pending_recs = _resolve_recommendations(
        db,
        db.query(Recommendation)
        .filter(Recommendation.status == RecommendationStatus.PENDING)
        .order_by(Recommendation.created_at.desc())
        .all(),
    )

    return templates.TemplateResponse(
        "admin/dashboard.html",
        _admin_context(
            request, db,
            vets=vets, clinics=clinics,
            approved_vets=approved_vets, approved_clinics=approved_clinics,
            reviews=reviews, published_reviews=published_reviews,
            pending_cases=pending_cases,
            pending_comments=pending_comments,
            pending_recs=pending_recs,
            users=users, admin=admin,
        ),
    )


def _resolve_recommendations(db: Session, recs):
    """Resolve nome do autor (vet/clínica) e do alvo para exibição."""
    out = []
    for r in recs:
        if r.author_type.value == "veterinarian":
            a = db.query(Veterinarian).filter(Veterinarian.id == r.author_id).first()
            author_name = a.full_name if a else "Veterinário(a)"
        else:
            a = db.query(Clinic).filter(Clinic.id == r.author_id).first()
            author_name = a.name if a else "Clínica"
        target = db.query(Veterinarian).filter(Veterinarian.id == r.target_vet_id).first()
        out.append({
            "id": str(r.id),
            "author_name": author_name,
            "author_type": r.author_type.value,
            "target_name": target.full_name if target else "—",
            "target_slug": target.slug if target else "",
            "content": r.content,
        })
    return out


# ── Veterinários ──────────────────────────────────────────────────────────────

@router.post("/vets/{vet_id}/approve")
def approve_vet(vet_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    vet.is_approved = True
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vets/{vet_id}/reject")
def reject_vet(vet_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    db.query(Review).filter(Review.reviewee_id == vet.id).delete()
    db.delete(vet)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vets/{vet_id}/delete")
def delete_vet(vet_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    db.query(Review).filter(Review.reviewee_id == vet.id).delete()
    db.delete(vet)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vets/{vet_id}/set-badge")
def set_vet_badge(vet_id: str, badge_type: str = Form(...), db: Session = Depends(get_db), admin=Depends(require_admin)):
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    vet.is_founder = (badge_type == "founder")
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vets/{vet_id}/verify")
def verify_vet(vet_id: str, verified: str = Form(...), db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Concede/remove o selo 'Perfil Verificado' (identidade + CRMV validado)."""
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    vet.is_verified = (verified == "true")
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


# ── Clínicas ──────────────────────────────────────────────────────────────────

@router.post("/clinics/{clinic_id}/approve")
def approve_clinic(clinic_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    clinic.is_approved = True
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/set-badge")
def set_clinic_badge(clinic_id: str, badge_type: str = Form(...), db: Session = Depends(get_db), admin=Depends(require_admin)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    clinic.is_founder = (badge_type == "founder")
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/verify")
def verify_clinic(clinic_id: str, verified: str = Form(...), db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Concede/remove o selo 'Perfil Verificado' da clínica."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    clinic.is_verified = (verified == "true")
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/delete")
def delete_clinic(clinic_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    db.query(Review).filter(Review.reviewee_id == clinic.id).delete()
    db.delete(clinic)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/reject")
def reject_clinic(clinic_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    db.query(Review).filter(Review.reviewee_id == clinic.id).delete()
    db.delete(clinic)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


# ── Reviews ───────────────────────────────────────────────────────────────────

@router.post("/reviews/{review_id}/approve")
def approve_review(review_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    review.status = ReviewStatus.APPROVED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/reviews/{review_id}/reject")
def reject_review(review_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    review.status = ReviewStatus.REJECTED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/reviews/{review_id}/delete")
def delete_review(review_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    db.delete(review)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


# ── Recomendações ─────────────────────────────────────────────────────────────

@router.post("/recommendations/{rec_id}/approve")
def approve_recommendation(rec_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recomendação não encontrada")
    rec.status = RecommendationStatus.APPROVED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/recommendations/{rec_id}/reject")
def reject_recommendation(rec_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recomendação não encontrada")
    rec.status = RecommendationStatus.REJECTED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/recommendations/{rec_id}/delete")
def delete_recommendation(rec_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recomendação não encontrada")
    db.delete(rec)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


# ── Usuários ──────────────────────────────────────────────────────────────────

@router.post("/users/{user_id}/block")
def block_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.user_type == UserType.ADMIN:
        raise HTTPException(status_code=400, detail="Não é possível inativar admin")
    user.is_active = False
    vet = db.query(Veterinarian).filter(Veterinarian.user_id == user.id).first()
    if vet:
        vet.is_approved = False
    clinic = db.query(Clinic).filter(Clinic.user_id == user.id).first()
    if clinic:
        clinic.is_approved = False
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/{user_id}/unblock")
def unblock_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_active = True
    vet = db.query(Veterinarian).filter(Veterinarian.user_id == user.id).first()
    if vet:
        vet.is_approved = True
    clinic = db.query(Clinic).filter(Clinic.user_id == user.id).first()
    if clinic:
        clinic.is_approved = True
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


def _delete_reviews(reviewee_or_author_ids, column, db: Session):
    """Apaga avaliações (e seus comentários) por reviewee_id ou author_id."""
    SS = {"synchronize_session": False}
    rev_ids = [r[0] for r in db.query(Review.id).filter(column.in_(reviewee_or_author_ids)).all()]
    if rev_ids:
        db.query(Comment).filter(Comment.review_id.in_(rev_ids)).delete(**SS)
        db.query(Review).filter(Review.id.in_(rev_ids)).delete(**SS)


def _delete_user_and_profiles(user: User, db: Session):
    SS = {"synchronize_session": False}

    # ── Perfil de veterinário ───────────────────────────────────────────
    vet = db.query(Veterinarian).filter(Veterinarian.user_id == user.id).first()
    if vet:
        case_ids = [r[0] for r in db.query(ClinicalCase.id).filter(ClinicalCase.author_id == vet.id).all()]
        # Comentários nos casos publicados por este vet (de qualquer autor)
        if case_ids:
            db.query(CaseComment).filter(CaseComment.case_id.in_(case_ids)).delete(**SS)
        # Comentários escritos por este vet em qualquer caso
        db.query(CaseComment).filter(CaseComment.author_id == vet.id).delete(**SS)
        # Casos clínicos do vet
        if case_ids:
            db.query(ClinicalCase).filter(ClinicalCase.id.in_(case_ids)).delete(**SS)
        # Avaliações recebidas pelo vet (+ comentários)
        _delete_reviews([vet.id], Review.reviewee_id, db)
        db.delete(vet)
        db.flush()

    # ── Perfil de clínica ───────────────────────────────────────────────
    clinic = db.query(Clinic).filter(Clinic.user_id == user.id).first()
    if clinic:
        # Desvincular vets que apontam para esta clínica
        db.query(Veterinarian).filter(Veterinarian.clinic_id == clinic.id).update({"clinic_id": None}, **SS)
        # Avaliações recebidas pela clínica (+ comentários)
        _delete_reviews([clinic.id], Review.reviewee_id, db)
        db.delete(clinic)
        db.flush()

    # ── Perfil de tutor ─────────────────────────────────────────────────
    tutor = db.query(Tutor).filter(Tutor.user_id == user.id).first()
    if tutor:
        db.delete(tutor)
        db.flush()

    # ── Conteúdo escrito pelo próprio usuário ────────────────────────────
    # Comentários de avaliações escritos pelo usuário
    db.query(Comment).filter(Comment.author_id == user.id).delete(**SS)
    # Avaliações escritas pelo usuário (+ comentários nelas)
    _delete_reviews([user.id], Review.author_id, db)

    db.delete(user)
    db.flush()


@router.post("/users/{user_id}/delete")
def delete_user(user_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.user_type == UserType.ADMIN:
        raise HTTPException(status_code=400, detail="Não é possível excluir admin")
    _delete_user_and_profiles(user, db)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/bulk-action")
def bulk_user_action(
    action: str = Form(...),
    user_ids: List[str] = Form(default=[]),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    for uid in user_ids:
        user = db.query(User).filter(User.id == uid).first()
        if not user or user.user_type == UserType.ADMIN:
            continue
        if action == "approve":
            user.is_active = True
            vet = db.query(Veterinarian).filter(Veterinarian.user_id == user.id).first()
            if vet:
                vet.is_approved = True
            clinic = db.query(Clinic).filter(Clinic.user_id == user.id).first()
            if clinic:
                clinic.is_approved = True
        elif action == "inativar":
            user.is_active = False
            vet = db.query(Veterinarian).filter(Veterinarian.user_id == user.id).first()
            if vet:
                vet.is_approved = False
            clinic = db.query(Clinic).filter(Clinic.user_id == user.id).first()
            if clinic:
                clinic.is_approved = False
        elif action == "excluir":
            _delete_user_and_profiles(user, db)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


# ── Casos Clínicos ────────────────────────────────────────────────────────────

@router.post("/comments/{comment_id}/approve")
def approve_comment(comment_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    comment = db.query(CaseComment).filter(CaseComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    comment.status = CaseStatus.APPROVED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/comments/{comment_id}/reject")
def reject_comment(comment_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    comment = db.query(CaseComment).filter(CaseComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    comment.status = CaseStatus.REJECTED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/comments/{comment_id}/delete")
def delete_comment(comment_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    comment = db.query(CaseComment).filter(CaseComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    db.delete(comment)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/cases/{case_id}/approve")
def approve_case(case_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    case = db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    case.status = CaseStatus.APPROVED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/cases/{case_id}/reject")
def reject_case(case_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    case = db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    case.status = CaseStatus.REJECTED
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/cases/{case_id}/delete")
def delete_case(case_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    case = db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    db.delete(case)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)

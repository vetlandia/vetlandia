from typing import List

import base64
import re

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session, joinedload

from app.core.assets import ASSET_VERSION
from app.core.database import get_db
from app.core.deps import require_admin
from app.models.audit import AuditLog, log_action
from app.services.email import (
    send_email,
    tpl_aprovacao,
    tpl_reprovacao,
    tpl_avaliacao_publicada,
    tpl_recomendacao_publicada,
)
from app.models.case import CaseComment, CaseStatus, ClinicalCase
from app.models.clinic import Clinic
from app.models.comment import Comment
from app.models.entitlement import CLINIC_PRODUCTS, ClinicEntitlement
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.review import Review, ReviewStatus
from app.models.tutor import Tutor
from app.models.user import User, UserType
from app.models.veterinarian import Veterinarian

from app.core.templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])
templates.env.globals["asset_v"] = ASSET_VERSION


def _admin_context(request: Request, db: Session, **kwargs):
    pending_vets = db.query(Veterinarian).filter(Veterinarian.is_approved == False, Veterinarian.is_rejected == False).count()
    pending_clinics = db.query(Clinic).filter(Clinic.is_approved == False, Clinic.is_rejected == False).count()
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
    vets = db.query(Veterinarian).filter(Veterinarian.is_approved == False, Veterinarian.is_rejected == False).order_by(Veterinarian.created_at.desc()).all()
    clinics = db.query(Clinic).filter(Clinic.is_approved == False, Clinic.is_rejected == False).order_by(Clinic.created_at.desc()).all()
    rejected_vets = db.query(Veterinarian).filter(Veterinarian.is_rejected == True).order_by(Veterinarian.created_at.desc()).all()
    rejected_clinics = db.query(Clinic).filter(Clinic.is_rejected == True).order_by(Clinic.created_at.desc()).all()
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

    # Módulo 8: produtos ativos por clínica (para os toggles no admin)
    clinic_products = {
        str(c.id): {e.product for e in c.entitlements if e.is_active}
        for c in approved_clinics
    }

    audit_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        _admin_context(
            request, db,
            vets=vets, clinics=clinics,
            rejected_vets=rejected_vets, rejected_clinics=rejected_clinics,
            approved_vets=approved_vets, approved_clinics=approved_clinics,
            reviews=reviews, published_reviews=published_reviews,
            pending_cases=pending_cases,
            pending_comments=pending_comments,
            pending_recs=pending_recs,
            clinic_products=clinic_products,
            clinic_products_catalog=CLINIC_PRODUCTS,
            audit_logs=audit_logs,
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
        if r.target_type.value == "clinic":
            t = db.query(Clinic).filter(Clinic.id == r.target_id).first()
            target_name = t.name if t else "—"
            target_url = ("/clinica/" + t.slug) if t else ""
        else:
            t = db.query(Veterinarian).filter(Veterinarian.id == r.target_id).first()
            target_name = t.full_name if t else "—"
            target_url = ("/veterinario/" + t.slug) if t else ""
        out.append({
            "id": str(r.id),
            "author_name": author_name,
            "author_type": r.author_type.value,
            "target_name": target_name,
            "target_url": target_url,
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
    vet.is_rejected = False
    log_action(db, admin, "approve", "veterinarian", vet_id, f"Aprovou veterinário(a) {vet.full_name}")
    db.commit()
    user = db.query(User).filter(User.id == vet.user_id).first()
    if user:
        profile_url = f"https://vetlandia.com.br/veterinario/{vet.slug}"
        send_email(user.email, "Perfil aprovado no VetLândia! 🎉", tpl_aprovacao(vet.full_name, "veterinarian", profile_url))
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vets/{vet_id}/reject")
def reject_vet(vet_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Reprova de forma REVERSÍVEL (Módulo 9): marca is_rejected, não apaga."""
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    vet.is_rejected = True
    vet.is_approved = False
    log_action(db, admin, "reject", "veterinarian", vet_id, f"Reprovou veterinário(a) {vet.full_name}")
    db.commit()
    user = db.query(User).filter(User.id == vet.user_id).first()
    if user:
        send_email(user.email, "Informação sobre seu cadastro — VetLândia", tpl_reprovacao(vet.full_name, "veterinarian"))
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vets/{vet_id}/restore")
def restore_vet(vet_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Reverte a reprovação: volta o veterinário para a fila de pendentes."""
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    vet.is_rejected = False
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/vets/{vet_id}/delete")
def delete_vet(vet_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    db.query(Review).filter(Review.reviewee_id == vet.id).delete()
    db.delete(vet)
    log_action(db, admin, "delete", "veterinarian", vet_id, f"Excluiu veterinário(a) {vet.full_name} ({vet.crmv})")
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
    log_action(db, admin, "verify" if vet.is_verified else "unverify", "veterinarian", vet_id,
               ("Verificou CRMV de " if vet.is_verified else "Removeu verificação de ") + vet.full_name)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/vets/{vet_id}/carteira")
def view_vet_carteira(vet_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Serve a imagem da carteira do CRMV (data URL base64) para o admin abrir.
    Necessário porque navegadores bloqueiam abrir data: URLs diretamente."""
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet or not vet.crmv_card_url:
        raise HTTPException(status_code=404, detail="Carteira não enviada")
    url = vet.crmv_card_url
    if url.startswith("data:"):
        m = re.match(r"data:([^;]+);base64,(.*)", url, re.DOTALL)
        if not m:
            raise HTTPException(status_code=400, detail="Formato de carteira inválido")
        try:
            data = base64.b64decode(m.group(2))
        except Exception:
            raise HTTPException(status_code=400, detail="Carteira corrompida")
        return Response(content=data, media_type=m.group(1))
    return RedirectResponse(url)


@router.get("/vets/{vet_id}/validar-crmv", response_class=HTMLResponse)
def validar_crmv_page(vet_id: str, request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Tela de validação: dados do vet + carteira ao lado da consulta oficial
    do CFMV (embutida), para o admin conferir e confirmar."""
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinário(a) não encontrado(a)")
    return templates.TemplateResponse("admin/validar_crmv.html", {"request": request, "vet": vet})


# ── Clínicas ──────────────────────────────────────────────────────────────────

@router.post("/clinics/{clinic_id}/approve")
def approve_clinic(clinic_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    clinic.is_approved = True
    clinic.is_rejected = False
    log_action(db, admin, "approve", "clinic", clinic_id, f"Aprovou clínica {clinic.name}")
    db.commit()
    user = db.query(User).filter(User.id == clinic.user_id).first()
    if user:
        profile_url = f"https://vetlandia.com.br/clinica/{clinic.slug}"
        send_email(user.email, "Perfil aprovado no VetLândia! 🎉", tpl_aprovacao(clinic.name, "clinic", profile_url))
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


@router.post("/clinics/{clinic_id}/recruitment-access")
def set_clinic_recruitment_access(clinic_id: str, access: str = Form(...), db: Session = Depends(get_db), admin=Depends(require_admin)):
    """[legado Módulo 6] Mantido por compatibilidade; o controle agora é por
    entitlements (Módulo 8). Rota preservada, sem botão na interface."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    clinic.has_recruitment_access = (access == "true")
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/entitlement")
def toggle_clinic_entitlement(
    clinic_id: str,
    product: str = Form(...),
    active: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Libera/remove um produto para a clínica (Módulo 8 — sem cobrança)."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    if product not in CLINIC_PRODUCTS:
        raise HTTPException(status_code=400, detail="Produto inválido")
    want_active = (active == "true")
    ent = (
        db.query(ClinicEntitlement)
        .filter(ClinicEntitlement.clinic_id == clinic.id, ClinicEntitlement.product == product)
        .first()
    )
    if ent:
        ent.is_active = want_active
    else:
        db.add(ClinicEntitlement(clinic_id=clinic.id, product=product, is_active=want_active))
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/delete")
def delete_clinic(clinic_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    db.query(Review).filter(Review.reviewee_id == clinic.id).delete()
    db.delete(clinic)
    log_action(db, admin, "delete", "clinic", clinic_id, f"Excluiu clínica {clinic.name}")
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/reject")
def reject_clinic(clinic_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Reprova de forma REVERSÍVEL (Módulo 9): marca is_rejected, não apaga."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    clinic.is_rejected = True
    clinic.is_approved = False
    log_action(db, admin, "reject", "clinic", clinic_id, f"Reprovou clínica {clinic.name}")
    db.commit()
    user = db.query(User).filter(User.id == clinic.user_id).first()
    if user:
        send_email(user.email, "Informação sobre seu cadastro — VetLândia", tpl_reprovacao(clinic.name, "clinic"))
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/clinics/{clinic_id}/restore")
def restore_clinic(clinic_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Reverte a reprovação: volta a clínica para a fila de pendentes."""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada")
    clinic.is_rejected = False
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


# ── Reviews ───────────────────────────────────────────────────────────────────

@router.post("/reviews/{review_id}/approve")
def approve_review(review_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    from app.models.review import RevieweeType
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    review.status = ReviewStatus.APPROVED
    db.commit()
    # Notifica o autor (tutor) que a avaliação foi publicada
    author_user = db.query(User).filter(User.id == review.author_id).first()
    if author_user:
        if review.reviewee_type == RevieweeType.VETERINARIAN:
            reviewee = db.query(Veterinarian).filter(Veterinarian.id == review.reviewee_id).first()
            reviewee_name = reviewee.full_name if reviewee else "o veterinário"
            profile_url = f"https://vetlandia.com.br/veterinario/{reviewee.slug}" if reviewee else "https://vetlandia.com.br"
        else:
            reviewee = db.query(Clinic).filter(Clinic.id == review.reviewee_id).first()
            reviewee_name = reviewee.name if reviewee else "a clínica"
            profile_url = f"https://vetlandia.com.br/clinica/{reviewee.slug}" if reviewee else "https://vetlandia.com.br"
        send_email(
            author_user.email,
            "Sua avaliação foi publicada — VetLândia",
            tpl_avaliacao_publicada(author_user.display_name or author_user.email, reviewee_name, profile_url),
        )
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/reviews/{review_id}/reject")
def reject_review(review_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    review.status = ReviewStatus.REJECTED
    log_action(db, admin, "reject", "review", review_id, f"Reprovou avaliação (nota {review.rating})")
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/reviews/{review_id}/delete")
def delete_review(review_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    log_action(db, admin, "delete", "review", review_id, f"Excluiu avaliação (nota {review.rating}): {(review.comment or '')[:60]}")
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
    # Notifica o autor (vet ou clínica) que a recomendação foi publicada
    if rec.author_type.value == "veterinarian":
        author_profile = db.query(Veterinarian).filter(Veterinarian.id == rec.author_id).first()
        author_name = author_profile.full_name if author_profile else "Veterinário(a)"
        author_user = db.query(User).filter(User.id == author_profile.user_id).first() if author_profile else None
    else:
        author_profile = db.query(Clinic).filter(Clinic.id == rec.author_id).first()
        author_name = author_profile.name if author_profile else "Clínica"
        author_user = db.query(User).filter(User.id == author_profile.user_id).first() if author_profile else None
    if rec.target_type.value == "veterinarian":
        target = db.query(Veterinarian).filter(Veterinarian.id == rec.target_id).first()
        target_name = target.full_name if target else "o veterinário"
        profile_url = f"https://vetlandia.com.br/veterinario/{target.slug}" if target else "https://vetlandia.com.br"
    else:
        target = db.query(Clinic).filter(Clinic.id == rec.target_id).first()
        target_name = target.name if target else "a clínica"
        profile_url = f"https://vetlandia.com.br/clinica/{target.slug}" if target else "https://vetlandia.com.br"
    if author_user:
        send_email(
            author_user.email,
            "Sua recomendação foi publicada — VetLândia",
            tpl_recomendacao_publicada(author_name, target_name, profile_url),
        )
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
    log_action(db, admin, "delete", "recommendation", rec_id, "Excluiu recomendação")
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
    log_action(db, admin, "delete", "user", user_id, f"Excluiu usuário {user.display_name} ({user.email})")
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
    log_action(db, admin, "delete", "case_comment", comment_id, "Excluiu comentário de caso")
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
    log_action(db, admin, "delete", "clinical_case", case_id, f"Excluiu caso clínico: {case.title}")
    db.delete(case)
    db.commit()
    return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/test-email", response_class=HTMLResponse)
def test_email_form(admin=Depends(require_admin)):
    """Mostra config SMTP atual e formulário para disparo de teste."""
    from app.core.config import settings as _s
    cfg = [
        ("SMTP_HOST", _s.SMTP_HOST),
        ("SMTP_PORT", str(_s.SMTP_PORT)),
        ("SMTP_USER", _s.SMTP_USER or "(vazio)"),
        ("SMTP_PASSWORD", "configurada" if _s.SMTP_PASSWORD else "(vazio — e-mails ignorados)"),
    ]
    cfg_html = "".join(f"<tr><td style='padding:6px 12px;font-weight:700'>{k}</td><td style='padding:6px 12px;font-family:monospace'>{v}</td></tr>" for k, v in cfg)
    return f"""<html><body style='font-family:sans-serif;padding:32px;max-width:600px'>
    <h2>Teste SMTP — VetLândia</h2>
    <table border='1' cellspacing='0' style='border-collapse:collapse;margin-bottom:24px;width:100%'>{cfg_html}</table>
    <form method='POST' action='/admin/test-email'>
        <label style='display:block;margin-bottom:6px'>Enviar para:</label>
        <input name='to' type='email' placeholder='email@exemplo.com' required
               style='padding:8px 12px;border:1px solid #ccc;border-radius:6px;width:300px;margin-right:8px'>
        <button type='submit' style='padding:8px 18px;background:#088395;color:#fff;border:none;border-radius:6px;cursor:pointer'>Enviar teste</button>
    </form>
    <p style='margin-top:24px'><a href='/admin'>← Voltar ao admin</a></p>
    </body></html>"""


@router.post("/test-email", response_class=HTMLResponse)
def test_email_send(to: str = Form(...), admin=Depends(require_admin)):
    """Dispara e-mail de teste síncrono com timeout curto e retorna erro exato."""
    import smtplib
    from app.core.config import settings as _s
    from app.services.email import tpl_boas_vindas_tutor
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    steps = []
    error = None
    try:
        steps.append("Conectando a {}:{}...".format(_s.SMTP_HOST, _s.SMTP_PORT))
        srv = smtplib.SMTP(_s.SMTP_HOST, _s.SMTP_PORT, timeout=8)
        steps.append("Conexão OK")
        srv.ehlo()
        steps.append("EHLO OK")
        srv.starttls()
        steps.append("STARTTLS OK")
        srv.ehlo()
        srv.login(_s.SMTP_USER, _s.SMTP_PASSWORD)
        steps.append("Login OK")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Teste SMTP — VetLândia"
        msg["From"] = f"VetLândia <{_s.SMTP_USER}>"
        msg["To"] = to
        msg.attach(MIMEText(tpl_boas_vindas_tutor("Admin"), "html", "utf-8"))
        srv.sendmail(_s.SMTP_USER, [to], msg.as_string())
        srv.quit()
        steps.append(f"E-mail enviado para {to} ✅")
    except Exception as exc:
        error = str(exc)

    steps_html = "".join(f"<li>{s}</li>" for s in steps)
    result = (
        f"<p style='color:red;font-weight:700'>❌ Falhou em: <code>{error}</code></p>"
        if error else
        f"<p style='color:green;font-weight:700'>✅ Sucesso!</p>"
    )
    return f"""<html><body style='font-family:sans-serif;padding:32px;max-width:600px'>
    <h2>Resultado do teste SMTP</h2>
    <ol>{steps_html}</ol>
    {result}
    <p><a href='/admin/test-email'>← Tentar novamente</a> &nbsp; <a href='/admin'>← Admin</a></p>
    </body></html>"""

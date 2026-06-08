from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.assets import ASSET_VERSION
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.case import ClinicalCase
from app.models.clinic import Clinic
from app.models.review import Review, RevieweeType
from app.models.user import User
from app.models.veterinarian import Veterinarian

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["asset_v"] = ASSET_VERSION


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    # Buscar apenas veterinários aprovados com ranking
    vet_ratings = (
        db.query(
            Veterinarian,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .filter(Veterinarian.is_approved == True)
        .outerjoin(
            Review,
            (Review.reviewee_id == Veterinarian.id)
            & (Review.reviewee_type == RevieweeType.VETERINARIAN),
        )
        .group_by(Veterinarian.id)
        .order_by(func.coalesce(func.avg(Review.rating), 0).desc(), Veterinarian.created_at.desc())
        .limit(6)
        .all()
    )

    veterinarians = []
    for vet, avg_rating, review_count in vet_ratings:
        vet.avg_rating = round(avg_rating, 1) if avg_rating else 0
        vet.review_count = review_count
        veterinarians.append(vet)

    # Buscar apenas clínicas aprovadas com ranking
    clinic_ratings = (
        db.query(
            Clinic,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .filter(Clinic.is_approved == True)
        .outerjoin(
            Review,
            (Review.reviewee_id == Clinic.id) & (Review.reviewee_type == RevieweeType.CLINIC),
        )
        .group_by(Clinic.id)
        .order_by(func.coalesce(func.avg(Review.rating), 0).desc(), Clinic.created_at.desc())
        .limit(6)
        .all()
    )

    clinics = []
    for clinic, avg_rating, review_count in clinic_ratings:
        clinic.avg_rating = round(avg_rating, 1) if avg_rating else 0
        clinic.review_count = review_count
        clinics.append(clinic)

    # Buscar casos clínicos recentes (sem filter, já que não tem is_approved ainda)
    recent_cases = (
        db.query(ClinicalCase)
        .options(joinedload(ClinicalCase.author))
        .order_by(ClinicalCase.created_at.desc())
        .limit(3)
        .all()
    )

    # Contagens reais para estatísticas do hero
    vet_count = db.query(Veterinarian).filter(Veterinarian.is_approved == True).count()
    clinic_count = db.query(Clinic).filter(Clinic.is_approved == True).count()
    review_count = db.query(Review).count()

    return templates.TemplateResponse(
        "home-redesign.html",
        {
            "request": request,
            "current_user": current_user,
            "veterinarians": veterinarians,
            "clinics": clinics,
            "recent_cases": recent_cases,
            "vet_count": vet_count,
            "clinic_count": clinic_count,
            "review_count": review_count,
        },
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/")
    return templates.TemplateResponse("auth/login.html", {"request": request, "current_user": None})


@router.get("/cadastro", response_class=HTMLResponse)
def cadastro_page(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/")
    return templates.TemplateResponse("auth/cadastro.html", {"request": request, "current_user": None})


@router.get("/buscar/veterinarios", response_class=HTMLResponse)
def buscar_veterinarios(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    query: str = None,
    especialidade: str = None,
    cidade: str = None,
    estado: str = None,
):
    q = db.query(
        Veterinarian,
        func.avg(Review.rating).label("avg_rating"),
        func.count(Review.id).label("review_count"),
    ).filter(
        Veterinarian.is_approved == True
    ).outerjoin(
        Review,
        (Review.reviewee_id == Veterinarian.id)
        & (Review.reviewee_type == RevieweeType.VETERINARIAN),
    )

    if query:
        q = q.filter(
            (Veterinarian.full_name.ilike(f"%{query}%"))
            | (Veterinarian.crmv.ilike(f"%{query}%"))
        )

    if especialidade:
        q = q.filter(Veterinarian.specialty.ilike(f"%{especialidade}%"))

    if cidade:
        q = q.filter(Veterinarian.city.ilike(f"%{cidade}%"))

    if estado:
        q = q.filter(Veterinarian.state == estado.upper())

    results = (
        q.group_by(Veterinarian.id)
        .order_by(func.coalesce(func.avg(Review.rating), 0).desc())
        .all()
    )

    veterinarians = []
    for vet, avg_rating, review_count in results:
        vet.avg_rating = round(avg_rating, 1) if avg_rating else 0
        vet.review_count = review_count
        veterinarians.append(vet)

    return templates.TemplateResponse(
        "veterinarian/search.html",
        {
            "request": request,
            "current_user": current_user,
            "veterinarians": veterinarians,
            "query": query,
            "especialidade": especialidade,
        },
    )


@router.get("/buscar/clinicas", response_class=HTMLResponse)
def buscar_clinicas(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    query: str = None,
    cidade: str = None,
    estado: str = None,
):
    q = db.query(
        Clinic,
        func.avg(Review.rating).label("avg_rating"),
        func.count(Review.id).label("review_count"),
    ).filter(
        Clinic.is_approved == True
    ).outerjoin(
        Review, (Review.reviewee_id == Clinic.id) & (Review.reviewee_type == RevieweeType.CLINIC)
    )

    if query:
        q = q.filter(Clinic.name.ilike(f"%{query}%"))

    if cidade:
        q = q.filter(Clinic.city.ilike(f"%{cidade}%"))

    if estado:
        q = q.filter(Clinic.state == estado.upper())

    results = (
        q.group_by(Clinic.id)
        .order_by(func.coalesce(func.avg(Review.rating), 0).desc())
        .all()
    )

    clinics = []
    for clinic, avg_rating, review_count in results:
        clinic.avg_rating = round(avg_rating, 1) if avg_rating else 0
        clinic.review_count = review_count
        clinics.append(clinic)

    return templates.TemplateResponse(
        "clinic/search.html",
        {"request": request, "current_user": current_user, "clinics": clinics, "query": query},
    )


@router.get("/veterinario/{slug}", response_class=HTMLResponse)
def perfil_veterinario(request: Request, slug: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    vet = db.query(Veterinarian).filter(Veterinarian.slug == slug).first()

    if not vet:
        return RedirectResponse("/buscar/veterinarios")

    # Calcular rating
    rating_data = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(
            Review.reviewee_id == vet.id, Review.reviewee_type == RevieweeType.VETERINARIAN
        )
        .first()
    )

    vet.avg_rating = round(rating_data[0], 1) if rating_data[0] else 0
    vet.review_count = rating_data[1]

    # Buscar avaliações
    reviews = (
        db.query(Review)
        .filter(
            Review.reviewee_id == vet.id, Review.reviewee_type == RevieweeType.VETERINARIAN
        )
        .order_by(Review.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "veterinarian/profile.html",
        {"request": request, "current_user": current_user, "veterinarian": vet, "reviews": reviews},
    )


@router.get("/clinica/{slug}", response_class=HTMLResponse)
def perfil_clinica(request: Request, slug: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    clinic = db.query(Clinic).filter(Clinic.slug == slug).first()

    if not clinic:
        return RedirectResponse("/buscar/clinicas")

    # Calcular rating
    rating_data = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.reviewee_id == clinic.id, Review.reviewee_type == RevieweeType.CLINIC)
        .first()
    )

    clinic.avg_rating = round(rating_data[0], 1) if rating_data[0] else 0
    clinic.review_count = rating_data[1]

    # Buscar avaliações
    reviews = (
        db.query(Review)
        .filter(Review.reviewee_id == clinic.id, Review.reviewee_type == RevieweeType.CLINIC)
        .order_by(Review.created_at.desc())
        .all()
    )

    # Buscar veterinários da clínica
    veterinarians = (
        db.query(Veterinarian).filter(Veterinarian.clinic_id == clinic.id).all()
    )

    return templates.TemplateResponse(
        "clinic/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "clinic": clinic,
            "reviews": reviews,
            "veterinarians": veterinarians,
        },
    )


@router.get("/sobre", response_class=HTMLResponse)
def sobre(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    return templates.TemplateResponse("pages/sobre.html", {"request": request, "current_user": current_user})


@router.get("/contato", response_class=HTMLResponse)
def contato(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    return templates.TemplateResponse("pages/contato.html", {"request": request, "current_user": current_user})


@router.get("/termos", response_class=HTMLResponse)
def termos(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    return templates.TemplateResponse("pages/termos.html", {"request": request, "current_user": current_user})


@router.get("/privacidade", response_class=HTMLResponse)
def privacidade(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    return templates.TemplateResponse("pages/privacidade.html", {"request": request, "current_user": current_user})


@router.get("/aguardando-aprovacao", response_class=HTMLResponse)
def aguardando_aprovacao(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    return templates.TemplateResponse("auth/aguardando.html", {"request": request, "current_user": current_user})


@router.get("/minha-conta", response_class=HTMLResponse)
def minha_conta(request: Request, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse("/login")
    profile = None
    if current_user.user_type.value == "tutor":
        from app.models.tutor import Tutor
        profile = db.query(Tutor).filter(Tutor.user_id == current_user.id).first()
    elif current_user.user_type.value == "veterinarian":
        profile = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
    elif current_user.user_type.value == "clinic":
        profile = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
    return templates.TemplateResponse(
        "auth/minha-conta.html",
        {"request": request, "current_user": current_user, "profile": profile},
    )


@router.get("/casos-clinicos", response_class=HTMLResponse)
def casos_clinicos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    especialidade: str = None,
):
    q = db.query(ClinicalCase).options(joinedload(ClinicalCase.author))

    if especialidade:
        q = q.filter(ClinicalCase.specialty.ilike(f"%{especialidade}%"))

    cases = q.order_by(ClinicalCase.created_at.desc()).all()

    return templates.TemplateResponse(
        "case/list.html",
        {"request": request, "current_user": current_user, "cases": cases, "especialidade": especialidade},
    )


@router.get("/casos-clinicos/criar", response_class=HTMLResponse)
def criar_caso_clinico(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    return templates.TemplateResponse("case/create.html", {"request": request, "current_user": current_user})


@router.get("/casos-clinicos/{case_id}", response_class=HTMLResponse)
def caso_clinico_detalhe(request: Request, case_id: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    from app.models.case import CaseComment

    case = (
        db.query(ClinicalCase)
        .options(joinedload(ClinicalCase.author))
        .filter(ClinicalCase.id == case_id)
        .first()
    )

    if not case:
        return RedirectResponse("/casos-clinicos")

    comments = (
        db.query(CaseComment)
        .options(joinedload(CaseComment.author))
        .filter(CaseComment.case_id == case_id)
        .order_by(CaseComment.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "case/detail.html",
        {"request": request, "current_user": current_user, "case": case, "comments": comments},
    )

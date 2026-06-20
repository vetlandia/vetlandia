import json
import unicodedata
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.assets import ASSET_VERSION
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.case import CaseComment, CaseStatus, ClinicalCase
from app.models.clinic import Clinic
from app.models.entitlement import clinic_has_product
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.review import Review, RevieweeType, ReviewStatus
from app.models.user import User
from app.models.veterinarian import Veterinarian

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["asset_v"] = ASSET_VERSION

# ── Busca inteligente ──────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Remove acentos e coloca em minúsculas para comparação."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    ).lower().strip()

_24H_TERMS = {'24h', '24 h', 'plantao', 'plantão', 'emergencia', 'emergência',
              'urgencia', 'urgência', 'urgente', 'noturno', 'noite'}

_SPECIALTY_MAP = {
    'geral': 'geral', 'clinico': 'geral', 'clinica': 'geral',
    'derma': 'dermatologia', 'pele': 'dermatologia',
    'cirurgi': 'cirurgia', 'operar': 'cirurgia', 'operacao': 'cirurgia',
    'ortop': 'ortopedia', 'osso': 'ortopedia', 'fratura': 'ortopedia',
    'cardio': 'cardiologia', 'coracao': 'cardiologia', 'coração': 'cardiologia',
    'oftalmo': 'oftalmologia', 'olho': 'oftalmologia', 'visao': 'oftalmologia',
    'emergencia': 'emergência', 'urgencia': 'emergência',
    'oncolog': 'oncologia', 'cancer': 'oncologia', 'tumor': 'oncologia',
    'nutri': 'nutrição', 'dieta': 'nutrição',
    'fisio': 'fisioterapia', 'reabili': 'fisioterapia',
    'compor': 'comportamento', 'comportament': 'comportamento',
    'acupun': 'acupuntura',
    'neuro': 'neurologia',
    'reprod': 'reprodução', 'reproducao': 'reprodução',
    'exo': 'animais exóticos', 'exoti': 'animais exóticos', 'silvestr': 'animais silvestres',
    'gato': 'felinos', 'felino': 'felinos',
    'cao': 'cães', 'cachorro': 'cães', 'caes': 'cães',
    'coelho': 'pequenos animais', 'hamster': 'pequenos animais',
}

def _is_24h_query(term: str) -> bool:
    n = _norm(term)
    return any(t in n or n in t for t in {_norm(x) for x in _24H_TERMS})

def _specialty_from_query(term: str):
    n = _norm(term)
    for alias, real in _SPECIALTY_MAP.items():
        if alias in n or n in alias:
            return real
    return None


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
            & (Review.reviewee_type == RevieweeType.VETERINARIAN)
            & (Review.status == ReviewStatus.APPROVED),
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
            (Review.reviewee_id == Clinic.id)
            & (Review.reviewee_type == RevieweeType.CLINIC)
            & (Review.status == ReviewStatus.APPROVED),
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

    # Casos recentes aprovados para a home (só exibido para vet/admin no template)
    recent_cases = (
        db.query(ClinicalCase)
        .options(joinedload(ClinicalCase.author))
        .filter(ClinicalCase.status == CaseStatus.APPROVED)
        .order_by(ClinicalCase.created_at.desc())
        .limit(3)
        .all()
    )

    # Três COUNTs em uma única ida ao banco
    from sqlalchemy import text as _text
    _counts = db.execute(_text(
        "SELECT "
        "(SELECT COUNT(*) FROM veterinarians WHERE is_approved = true) AS vc,"
        "(SELECT COUNT(*) FROM clinics WHERE is_approved = true) AS cc,"
        "(SELECT COUNT(*) FROM reviews) AS rc"
    )).one()
    vet_count, clinic_count, review_count = _counts.vc, _counts.cc, _counts.rc

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


@router.get("/buscar", response_class=HTMLResponse)
def buscar(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    tipo: str = "ambos",
    query: str = None,
    especialidade: str = None,
    cidade: str = None,
    estado: str = None,
    somente_24h: str = None,
    aplica_vacinas: str = None,
):
    veterinarians = []
    clinics = []

    if tipo in ("veterinario", "ambos"):
        qv = db.query(
            Veterinarian,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        ).filter(
            Veterinarian.is_approved == True
        ).outerjoin(
            Review,
            (Review.reviewee_id == Veterinarian.id)
            & (Review.reviewee_type == RevieweeType.VETERINARIAN)
            & (Review.status == ReviewStatus.APPROVED),
        )

        if query:
            if _is_24h_query(query):
                qv = qv.filter(Veterinarian.is_24h == True)
            else:
                sp = _specialty_from_query(query)
                like = f"%{query}%"
                if sp:
                    qv = qv.filter(
                        Veterinarian.specialty.ilike(f"%{sp}%")
                        | Veterinarian.full_name.ilike(like)
                        | Veterinarian.bio.ilike(like)
                    )
                else:
                    qv = qv.filter(
                        Veterinarian.full_name.ilike(like)
                        | Veterinarian.specialty.ilike(like)
                        | Veterinarian.bio.ilike(like)
                        | Veterinarian.city.ilike(like)
                        | Veterinarian.crmv.ilike(like)
                        | Veterinarian.animal_species.ilike(like)
                    )

        if especialidade:
            qv = qv.filter(Veterinarian.specialty.ilike(f"%{especialidade}%"))
        if cidade:
            if "/" in cidade:
                partes = cidade.split("/", 1)
                qv = qv.filter(Veterinarian.city.ilike(f"%{partes[0].strip()}%"))
                if partes[1].strip():
                    qv = qv.filter(Veterinarian.state == partes[1].strip().upper())
            else:
                qv = qv.filter(Veterinarian.city.ilike(f"%{cidade}%"))
        if estado:
            qv = qv.filter(Veterinarian.state == estado.upper())
        if somente_24h in ("1", "on"):
            qv = qv.filter(Veterinarian.is_24h == True)
        if aplica_vacinas in ("1", "on"):
            qv = qv.filter(Veterinarian.aplica_vacinas == True)

        for vet, avg_rating, review_count in (
            qv.group_by(Veterinarian.id)
            .order_by(func.coalesce(func.avg(Review.rating), 0).desc())
            .all()
        ):
            vet.avg_rating = round(avg_rating, 1) if avg_rating else 0
            vet.review_count = review_count
            veterinarians.append(vet)

    if tipo in ("clinica", "ambos"):
        qc = db.query(
            Clinic,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        ).filter(
            Clinic.is_approved == True
        ).outerjoin(
            Review,
            (Review.reviewee_id == Clinic.id)
            & (Review.reviewee_type == RevieweeType.CLINIC)
            & (Review.status == ReviewStatus.APPROVED),
        )

        if query:
            if _is_24h_query(query):
                qc = qc.filter(Clinic.is_24h == True)
            else:
                sp = _specialty_from_query(query)
                like = f"%{query}%"
                if sp:
                    qc = qc.filter(
                        Clinic.specialties.ilike(f"%{sp}%")
                        | Clinic.name.ilike(like)
                        | Clinic.description.ilike(like)
                    )
                else:
                    qc = qc.filter(
                        Clinic.name.ilike(like)
                        | Clinic.razao_social.ilike(like)
                        | Clinic.specialties.ilike(like)
                        | Clinic.description.ilike(like)
                        | Clinic.city.ilike(like)
                        | Clinic.animal_species.ilike(like)
                    )

        if cidade:
            if "/" in cidade:
                partes = cidade.split("/", 1)
                qc = qc.filter(Clinic.city.ilike(f"%{partes[0].strip()}%"))
                if partes[1].strip():
                    qc = qc.filter(Clinic.state == partes[1].strip().upper())
            else:
                qc = qc.filter(Clinic.city.ilike(f"%{cidade}%"))
        if estado:
            qc = qc.filter(Clinic.state == estado.upper())
        if somente_24h in ("1", "on"):
            qc = qc.filter(Clinic.is_24h == True)
        if aplica_vacinas in ("1", "on"):
            qc = qc.filter(Clinic.aplica_vacinas == True)

        for clinic, avg_rating, review_count in (
            qc.group_by(Clinic.id)
            .order_by(func.coalesce(func.avg(Review.rating), 0).desc())
            .all()
        ):
            clinic.avg_rating = round(avg_rating, 1) if avg_rating else 0
            clinic.review_count = review_count
            clinics.append(clinic)

    especialidades_disponiveis = sorted([
        r[0] for r in
        db.query(Veterinarian.specialty)
        .filter(Veterinarian.is_approved == True, Veterinarian.specialty != None, Veterinarian.specialty != "")
        .distinct().all()
    ])
    cidades_vets = [
        f"{r[0]}/{r[1]}" for r in
        db.query(Veterinarian.city, Veterinarian.state)
        .filter(Veterinarian.is_approved == True, Veterinarian.city != None, Veterinarian.city != "")
        .distinct().all()
    ]
    cidades_clinicas = [
        f"{r[0]}/{r[1]}" if r[1] else r[0] for r in
        db.query(Clinic.city, Clinic.state)
        .filter(Clinic.is_approved == True, Clinic.city != None, Clinic.city != "")
        .distinct().all()
    ]
    cidades_disponiveis = sorted(set(cidades_vets + cidades_clinicas))

    return templates.TemplateResponse(
        "busca.html",
        {
            "request": request,
            "current_user": current_user,
            "veterinarians": veterinarians,
            "clinics": clinics,
            "tipo": tipo,
            "query": query,
            "especialidade": especialidade,
            "cidade": cidade,
            "estado": estado,
            "somente_24h": somente_24h,
            "aplica_vacinas": aplica_vacinas,
            "especialidades_disponiveis": especialidades_disponiveis,
            "cidades_disponiveis": cidades_disponiveis,
        },
    )


@router.get("/buscar/veterinarios", response_class=HTMLResponse)
def buscar_veterinarios(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    query: str = None,
    especialidade: str = None,
    cidade: str = None,
    estado: str = None,
    somente_24h: str = None,
    aplica_vacinas: str = None,
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
        & (Review.reviewee_type == RevieweeType.VETERINARIAN)
        & (Review.status == ReviewStatus.APPROVED),
    )

    if query:
        if _is_24h_query(query):
            q = q.filter(Veterinarian.is_24h == True)
        else:
            sp = _specialty_from_query(query)
            like = f"%{query}%"
            if sp:
                q = q.filter(
                    Veterinarian.specialty.ilike(f"%{sp}%")
                    | Veterinarian.full_name.ilike(like)
                    | Veterinarian.bio.ilike(like)
                )
            else:
                q = q.filter(
                    Veterinarian.full_name.ilike(like)
                    | Veterinarian.specialty.ilike(like)
                    | Veterinarian.bio.ilike(like)
                    | Veterinarian.city.ilike(like)
                    | Veterinarian.crmv.ilike(like)
                    | Veterinarian.animal_species.ilike(like)
                )

    if especialidade:
        q = q.filter(Veterinarian.specialty.ilike(f"%{especialidade}%"))

    if cidade:
        if "/" in cidade:
            partes = cidade.split("/", 1)
            q = q.filter(Veterinarian.city.ilike(f"%{partes[0].strip()}%"))
            if partes[1].strip():
                q = q.filter(Veterinarian.state == partes[1].strip().upper())
        else:
            q = q.filter(Veterinarian.city.ilike(f"%{cidade}%"))

    if estado:
        q = q.filter(Veterinarian.state == estado.upper())
    if somente_24h in ("1", "on"):
        q = q.filter(Veterinarian.is_24h == True)
    if aplica_vacinas in ("1", "on"):
        q = q.filter(Veterinarian.aplica_vacinas == True)

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

    # Combos dinâmicos: apenas especialidades e cidades com vets aprovados
    especialidades_disponiveis = sorted([
        r[0] for r in
        db.query(Veterinarian.specialty)
        .filter(Veterinarian.is_approved == True, Veterinarian.specialty != None, Veterinarian.specialty != "")
        .distinct().all()
    ])
    cidades_disponiveis = sorted([
        f"{r[0]}/{r[1]}" for r in
        db.query(Veterinarian.city, Veterinarian.state)
        .filter(Veterinarian.is_approved == True, Veterinarian.city != None, Veterinarian.city != "")
        .distinct().all()
    ])

    return templates.TemplateResponse(
        "veterinarian/search.html",
        {
            "request": request,
            "current_user": current_user,
            "veterinarians": veterinarians,
            "query": query,
            "especialidade": especialidade,
            "cidade": cidade,
            "somente_24h": somente_24h,
            "aplica_vacinas": aplica_vacinas,
            "especialidades_disponiveis": especialidades_disponiveis,
            "cidades_disponiveis": cidades_disponiveis,
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
    somente_24h: str = None,
    aplica_vacinas: str = None,
):
    q = db.query(
        Clinic,
        func.avg(Review.rating).label("avg_rating"),
        func.count(Review.id).label("review_count"),
    ).filter(
        Clinic.is_approved == True
    ).outerjoin(
        Review,
        (Review.reviewee_id == Clinic.id)
        & (Review.reviewee_type == RevieweeType.CLINIC)
        & (Review.status == ReviewStatus.APPROVED),
    )

    if query:
        if _is_24h_query(query):
            q = q.filter(Clinic.is_24h == True)
        else:
            sp = _specialty_from_query(query)
            like = f"%{query}%"
            if sp:
                q = q.filter(
                    Clinic.specialties.ilike(f"%{sp}%")
                    | Clinic.name.ilike(like)
                    | Clinic.description.ilike(like)
                )
            else:
                q = q.filter(
                    Clinic.name.ilike(like)
                    | Clinic.razao_social.ilike(like)
                    | Clinic.specialties.ilike(like)
                    | Clinic.description.ilike(like)
                    | Clinic.city.ilike(like)
                    | Clinic.animal_species.ilike(like)
                )

    if cidade:
        if "/" in cidade:
            partes = cidade.split("/", 1)
            q = q.filter(Clinic.city.ilike(f"%{partes[0].strip()}%"))
            if partes[1].strip():
                q = q.filter(Clinic.state == partes[1].strip().upper())
        else:
            q = q.filter(Clinic.city.ilike(f"%{cidade}%"))

    if estado:
        q = q.filter(Clinic.state == estado.upper())
    if somente_24h in ("1", "on"):
        q = q.filter(Clinic.is_24h == True)
    if aplica_vacinas in ("1", "on"):
        q = q.filter(Clinic.aplica_vacinas == True)

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

    cidades_disponiveis = sorted([
        f"{r[0]}/{r[1]}" if r[1] else r[0] for r in
        db.query(Clinic.city, Clinic.state)
        .filter(Clinic.is_approved == True, Clinic.city != None, Clinic.city != "")
        .distinct().all()
    ])

    return templates.TemplateResponse(
        "clinic/search.html",
        {
            "request": request,
            "current_user": current_user,
            "clinics": clinics,
            "query": query,
            "cidade": cidade,
            "somente_24h": somente_24h,
            "aplica_vacinas": aplica_vacinas,
            "cidades_disponiveis": cidades_disponiveis,
        },
    )


@router.get("/veterinario/{slug}", response_class=HTMLResponse)
def perfil_veterinario(request: Request, slug: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    vet = db.query(Veterinarian).filter(Veterinarian.slug == slug).first()

    # Admin pode pré-visualizar perfis ainda não aprovados (Módulo 9)
    is_admin = bool(current_user and current_user.user_type.value == "admin")
    if not vet or (not vet.is_approved and not is_admin):
        return templates.TemplateResponse("pages/404.html", {"request": request, "current_user": current_user}, status_code=404)

    # Calcular rating (apenas aprovadas)
    rating_data = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(
            Review.reviewee_id == vet.id,
            Review.reviewee_type == RevieweeType.VETERINARIAN,
            Review.status == ReviewStatus.APPROVED,
        )
        .first()
    )

    vet.avg_rating = round(rating_data[0], 1) if rating_data[0] else 0
    vet.review_count = rating_data[1]

    # Buscar avaliações aprovadas com autor
    from sqlalchemy.orm import joinedload as jl
    reviews = (
        db.query(Review)
        .options(jl(Review.author))
        .filter(
            Review.reviewee_id == vet.id,
            Review.reviewee_type == RevieweeType.VETERINARIAN,
            Review.status == ReviewStatus.APPROVED,
        )
        .order_by(Review.created_at.desc())
        .all()
    )

    # Avaliação do tutor logado (qualquer status)
    tutor_review = None
    if current_user and current_user.user_type.value == "tutor":
        tutor_review = (
            db.query(Review)
            .filter(
                Review.author_id == current_user.id,
                Review.reviewee_id == vet.id,
                Review.reviewee_type == RevieweeType.VETERINARIAN,
            )
            .first()
        )

    # Casos clínicos aprovados do veterinário
    vet_cases = (
        db.query(ClinicalCase)
        .filter(
            ClinicalCase.author_id == vet.id,
            ClinicalCase.status == CaseStatus.APPROVED,
        )
        .order_by(ClinicalCase.created_at.desc())
        .limit(6)
        .all()
    )

    try:
        vet_species = json.loads(vet.animal_species) if vet.animal_species else []
    except (ValueError, TypeError):
        vet_species = []

    try:
        vet_specialties = json.loads(vet.specialties) if vet.specialties else []
    except (ValueError, TypeError):
        vet_specialties = []

    # Vínculos atuais (público): clínicas aprovadas onde o vet atua hoje
    vet_current_clinics = [
        link.clinic
        for link in vet.clinic_links
        if link.is_current and link.clinic and link.clinic.is_approved
    ]

    # Recomendações aprovadas (com nome do autor resolvido)
    approved_recs = (
        db.query(Recommendation)
        .filter(
            Recommendation.target_vet_id == vet.id,
            Recommendation.status == RecommendationStatus.APPROVED,
        )
        .order_by(Recommendation.created_at.desc())
        .all()
    )
    vet_recommendations = []
    for r in approved_recs:
        if r.author_type.value == "veterinarian":
            a = db.query(Veterinarian).filter(Veterinarian.id == r.author_id).first()
            vet_recommendations.append({
                "author_name": a.full_name if a else "Veterinário(a)",
                "author_label": "Veterinário(a)",
                "content": r.content,
            })
        else:
            a = db.query(Clinic).filter(Clinic.id == r.author_id).first()
            vet_recommendations.append({
                "author_name": a.name if a else "Clínica",
                "author_label": "Clínica",
                "content": r.content,
            })

    # Quem pode recomendar: vet (≠ o próprio) ou clínica logados
    can_recommend = False
    already_recommended = False
    if current_user and current_user.user_type.value in ("veterinarian", "clinic"):
        if current_user.user_type.value == "veterinarian":
            author = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
            atype = "veterinarian"
        else:
            author = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
            atype = "clinic"
        if author and not (atype == "veterinarian" and author.id == vet.id):
            can_recommend = True
            already_recommended = (
                db.query(Recommendation)
                .filter(
                    Recommendation.author_type == atype,
                    Recommendation.author_id == author.id,
                    Recommendation.target_vet_id == vet.id,
                )
                .first()
                is not None
            )

    # Dono do perfil logado (pode excluir avaliações do próprio perfil)
    is_owner = bool(
        current_user
        and current_user.user_type.value == "veterinarian"
        and db.query(Veterinarian.id)
        .filter(Veterinarian.user_id == current_user.id, Veterinarian.id == vet.id)
        .first()
    )

    # ── Módulo 6: camada de visibilidade de recrutamento ──
    # Só admin ou clínica com acesso liberado veem disponibilidades e histórico.
    can_see_recruitment = False
    if current_user:
        if current_user.user_type.value == "admin":
            can_see_recruitment = True
        elif current_user.user_type.value == "clinic":
            viewer_clinic = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
            # Módulo 8: a fonte de verdade é o entitlement 'recrutamento'
            can_see_recruitment = bool(viewer_clinic and clinic_has_product(viewer_clinic, "recrutamento"))

    vet_availability = None
    vet_history = []
    if can_see_recruitment:
        vet_availability = {
            "plantao": vet.disp_plantao,
            "volante": vet.disp_volante,
            "oportunidades": vet.disp_oportunidades,
            "parcerias": vet.disp_parcerias,
        }
        # Histórico completo (atuais + encerrados) com dados da clínica
        for link in vet.clinic_links:
            if link.clinic:
                vet_history.append({
                    "clinic_name": link.clinic.name,
                    "clinic_slug": link.clinic.slug,
                    "role": link.role,
                    "start_year": link.start_year,
                    "end_year": link.end_year,
                    "is_current": link.is_current,
                })

    return templates.TemplateResponse(
        "veterinarian/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "veterinarian": vet,
            "reviews": reviews,
            "tutor_review": tutor_review,
            "reviewee_type": "veterinarian",
            "reviewee_id": str(vet.id),
            "vet_cases": vet_cases,
            "vet_species": vet_species,
            "vet_specialties": vet_specialties,
            "vet_educations": vet.educations,
            "vet_current_clinics": vet_current_clinics,
            "vet_contents": vet.contents,
            "vet_recommendations": vet_recommendations,
            "can_recommend": can_recommend,
            "already_recommended": already_recommended,
            "can_see_recruitment": can_see_recruitment,
            "vet_availability": vet_availability,
            "vet_history": vet_history,
            "admin_preview": is_admin and not vet.is_approved,
            "is_owner": is_owner,
        },
    )


@router.get("/clinica/{slug}", response_class=HTMLResponse)
def perfil_clinica(request: Request, slug: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    clinic = db.query(Clinic).filter(Clinic.slug == slug).first()

    # Admin pode pré-visualizar perfis ainda não aprovados (Módulo 9)
    is_admin = bool(current_user and current_user.user_type.value == "admin")
    if not clinic or (not clinic.is_approved and not is_admin):
        return templates.TemplateResponse("pages/404.html", {"request": request, "current_user": current_user}, status_code=404)

    # Calcular rating (apenas aprovadas)
    rating_data = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(
            Review.reviewee_id == clinic.id,
            Review.reviewee_type == RevieweeType.CLINIC,
            Review.status == ReviewStatus.APPROVED,
        )
        .first()
    )

    clinic.avg_rating = round(rating_data[0], 1) if rating_data[0] else 0
    clinic.review_count = rating_data[1]

    # Buscar avaliações aprovadas com autor
    from sqlalchemy.orm import joinedload as jl
    reviews = (
        db.query(Review)
        .options(jl(Review.author))
        .filter(
            Review.reviewee_id == clinic.id,
            Review.reviewee_type == RevieweeType.CLINIC,
            Review.status == ReviewStatus.APPROVED,
        )
        .order_by(Review.created_at.desc())
        .all()
    )

    # Avaliação do tutor logado (qualquer status)
    tutor_review = None
    if current_user and current_user.user_type.value == "tutor":
        tutor_review = (
            db.query(Review)
            .filter(
                Review.author_id == current_user.id,
                Review.reviewee_id == clinic.id,
                Review.reviewee_type == RevieweeType.CLINIC,
            )
            .first()
        )

    # Corpo clínico (grafo): clínica legada (clinic_id) + vínculos atuais,
    # apenas vets aprovados, sem duplicar.
    veterinarians = []
    _seen = set()
    for v in db.query(Veterinarian).filter(Veterinarian.clinic_id == clinic.id).all():
        if v.id not in _seen:
            veterinarians.append(v)
            _seen.add(v.id)
    for link in clinic.vet_links:
        v = link.veterinarian
        if link.is_current and v and v.is_approved and v.id not in _seen:
            veterinarians.append(v)
            _seen.add(v.id)

    def _parse_json_list(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return [v.strip() for v in val.split(",") if v.strip()]

    # Especialidades da equipe (derivadas dos vets do corpo clínico)
    team_specialties = set()
    for v in veterinarians:
        if v.specialty:
            team_specialties.add(v.specialty)
        try:
            for sp in (json.loads(v.specialties) if v.specialties else []):
                team_specialties.add(sp)
        except (ValueError, TypeError):
            pass

    return templates.TemplateResponse(
        "clinic/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "clinic": clinic,
            "reviews": reviews,
            "veterinarians": veterinarians,
            "team_specialties": sorted(team_specialties),
            "clinic_specialties": _parse_json_list(clinic.specialties),
            "clinic_species": _parse_json_list(clinic.animal_species),
            "clinic_convenios": _parse_json_list(clinic.convenios),
            "tutor_review": tutor_review,
            "reviewee_type": "clinic",
            "reviewee_id": str(clinic.id),
            "admin_preview": is_admin and not clinic.is_approved,
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
    vet_specialties = []
    vet_educations = []
    vet_clinic_links = []
    vet_contents = []
    all_clinics = []
    if current_user.user_type.value == "tutor":
        from app.models.tutor import Tutor
        profile = db.query(Tutor).filter(Tutor.user_id == current_user.id).first()
    elif current_user.user_type.value == "veterinarian":
        profile = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
        if profile:
            try:
                vet_specialties = json.loads(profile.specialties) if profile.specialties else []
            except (ValueError, TypeError):
                vet_specialties = []
            vet_educations = profile.educations
            vet_clinic_links = profile.clinic_links
            vet_contents = profile.contents
            all_clinics = (
                db.query(Clinic).filter(Clinic.is_approved == True).order_by(Clinic.name).all()
            )
    elif current_user.user_type.value == "clinic":
        profile = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
    return templates.TemplateResponse(
        "auth/minha-conta.html",
        {
            "request": request,
            "current_user": current_user,
            "profile": profile,
            "vet_specialties": vet_specialties,
            "vet_educations": vet_educations,
            "vet_clinic_links": vet_clinic_links,
            "vet_contents": vet_contents,
            "all_clinics": all_clinics,
        },
    )


@router.get("/casos-clinicos", response_class=HTMLResponse)
def casos_clinicos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    especialidade: str = None,
):
    q = db.query(ClinicalCase).options(joinedload(ClinicalCase.author)).filter(
        ClinicalCase.status == CaseStatus.APPROVED
    )

    if especialidade:
        q = q.filter(ClinicalCase.specialty.ilike(f"%{especialidade}%"))

    cases = q.order_by(ClinicalCase.created_at.desc()).all()

    return templates.TemplateResponse(
        "case/list.html",
        {"request": request, "current_user": current_user, "cases": cases, "especialidade": especialidade},
    )


@router.get("/casos-clinicos/criar", response_class=HTMLResponse)
def criar_caso_clinico(request: Request, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    vet_profile = None
    if current_user and current_user.user_type.value == "veterinarian":
        vet_profile = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
    return templates.TemplateResponse("case/create.html", {"request": request, "current_user": current_user, "vet_profile": vet_profile})


@router.get("/casos-clinicos/{case_id}", response_class=HTMLResponse)
def caso_clinico_detalhe(request: Request, case_id: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    case = (
        db.query(ClinicalCase)
        .options(joinedload(ClinicalCase.author))
        .filter(ClinicalCase.id == case_id)
        .first()
    )

    is_admin = current_user and current_user.user_type.value == "admin"
    if not case or (case.status != CaseStatus.APPROVED and not is_admin):
        return RedirectResponse("/casos-clinicos")

    comments = (
        db.query(CaseComment)
        .options(joinedload(CaseComment.author))
        .filter(
            CaseComment.case_id == case_id,
            CaseComment.status == CaseStatus.APPROVED,
        )
        .order_by(CaseComment.created_at.desc())
        .all()
    )

    vet_profile = None
    if current_user and current_user.user_type.value == "veterinarian":
        vet_profile = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()

    return templates.TemplateResponse(
        "case/detail.html",
        {"request": request, "current_user": current_user, "case": case, "comments": comments, "vet_profile": vet_profile},
    )

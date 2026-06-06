from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.case import ClinicalCase
from app.models.clinic import Clinic
from app.models.veterinarian import Veterinarian

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    # Buscar veterinários em destaque (máximo 6)
    veterinarians = (
        db.query(Veterinarian)
        .order_by(Veterinarian.created_at.desc())
        .limit(6)
        .all()
    )

    # Buscar clínicas em destaque (máximo 6)
    clinics = (
        db.query(Clinic)
        .order_by(Clinic.created_at.desc())
        .limit(6)
        .all()
    )

    # Buscar casos clínicos recentes (máximo 3)
    recent_cases = (
        db.query(ClinicalCase)
        .options(joinedload(ClinicalCase.author))
        .order_by(ClinicalCase.created_at.desc())
        .limit(3)
        .all()
    )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "veterinarians": veterinarians,
            "clinics": clinics,
            "recent_cases": recent_cases,
        },
    )

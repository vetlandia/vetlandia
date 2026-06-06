from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.clinic import ClinicCreate
from app.schemas.tutor import TutorCreate
from app.schemas.user import Token, UserLogin
from app.schemas.veterinarian import VeterinarianCreate
from app.services import auth as auth_service

router = APIRouter()


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login de usuário (tutor, veterinário ou clínica)"""
    return auth_service.login(db, credentials)


@router.post("/register/tutor", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_tutor(data: TutorCreate, db: Session = Depends(get_db)):
    """Registro de tutor"""
    return auth_service.register_tutor(db, data)


@router.post("/register/veterinarian", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_veterinarian(data: VeterinarianCreate, db: Session = Depends(get_db)):
    """Registro de veterinário"""
    return auth_service.register_veterinarian(db, data)


@router.post("/register/clinic", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_clinic(data: ClinicCreate, db: Session = Depends(get_db)):
    """Registro de clínica"""
    return auth_service.register_clinic(db, data)

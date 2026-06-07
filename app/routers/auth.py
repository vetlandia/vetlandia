from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserType
from app.schemas.clinic import ClinicCreate
from app.schemas.tutor import TutorCreate
from app.schemas.user import Token, UserLogin
from app.schemas.veterinarian import VeterinarianCreate
from app.services import auth as auth_service

router = APIRouter()


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    token = auth_service.login(db, credentials)

    # Descobrir user_type para redirecionar
    user = auth_service.authenticate_user(db, credentials)
    is_admin = user and user.user_type == UserType.ADMIN

    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Railway usa HTTPS, Cloudflare termina SSL
        max_age=60 * 60 * 24 * 30,  # 30 dias
    )
    return {**token.dict(), "is_admin": is_admin}


@router.post("/register/tutor", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_tutor(data: TutorCreate, response: Response, db: Session = Depends(get_db)):
    token = auth_service.register_tutor(db, data)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 30,
    )
    return token


@router.post("/register/veterinarian", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_veterinarian(data: VeterinarianCreate, response: Response, db: Session = Depends(get_db)):
    token = auth_service.register_veterinarian(db, data)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 30,
    )
    return token


@router.post("/register/clinic", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_clinic(data: ClinicCreate, response: Response, db: Session = Depends(get_db)):
    token = auth_service.register_clinic(db, data)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 30,
    )
    return token

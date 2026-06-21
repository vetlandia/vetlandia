import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.schemas.clinic import ClinicCreate
from app.schemas.tutor import TutorCreate
from app.schemas.user import Token, UserLogin
from app.schemas.veterinarian import VeterinarianCreate
from app.services import auth as auth_service
from app.services.email import send_email, tpl_reset_senha

router = APIRouter()

_SITE_URL = "https://vetlandia.com.br"


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    token = auth_service.login(db, credentials)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 30,
    )
    return token


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


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    # Always return 200 to avoid email enumeration
    if not user or not user.is_active:
        return {"ok": True}

    # Invalidate any existing tokens for this user
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    prt = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    db.add(prt)
    db.commit()

    reset_url = f"{_SITE_URL}/redefinir-senha?token={raw_token}"
    send_email(user.email, "Redefinição de senha — VetLândia", tpl_reset_senha(user.display_name, reset_url))
    return {"ok": True}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    prt = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used == False,
    ).first()

    if not prt or prt.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Link inválido ou expirado. Solicite um novo.")

    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="A senha deve ter pelo menos 6 caracteres.")

    user = db.query(User).filter(User.id == prt.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado.")

    user.password_hash = get_password_hash(data.password)
    prt.used = True
    db.commit()
    return {"ok": True}

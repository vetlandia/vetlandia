from datetime import timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.clinic import Clinic
from app.models.tutor import Tutor
from app.models.user import User, UserType
from app.models.veterinarian import Veterinarian
from app.schemas.clinic import ClinicCreate
from app.schemas.tutor import TutorCreate
from app.schemas.user import Token, UserLogin
from app.schemas.veterinarian import VeterinarianCreate
from app.utils.slugify import slugify


def authenticate_user(db: Session, credentials: UserLogin) -> Optional[User]:
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        return None

    if not verify_password(credentials.password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user


def create_token_for_user(user: User) -> Token:
    access_token = create_access_token(
        data={"sub": str(user.id), "user_type": user.user_type.value}
    )
    return Token(access_token=access_token)


def login(db: Session, credentials: UserLogin) -> Token:
    user = authenticate_user(db, credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    return create_token_for_user(user)


def register_tutor(db: Session, data: TutorCreate) -> Token:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        user_type=UserType.TUTOR,
    )
    db.add(user)
    db.flush()

    tutor = Tutor(
        user_id=user.id,
        full_name=data.full_name,
        phone=data.phone,
    )
    db.add(tutor)
    db.commit()
    db.refresh(user)

    return create_token_for_user(user)


def register_veterinarian(db: Session, data: VeterinarianCreate) -> Token:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    existing_crmv = db.query(Veterinarian).filter(Veterinarian.crmv == data.crmv).first()
    if existing_crmv:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CRMV já cadastrado",
        )

    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        user_type=UserType.VETERINARIAN,
    )
    db.add(user)
    db.flush()

    base_slug = slugify(f"{data.full_name} {data.city or ''}")
    slug = base_slug
    counter = 1
    while db.query(Veterinarian).filter(Veterinarian.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    veterinarian = Veterinarian(
        user_id=user.id,
        full_name=data.full_name,
        crmv=data.crmv,
        specialty=data.specialty,
        bio=data.bio,
        phone=data.phone,
        city=data.city,
        state=data.state,
        slug=slug,
        clinic_id=data.clinic_id,
    )
    db.add(veterinarian)
    db.commit()
    db.refresh(user)

    return create_token_for_user(user)


def register_clinic(db: Session, data: ClinicCreate) -> Token:
    existing = db.query(User).filter(User.email == data.email_user).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    user = User(
        email=data.email_user,
        password_hash=get_password_hash(data.password),
        user_type=UserType.CLINIC,
    )
    db.add(user)
    db.flush()

    base_slug = slugify(f"{data.name} {data.city}")
    slug = base_slug
    counter = 1
    while db.query(Clinic).filter(Clinic.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    clinic = Clinic(
        user_id=user.id,
        name=data.name,
        description=data.description,
        address=data.address,
        city=data.city,
        state=data.state,
        zip_code=data.zip_code,
        phone=data.phone,
        email=data.email,
        website=data.website,
        slug=slug,
    )
    db.add(clinic)
    db.commit()
    db.refresh(user)

    return create_token_for_user(user)

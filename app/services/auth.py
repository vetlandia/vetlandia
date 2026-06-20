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


def _is_pending(user: User, db: Session) -> bool:
    if user.user_type == UserType.VETERINARIAN:
        vet = db.query(Veterinarian).filter(Veterinarian.user_id == user.id).first()
        return vet is not None and not vet.is_approved
    if user.user_type == UserType.CLINIC:
        clinic = db.query(Clinic).filter(Clinic.user_id == user.id).first()
        return clinic is not None and not clinic.is_approved
    return False


def create_token_for_user(user: User, db: Session = None, pending: bool = False) -> Token:
    access_token = create_access_token(
        data={"sub": str(user.id), "user_type": user.user_type.value}
    )
    return Token(
        access_token=access_token,
        user_type=user.user_type.value,
        pending=pending,
    )


def login(db: Session, credentials: UserLogin) -> Token:
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma conta encontrada com este e-mail.",
        )
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada. Entre em contato com o suporte.",
        )
    pending = _is_pending(user, db)
    return create_token_for_user(user, pending=pending)


def register_tutor(db: Session, data: TutorCreate) -> Token:
    _existing = db.query(User).filter(User.email == data.email).first()
    if _existing:
        if not _existing.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail está associado a uma conta desativada. Entre em contato com o suporte.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail já possui cadastro. Tente fazer login ou recuperar a senha.")
    if data.cpf and db.query(Tutor).filter(Tutor.cpf == data.cpf).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este CPF já está cadastrado.")

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
        cpf=data.cpf,
        phone=data.phone,
        state=data.state,
        city=data.city,
        pets=data.pets,
        photo_url=data.photo_url,
    )
    db.add(tutor)
    db.commit()
    db.refresh(user)
    return create_token_for_user(user, pending=False)


def register_veterinarian(db: Session, data: VeterinarianCreate) -> Token:
    _existing = db.query(User).filter(User.email == data.email).first()
    if _existing:
        if not _existing.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail está associado a uma conta desativada. Entre em contato com o suporte.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail já possui cadastro. Tente fazer login ou recuperar a senha.")
    # Estudantes podem não ter CRMV; veterinários formados precisam informar.
    if not data.is_student and not data.crmv:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informe o CRMV ou marque que é estudante.")
    if data.crmv and db.query(Veterinarian).filter(Veterinarian.crmv == data.crmv).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este CRMV já está cadastrado na plataforma.")
    if data.cpf and db.query(Veterinarian).filter(Veterinarian.cpf == data.cpf).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este CPF já está cadastrado.")

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
        cpf=data.cpf,
        crmv=data.crmv,
        specialty=data.specialty,
        bio=data.bio,
        phone=data.phone,
        whatsapp=data.whatsapp,
        city=data.city,
        state=data.state,
        complement=data.complement,
        animal_species=data.animal_species,
        photo_url=data.photo_url,
        cover_photo_url=data.cover_photo_url,
        is_24h=data.is_24h,
        aplica_vacinas=data.aplica_vacinas,
        is_student=data.is_student,
        student_institution=data.student_institution,
        disp_plantao=data.disp_plantao,
        disp_volante=data.disp_volante,
        disp_oportunidades=data.disp_oportunidades,
        disp_parcerias=data.disp_parcerias,
        disp_estagio=data.disp_estagio,
        slug=slug,
        clinic_id=data.clinic_id,
    )
    db.add(veterinarian)
    db.commit()
    db.refresh(user)
    return create_token_for_user(user, pending=True)


def register_clinic(db: Session, data: ClinicCreate) -> Token:
    _existing = db.query(User).filter(User.email == data.email_user).first()
    if _existing:
        if not _existing.is_active:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail está associado a uma conta desativada. Entre em contato com o suporte.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail já possui cadastro. Tente fazer login ou recuperar a senha.")
    if data.cnpj and db.query(Clinic).filter(Clinic.cnpj == data.cnpj).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este CNPJ já está cadastrado na plataforma.")

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
        razao_social=data.razao_social,
        cnpj=data.cnpj,
        description=data.description,
        address=data.address,
        complement=data.complement,
        city=data.city,
        state=data.state,
        zip_code=data.zip_code,
        phone=data.phone,
        whatsapp=data.whatsapp,
        email=data.email,
        website=data.website,
        convenios=data.convenios,
        animal_species=data.animal_species,
        specialties=data.specialties,
        photo_url=data.photo_url,
        cover_photo_url=data.cover_photo_url,
        is_24h=data.is_24h,
        aplica_vacinas=data.aplica_vacinas,
        open_hiring=data.open_hiring,
        open_internship=data.open_internship,
        slug=slug,
    )
    db.add(clinic)
    db.commit()
    db.refresh(user)
    return create_token_for_user(user, pending=True)

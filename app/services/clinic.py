from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.clinic import Clinic
from app.schemas.clinic import ClinicUpdate


def get_clinic_by_id(db: Session, clinic_id: UUID) -> Optional[Clinic]:
    return db.query(Clinic).filter(Clinic.id == clinic_id).first()


def get_clinic_by_slug(db: Session, slug: str) -> Optional[Clinic]:
    return db.query(Clinic).filter(Clinic.slug == slug).first()


def search_clinics(
    db: Session,
    city: Optional[str] = None,
    state: Optional[str] = None,
    query: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Clinic]:
    q = db.query(Clinic)

    if city:
        q = q.filter(Clinic.city.ilike(f"%{city}%"))

    if state:
        q = q.filter(Clinic.state == state.upper())

    if query:
        q = q.filter(
            or_(
                Clinic.name.ilike(f"%{query}%"),
                Clinic.description.ilike(f"%{query}%"),
            )
        )

    return q.offset(skip).limit(limit).all()


def update_clinic(
    db: Session,
    clinic_id: UUID,
    user_id: UUID,
    data: ClinicUpdate,
) -> Clinic:
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clínica não encontrada",
        )

    if clinic.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar este perfil",
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(clinic, field, value)

    db.commit()
    db.refresh(clinic)

    return clinic

from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.veterinarian import Veterinarian
from app.schemas.veterinarian import VeterinarianUpdate


def get_veterinarian_by_id(db: Session, vet_id: UUID) -> Optional[Veterinarian]:
    return (
        db.query(Veterinarian)
        .options(joinedload(Veterinarian.clinic))
        .filter(Veterinarian.id == vet_id)
        .first()
    )


def get_veterinarian_by_slug(db: Session, slug: str) -> Optional[Veterinarian]:
    return (
        db.query(Veterinarian)
        .options(joinedload(Veterinarian.clinic))
        .filter(Veterinarian.slug == slug)
        .first()
    )


def search_veterinarians(
    db: Session,
    city: Optional[str] = None,
    state: Optional[str] = None,
    specialty: Optional[str] = None,
    query: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Veterinarian]:
    q = db.query(Veterinarian)

    if city:
        q = q.filter(Veterinarian.city.ilike(f"%{city}%"))

    if state:
        q = q.filter(Veterinarian.state == state.upper())

    if specialty:
        q = q.filter(Veterinarian.specialty.ilike(f"%{specialty}%"))

    if query:
        q = q.filter(
            or_(
                Veterinarian.full_name.ilike(f"%{query}%"),
                Veterinarian.crmv.ilike(f"%{query}%"),
            )
        )

    return q.offset(skip).limit(limit).all()


def update_veterinarian(
    db: Session,
    vet_id: UUID,
    user_id: UUID,
    data: VeterinarianUpdate,
) -> Veterinarian:
    vet = db.query(Veterinarian).filter(Veterinarian.id == vet_id).first()

    if not vet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinário(a) não encontrado(a)",
        )

    if vet.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar este perfil",
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(vet, field, value)

    db.commit()
    db.refresh(vet)

    return vet

from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.case import CaseComment, ClinicalCase
from app.models.user import UserType
from app.schemas.case import CaseCommentCreate, ClinicalCaseCreate


def create_clinical_case(
    db: Session,
    author_id: UUID,
    data: ClinicalCaseCreate,
) -> ClinicalCase:
    case = ClinicalCase(
        author_id=author_id,
        title=data.title,
        species=data.species,
        breed=data.breed,
        specialty=data.specialty,
        content=data.content,
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    return case


def get_clinical_case_by_id(db: Session, case_id: UUID) -> ClinicalCase:
    case = (
        db.query(ClinicalCase)
        .options(
            joinedload(ClinicalCase.author),
            joinedload(ClinicalCase.comments).joinedload(CaseComment.author),
        )
        .filter(ClinicalCase.id == case_id)
        .first()
    )

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso clínico não encontrado",
        )

    return case


def list_clinical_cases(
    db: Session,
    specialty: str = None,
    skip: int = 0,
    limit: int = 20,
) -> List[ClinicalCase]:
    q = db.query(ClinicalCase).options(joinedload(ClinicalCase.author))

    if specialty:
        q = q.filter(ClinicalCase.specialty.ilike(f"%{specialty}%"))

    return q.order_by(ClinicalCase.created_at.desc()).offset(skip).limit(limit).all()


def create_case_comment(
    db: Session,
    case_id: UUID,
    author_id: UUID,
    user_type: UserType,
    data: CaseCommentCreate,
) -> CaseComment:
    if user_type != UserType.VETERINARIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas veterinários podem comentar em casos clínicos",
        )

    case = db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso clínico não encontrado",
        )

    comment = CaseComment(
        case_id=case_id,
        author_id=author_id,
        content=data.content,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment

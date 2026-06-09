from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.case import CaseComment, ClinicalCase
from app.models.user import User
from app.models.veterinarian import Veterinarian
from app.schemas.case import CaseCommentCreate, ClinicalCaseCreate

router = APIRouter()


def _get_approved_vet(current_user: User, db: Session) -> Veterinarian:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça login como veterinário(a)")
    if current_user.user_type.value != "veterinarian":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas veterinários(as) podem realizar esta ação")
    vet = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
    if not vet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de veterinário(a) não encontrado")
    if not vet.is_approved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seu perfil precisa ser aprovado para publicar casos clínicos")
    return vet


@router.post("/")
def criar_caso(
    data: ClinicalCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vet = _get_approved_vet(current_user, db)
    case = ClinicalCase(
        author_id=vet.id,
        title=data.title,
        species=data.species,
        breed=data.breed,
        specialty=data.specialty,
        content=data.content,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return {"id": str(case.id)}


@router.post("/{case_id}/comentarios")
def criar_comentario(
    case_id: UUID,
    data: CaseCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vet = _get_approved_vet(current_user, db)
    case = db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso clínico não encontrado")
    comment = CaseComment(case_id=case_id, author_id=vet.id, content=data.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"id": str(comment.id)}

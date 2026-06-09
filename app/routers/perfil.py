from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.clinic import Clinic
from app.models.tutor import Tutor
from app.models.user import User
from app.models.veterinarian import Veterinarian
from app.schemas.clinic import ClinicUpdate
from app.schemas.tutor import TutorUpdate
from app.schemas.veterinarian import VeterinarianUpdate

router = APIRouter()


@router.put("/tutor")
def update_tutor_profile(data: TutorUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.user_type.value != "tutor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    tutor = db.query(Tutor).filter(Tutor.user_id == current_user.id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tutor, field, value)
    db.commit()
    return {"ok": True}


@router.put("/veterinarian")
def update_vet_profile(data: VeterinarianUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.user_type.value != "veterinarian":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    vet = db.query(Veterinarian).filter(Veterinarian.user_id == current_user.id).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vet, field, value)
    db.commit()
    return {"ok": True}


@router.put("/clinic")
def update_clinic_profile(data: ClinicUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or current_user.user_type.value != "clinic":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    clinic = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    not_null = {'name', 'city', 'state'}
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None and field in not_null:
            continue
        setattr(clinic, field, value)
    db.commit()
    return {"ok": True}

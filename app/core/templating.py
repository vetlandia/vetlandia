"""Instância compartilhada de Jinja2Templates com globals de negócio."""
from fastapi.templating import Jinja2Templates

from app.core.database import SessionLocal
from app.models.clinic import Clinic
from app.models.entitlement import clinic_has_product

templates = Jinja2Templates(directory="app/templates")


def _user_has_recrutamento(current_user) -> bool:
    """Jinja2 global: True se o usuário logado é clínica com entitlement 'recrutamento'."""
    if current_user is None:
        return False
    if current_user.user_type.value == "admin":
        return True
    if current_user.user_type.value != "clinic":
        return False
    db = SessionLocal()
    try:
        clinic = db.query(Clinic).filter(Clinic.user_id == current_user.id).first()
        return bool(clinic and clinic_has_product(clinic, "recrutamento"))
    finally:
        db.close()


templates.env.globals["user_has_recrutamento"] = _user_has_recrutamento

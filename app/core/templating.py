"""Instância compartilhada de Jinja2Templates com globals de negócio."""
import time
import threading

from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.clinic import Clinic
from app.models.entitlement import clinic_has_product

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["ga_measurement_id"] = settings.GA_MEASUREMENT_ID


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


# ── Cache de popup stats (60s TTL, thread-safe) ────────────────────────────────

_popup_lock = threading.Lock()
_popup_cache: dict = {}
_POPUP_TTL = 60.0


def _get_popup_stats() -> dict:
    """Jinja2 global: retorna stats do popup com cache de 60s em memória."""
    now = time.monotonic()
    with _popup_lock:
        if _popup_cache.get("ts", 0) + _POPUP_TTL > now:
            return _popup_cache["data"]

    db = SessionLocal()
    try:
        from app.models.site_config import get_config
        from app.models.veterinarian import Veterinarian

        enabled = get_config(db, "popup_enabled", "true").lower() == "true"
        vl = int(get_config(db, "popup_vet_limit", "100"))
        cl = int(get_config(db, "popup_clinic_limit", "30"))
        vc = db.query(Veterinarian).filter(
            Veterinarian.is_approved == True, Veterinarian.is_founder == True
        ).count()
        cc = db.query(Clinic).filter(
            Clinic.is_approved == True, Clinic.is_founder == True
        ).count()
        data = {
            "enabled": enabled,
            "vet_remaining": max(0, vl - vc),
            "vet_limit": vl,
            "clinic_remaining": max(0, cl - cc),
            "clinic_limit": cl,
        }
    except Exception:
        data = {"enabled": False}
    finally:
        db.close()

    with _popup_lock:
        _popup_cache["ts"] = now
        _popup_cache["data"] = data

    return data


templates.env.globals["get_popup_stats"] = _get_popup_stats

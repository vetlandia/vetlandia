"""Analytics interno do VetLândia.

Todas as gravações são fire-and-forget em threads daemon — zero latência nas rotas.
IPs são armazenados apenas como SHA-256 (LGPD).
"""
import hashlib
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.analytics import PageView, ProfileView, SearchLog

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _hash_ip(ip: str) -> Optional[str]:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


def _client_ip(request) -> Optional[str]:
    cf = request.headers.get("CF-Connecting-IP")
    if cf:
        return cf
    xf = request.headers.get("X-Forwarded-For")
    if xf:
        return xf.split(",")[0].strip()
    return request.client.host if request.client else None


def _run(fn):
    threading.Thread(target=fn, daemon=True).start()


# ── Gravação ───────────────────────────────────────────────────────────────────

def record_profile_view(entity_type: str, entity_id, request, user_id=None):
    ip = _client_ip(request)
    ip_hash = _hash_ip(ip)

    def _w():
        db = SessionLocal()
        try:
            db.add(ProfileView(
                entity_type=entity_type,
                entity_id=entity_id,
                viewer_ip_hash=ip_hash,
                viewer_user_id=user_id,
            ))
            db.commit()
        except Exception as e:
            logger.error("analytics.record_profile_view: %s", e)
            db.rollback()
        finally:
            db.close()

    _run(_w)


def record_search(query, specialty, city, entity_type, result_count, request, user_id=None):
    ip = _client_ip(request)

    def _w():
        db = SessionLocal()
        try:
            db.add(SearchLog(
                query=(query or "")[:200] or None,
                specialty=specialty or None,
                city=city or None,
                entity_type=entity_type or None,
                result_count=result_count or 0,
                user_id=user_id,
            ))
            db.commit()
        except Exception as e:
            logger.error("analytics.record_search: %s", e)
            db.rollback()
        finally:
            db.close()

    _run(_w)


def record_page_view(path: str, request, user_id=None):
    ip = _client_ip(request)
    ip_hash = _hash_ip(ip)

    def _w():
        db = SessionLocal()
        try:
            db.add(PageView(path=path[:500], ip_hash=ip_hash, user_id=user_id))
            db.commit()
        except Exception as e:
            logger.error("analytics.record_page_view: %s", e)
            db.rollback()
        finally:
            db.close()

    _run(_w)


# ── Queries — perfil individual ────────────────────────────────────────────────

def profile_stats(db: Session, entity_type: str, entity_id) -> dict:
    """Estatísticas de visualização para um perfil específico."""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    prev_month_start = now - timedelta(days=60)

    base = db.query(func.count(ProfileView.id)).filter(
        ProfileView.entity_type == entity_type,
        ProfileView.entity_id == entity_id,
    )

    total = base.scalar() or 0
    today_count = base.filter(ProfileView.viewed_at >= today).scalar() or 0
    week_count = base.filter(ProfileView.viewed_at >= week_ago).scalar() or 0
    month_count = base.filter(ProfileView.viewed_at >= month_ago).scalar() or 0
    prev_month_count = (
        db.query(func.count(ProfileView.id))
        .filter(
            ProfileView.entity_type == entity_type,
            ProfileView.entity_id == entity_id,
            ProfileView.viewed_at >= prev_month_start,
            ProfileView.viewed_at < month_ago,
        )
        .scalar() or 0
    )

    growth = 0
    if prev_month_count > 0:
        growth = round((month_count - prev_month_count) / prev_month_count * 100)
    elif month_count > 0:
        growth = 100

    # Últimos 14 dias dia a dia
    daily = []
    for i in range(13, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        cnt = (
            db.query(func.count(ProfileView.id))
            .filter(
                ProfileView.entity_type == entity_type,
                ProfileView.entity_id == entity_id,
                ProfileView.viewed_at >= day_start,
                ProfileView.viewed_at < day_end,
            )
            .scalar() or 0
        )
        daily.append({"date": day_start.strftime("%d/%m"), "count": cnt})

    return {
        "total": total,
        "today": today_count,
        "week": week_count,
        "month": month_count,
        "prev_month": prev_month_count,
        "growth": growth,
        "daily": daily,
    }


# ── Queries — admin ─────────────────────────────────────────────────────────────

def platform_stats(db: Session) -> dict:
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total_pv = db.query(func.count(PageView.id)).scalar() or 0
    unique_today = (
        db.query(func.count(func.distinct(PageView.ip_hash)))
        .filter(PageView.occurred_at >= today, PageView.ip_hash.isnot(None))
        .scalar() or 0
    )
    unique_week = (
        db.query(func.count(func.distinct(PageView.ip_hash)))
        .filter(PageView.occurred_at >= week_ago, PageView.ip_hash.isnot(None))
        .scalar() or 0
    )
    unique_month = (
        db.query(func.count(func.distinct(PageView.ip_hash)))
        .filter(PageView.occurred_at >= month_ago, PageView.ip_hash.isnot(None))
        .scalar() or 0
    )
    logged_in_today = (
        db.query(func.count(func.distinct(PageView.user_id)))
        .filter(PageView.occurred_at >= today, PageView.user_id.isnot(None))
        .scalar() or 0
    )

    return {
        "total_page_views": total_pv,
        "unique_today": unique_today,
        "unique_week": unique_week,
        "unique_month": unique_month,
        "logged_in_today": logged_in_today,
    }


def top_profiles(db: Session, entity_type: str, limit: int = 10) -> list:
    rows = (
        db.query(ProfileView.entity_id, func.count(ProfileView.id).label("views"))
        .filter(ProfileView.entity_type == entity_type)
        .group_by(ProfileView.entity_id)
        .order_by(func.count(ProfileView.id).desc())
        .limit(limit)
        .all()
    )
    return [{"entity_id": str(r.entity_id), "views": r.views} for r in rows]


def search_trends(db: Session, limit: int = 10) -> dict:
    def _top(col):
        rows = (
            db.query(col, func.count(SearchLog.id).label("cnt"))
            .filter(col.isnot(None), col != "")
            .group_by(col)
            .order_by(func.count(SearchLog.id).desc())
            .limit(limit)
            .all()
        )
        return [{"value": r[0], "count": r[1]} for r in rows]

    return {
        "specialties": _top(SearchLog.specialty),
        "cities": _top(SearchLog.city),
        "queries": _top(SearchLog.query),
    }


def daily_new_users(db: Session, days: int = 30) -> list:
    from app.models.user import User
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for i in range(days - 1, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        cnt = (
            db.query(func.count(User.id))
            .filter(User.created_at >= day_start, User.created_at < day_end)
            .scalar() or 0
        )
        result.append({"date": day_start.strftime("%d/%m"), "count": cnt})
    return result


def daily_page_views(db: Session, days: int = 30) -> list:
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for i in range(days - 1, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        cnt = (
            db.query(func.count(PageView.id))
            .filter(PageView.occurred_at >= day_start, PageView.occurred_at < day_end)
            .scalar() or 0
        )
        result.append({"date": day_start.strftime("%d/%m"), "count": cnt})
    return result


def daily_searches(db: Session, days: int = 30) -> list:
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for i in range(days - 1, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        cnt = (
            db.query(func.count(SearchLog.id))
            .filter(SearchLog.searched_at >= day_start, SearchLog.searched_at < day_end)
            .scalar() or 0
        )
        result.append({"date": day_start.strftime("%d/%m"), "count": cnt})
    return result

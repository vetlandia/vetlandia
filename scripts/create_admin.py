#!/usr/bin/env python3
"""
Cria o administrador principal do VetLândia.
Execute: python scripts/create_admin.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.administrator import Administrator
from app.models.user import User, UserType

ADMIN_EMAIL = "admin@vetlandia.com.br"
ADMIN_PASSWORD = "vetlandia@2026"
ADMIN_NAME = "Administrador VetLândia"


def create_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if existing:
            print(f"✅ Admin já existe: {ADMIN_EMAIL}")
            return

        user = User(
            email=ADMIN_EMAIL,
            password_hash=get_password_hash(ADMIN_PASSWORD),
            user_type=UserType.ADMIN,
            is_active=True,
        )
        db.add(user)
        db.flush()

        admin = Administrator(
            user_id=user.id,
            full_name=ADMIN_NAME,
        )
        db.add(admin)
        db.commit()

        print("🎉 Administrador criado com sucesso!")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Senha: {ADMIN_PASSWORD}")
        print(f"   URL:   https://vetlandia.com.br/login")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()

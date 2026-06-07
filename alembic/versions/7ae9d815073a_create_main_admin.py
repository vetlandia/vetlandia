"""create_main_admin

Revision ID: 7ae9d815073a
Revises: a8e658a14ef4
Create Date: 2026-06-07 07:11:00.982760

"""
from alembic import op
import sqlalchemy as sa


revision = '7ae9d815073a'
down_revision = 'a8e658a14ef4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    import uuid
    from datetime import datetime
    from passlib.context import CryptContext

    conn = op.get_bind()

    existing = conn.execute(
        sa.text("SELECT id FROM users WHERE email = 'admin@vetlandia.com.br'")
    ).fetchone()

    if existing:
        print("✅ Admin já existe, pulando criação.")
        return

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash("vetlandia@2026")

    user_id = str(uuid.uuid4())
    now = datetime.utcnow()

    conn.execute(
        sa.text("""
            INSERT INTO users (id, email, password_hash, user_type, is_active, created_at, updated_at)
            VALUES (:id, :email, :password_hash, 'admin', true, :now, :now)
        """),
        {"id": user_id, "email": "admin@vetlandia.com.br", "password_hash": password_hash, "now": now},
    )

    admin_id = str(uuid.uuid4())
    conn.execute(
        sa.text("""
            INSERT INTO administrators (id, user_id, full_name, created_at, updated_at)
            VALUES (:id, :user_id, 'Administrador VetLândia', :now, :now)
        """),
        {"id": admin_id, "user_id": user_id, "now": now},
    )

    print("🎉 Admin criado: admin@vetlandia.com.br")


def downgrade() -> None:
    op.get_bind().execute(
        sa.text("DELETE FROM users WHERE email = 'admin@vetlandia.com.br'")
    )

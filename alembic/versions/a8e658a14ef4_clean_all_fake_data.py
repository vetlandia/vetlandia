"""clean_all_fake_data

Revision ID: a8e658a14ef4
Revises: 5486fcdc671f
Create Date: 2026-06-06 23:25:12.664916

"""
from alembic import op
import sqlalchemy as sa


revision = 'a8e658a14ef4'
down_revision = '5486fcdc671f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove todos os dados fictícios do banco de produção."""
    conn = op.get_bind()

    # Deletar na ordem correta (respeitar foreign keys)
    print("🧹 Removendo dados fictícios...")

    conn.execute(sa.text("DELETE FROM case_comments"))
    print("✅ Comentários de casos removidos")

    conn.execute(sa.text("DELETE FROM comments"))
    print("✅ Comentários de reviews removidos")

    conn.execute(sa.text("DELETE FROM reviews"))
    print("✅ Reviews removidas")

    conn.execute(sa.text("DELETE FROM clinical_cases"))
    print("✅ Casos clínicos removidos")

    conn.execute(sa.text("DELETE FROM veterinarians"))
    print("✅ Veterinários removidos")

    conn.execute(sa.text("DELETE FROM clinics"))
    print("✅ Clínicas removidas")

    conn.execute(sa.text("DELETE FROM tutors"))
    print("✅ Tutores removidos")

    conn.execute(sa.text("DELETE FROM administrators"))
    print("✅ Administradores removidos")

    conn.execute(sa.text("DELETE FROM users"))
    print("✅ Usuários removidos")

    print("🎉 Banco limpo!")


def downgrade() -> None:
    """Não é possível reverter limpeza de dados."""
    pass

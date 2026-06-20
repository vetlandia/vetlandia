"""backfill is_verified para aprovados existentes

Revision ID: l0a1b2c3d4e5
Revises: k9f0a1b2c3d4
Create Date: 2026-06-20 01:00:00.000000

Mantém o selo verde dos perfis JÁ aprovados ao mudar a semântica do
"Perfil Verificado" (que passou a depender de is_verified). Marca como
verificados os veterinários e clínicas atualmente aprovados.
"""
from alembic import op

revision = 'l0a1b2c3d4e5'
down_revision = 'k9f0a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE veterinarians SET is_verified = true WHERE is_approved = true")
    op.execute("UPDATE clinics SET is_verified = true WHERE is_approved = true")


def downgrade():
    # Reverte o backfill (best-effort): remove a verificação dos aprovados.
    op.execute("UPDATE veterinarians SET is_verified = false WHERE is_approved = true")
    op.execute("UPDATE clinics SET is_verified = false WHERE is_approved = true")

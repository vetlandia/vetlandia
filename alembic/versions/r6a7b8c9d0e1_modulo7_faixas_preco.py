"""modulo7 faixas de preco da clinica

Revision ID: r6a7b8c9d0e1
Revises: q5f6a7b8c9d0
Create Date: 2026-06-20 07:00:00.000000

Aditiva e reversível: faixas de preço (consulta e procedimento) na clínica.
Apenas faixas (economica/intermediaria/premium) — nunca valor exato. Opcionais.
"""
from alembic import op
import sqlalchemy as sa

revision = 'r6a7b8c9d0e1'
down_revision = 'q5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clinics', sa.Column('consulta_faixa', sa.String(length=20), nullable=True))
    op.add_column('clinics', sa.Column('procedimento_faixa', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('clinics', 'procedimento_faixa')
    op.drop_column('clinics', 'consulta_faixa')

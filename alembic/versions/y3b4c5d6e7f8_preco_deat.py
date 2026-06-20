"""clinica: faixa de preco de/ate em R$ (consulta e procedimento)

Revision ID: y3b4c5d6e7f8
Revises: x2a3b4c5d6e7
Create Date: 2026-06-20 16:00:00.000000

Aditiva e reversível: adiciona 4 colunas inteiras para faixa de preço
(de/até em R$) em substituição às categorias (econômica/intermediária/premium).
Colunas antigas (consulta_faixa/procedimento_faixa) mantidas como nullable legadas.
"""
from alembic import op
import sqlalchemy as sa

revision = 'y3b4c5d6e7f8'
down_revision = 'x2a3b4c5d6e7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clinics', sa.Column('consulta_preco_min', sa.Integer(), nullable=True))
    op.add_column('clinics', sa.Column('consulta_preco_max', sa.Integer(), nullable=True))
    op.add_column('clinics', sa.Column('procedimento_preco_min', sa.Integer(), nullable=True))
    op.add_column('clinics', sa.Column('procedimento_preco_max', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('clinics', 'procedimento_preco_max')
    op.drop_column('clinics', 'procedimento_preco_min')
    op.drop_column('clinics', 'consulta_preco_max')
    op.drop_column('clinics', 'consulta_preco_min')

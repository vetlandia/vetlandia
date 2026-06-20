"""clinica aberta para contratacao (efetivo/estagio)

Revision ID: x2a3b4c5d6e7
Revises: w1f2a3b4c5d6
Create Date: 2026-06-20 13:00:00.000000

Aditiva e reversível: a clínica indica se está aberta para contratar efetivo
e/ou receber estagiários.
"""
from alembic import op
import sqlalchemy as sa

revision = 'x2a3b4c5d6e7'
down_revision = 'w1f2a3b4c5d6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clinics', sa.Column('open_hiring', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('clinics', sa.Column('open_internship', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('clinics', 'open_internship')
    op.drop_column('clinics', 'open_hiring')

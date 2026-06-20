"""modulo6 has_recruitment_access na clinica

Revision ID: q5f6a7b8c9d0
Revises: p4e5f6a7b8c9
Create Date: 2026-06-20 06:00:00.000000

Aditiva e reversível: flag que libera a clínica a ver dados de recrutamento
dos veterinários (disponibilidades, histórico profissional). Default false.
"""
from alembic import op
import sqlalchemy as sa

revision = 'q5f6a7b8c9d0'
down_revision = 'p4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clinics', sa.Column('has_recruitment_access', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('clinics', 'has_recruitment_access')

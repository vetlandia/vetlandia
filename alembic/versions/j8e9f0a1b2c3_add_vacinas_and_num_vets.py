"""add aplica_vacinas and num_veterinarios

Revision ID: j8e9f0a1b2c3
Revises: i7d8e9f0a1b2
Create Date: 2026-06-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'j8e9f0a1b2c3'
down_revision = 'i7d8e9f0a1b2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('veterinarians', sa.Column('aplica_vacinas', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('clinics', sa.Column('aplica_vacinas', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('clinics', sa.Column('num_veterinarios', sa.String(10), nullable=True))


def downgrade():
    op.drop_column('veterinarians', 'aplica_vacinas')
    op.drop_column('clinics', 'aplica_vacinas')
    op.drop_column('clinics', 'num_veterinarios')

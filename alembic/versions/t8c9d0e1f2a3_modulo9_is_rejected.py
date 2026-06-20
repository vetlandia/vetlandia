"""modulo9 is_rejected reversivel (vet e clinica)

Revision ID: t8c9d0e1f2a3
Revises: s7b8c9d0e1f2
Create Date: 2026-06-20 09:00:00.000000

Aditiva e reversível: estado de reprovação reversível para veterinários e
clínicas, substituindo a exclusão física no fluxo de "Reprovar". Default false.
"""
from alembic import op
import sqlalchemy as sa

revision = 't8c9d0e1f2a3'
down_revision = 's7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('veterinarians', sa.Column('is_rejected', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('clinics', sa.Column('is_rejected', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('clinics', 'is_rejected')
    op.drop_column('veterinarians', 'is_rejected')

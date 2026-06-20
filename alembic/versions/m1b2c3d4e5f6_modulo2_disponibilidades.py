"""modulo2 disponibilidades profissionais do veterinario

Revision ID: m1b2c3d4e5f6
Revises: l0a1b2c3d4e5
Create Date: 2026-06-20 02:00:00.000000

Aditiva e reversível: flags opcionais de disponibilidade para recrutamento.
Default false (o veterinário pode não desejar recrutamento).
"""
from alembic import op
import sqlalchemy as sa

revision = 'm1b2c3d4e5f6'
down_revision = 'l0a1b2c3d4e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('veterinarians', sa.Column('disp_plantao', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('veterinarians', sa.Column('disp_volante', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('veterinarians', sa.Column('disp_oportunidades', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('veterinarians', sa.Column('disp_parcerias', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('veterinarians', 'disp_parcerias')
    op.drop_column('veterinarians', 'disp_oportunidades')
    op.drop_column('veterinarians', 'disp_volante')
    op.drop_column('veterinarians', 'disp_plantao')

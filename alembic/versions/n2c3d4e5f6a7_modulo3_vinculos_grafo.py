"""modulo3 vinculos profissionais vet-clinica (grafo)

Revision ID: n2c3d4e5f6a7
Revises: m1b2c3d4e5f6
Create Date: 2026-06-20 03:00:00.000000

Aditiva e reversível: nova tabela vet_clinic_links (N:N vet<->clínica) para
múltiplos vínculos simultâneos e histórico profissional. Preserva a coluna
legada veterinarians.clinic_id (não é removida).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'n2c3d4e5f6a7'
down_revision = 'm1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'vet_clinic_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('veterinarian_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=120), nullable=True),
        sa.Column('start_year', sa.String(length=4), nullable=True),
        sa.Column('end_year', sa.String(length=4), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['veterinarian_id'], ['veterinarians.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vet_clinic_links_veterinarian_id', 'vet_clinic_links', ['veterinarian_id'])
    op.create_index('ix_vet_clinic_links_clinic_id', 'vet_clinic_links', ['clinic_id'])


def downgrade():
    op.drop_index('ix_vet_clinic_links_clinic_id', table_name='vet_clinic_links')
    op.drop_index('ix_vet_clinic_links_veterinarian_id', table_name='vet_clinic_links')
    op.drop_table('vet_clinic_links')

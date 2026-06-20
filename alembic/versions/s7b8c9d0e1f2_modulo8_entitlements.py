"""modulo8 clinic entitlements

Revision ID: s7b8c9d0e1f2
Revises: r6a7b8c9d0e1
Create Date: 2026-06-20 08:00:00.000000

Aditiva e reversível: tabela clinic_entitlements (produtos liberados por clínica,
sem cobrança). Faz backfill: clínicas com has_recruitment_access=true (Módulo 6)
ganham o entitlement 'recrutamento', que passa a ser a fonte de verdade. A coluna
has_recruitment_access é preservada (não removida).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 's7b8c9d0e1f2'
down_revision = 'r6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'clinic_entitlements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clinic_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product', sa.String(length=40), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clinic_id', 'product', name='unique_clinic_product'),
    )
    op.create_index('ix_clinic_entitlements_clinic_id', 'clinic_entitlements', ['clinic_id'])

    # Backfill: quem já tinha acesso de recrutamento (Módulo 6) vira entitlement.
    op.execute(
        "INSERT INTO clinic_entitlements (id, clinic_id, product, is_active, created_at) "
        "SELECT gen_random_uuid(), id, 'recrutamento', true, now() "
        "FROM clinics WHERE has_recruitment_access = true"
    )


def downgrade():
    op.drop_index('ix_clinic_entitlements_clinic_id', table_name='clinic_entitlements')
    op.drop_table('clinic_entitlements')

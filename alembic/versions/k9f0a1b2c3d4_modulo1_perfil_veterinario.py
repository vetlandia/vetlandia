"""modulo1 enriquecimento do perfil do veterinario

Revision ID: k9f0a1b2c3d4
Revises: j8e9f0a1b2c3
Create Date: 2026-06-20 00:00:00.000000

Aditiva e reversível:
- veterinarians: especialidades múltiplas (JSON), site/redes, upload da carteira,
  selo "Perfil Verificado".
- clinics: selo "Perfil Verificado".
- nova tabela vet_educations (formação acadêmica, múltipla por veterinário).
Preserva colunas existentes (specialty singular, clinic_id) — nada é removido.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'k9f0a1b2c3d4'
down_revision = 'j8e9f0a1b2c3'
branch_labels = None
depends_on = None


def upgrade():
    # ── veterinarians ───────────────────────────────────────────────────
    op.add_column('veterinarians', sa.Column('specialties', sa.Text(), nullable=True))
    op.add_column('veterinarians', sa.Column('website', sa.String(length=500), nullable=True))
    op.add_column('veterinarians', sa.Column('linkedin', sa.String(length=255), nullable=True))
    op.add_column('veterinarians', sa.Column('instagram', sa.String(length=255), nullable=True))
    op.add_column('veterinarians', sa.Column('lattes', sa.String(length=255), nullable=True))
    op.add_column('veterinarians', sa.Column('crmv_card_url', sa.Text(), nullable=True))
    op.add_column('veterinarians', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))

    # ── clinics ─────────────────────────────────────────────────────────
    op.add_column('clinics', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))

    # ── vet_educations (nova tabela) ────────────────────────────────────
    op.create_table(
        'vet_educations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('veterinarian_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('instituicao', sa.String(length=255), nullable=False),
        sa.Column('curso', sa.String(length=255), nullable=True),
        sa.Column('area', sa.String(length=255), nullable=True),
        sa.Column('ano_conclusao', sa.String(length=4), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['veterinarian_id'], ['veterinarians.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vet_educations_veterinarian_id', 'vet_educations', ['veterinarian_id'])


def downgrade():
    op.drop_index('ix_vet_educations_veterinarian_id', table_name='vet_educations')
    op.drop_table('vet_educations')
    op.drop_column('clinics', 'is_verified')
    op.drop_column('veterinarians', 'is_verified')
    op.drop_column('veterinarians', 'crmv_card_url')
    op.drop_column('veterinarians', 'lattes')
    op.drop_column('veterinarians', 'instagram')
    op.drop_column('veterinarians', 'linkedin')
    op.drop_column('veterinarians', 'website')
    op.drop_column('veterinarians', 'specialties')

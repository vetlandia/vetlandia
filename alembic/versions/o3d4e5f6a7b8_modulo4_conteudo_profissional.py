"""modulo4 conteudo profissional (links externos)

Revision ID: o3d4e5f6a7b8
Revises: n2c3d4e5f6a7
Create Date: 2026-06-20 04:00:00.000000

Aditiva e reversível: nova tabela vet_contents (links externos). Os casos
clínicos internos (clinical_cases / case_comments) NÃO são tocados — apenas
ocultados na interface.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'o3d4e5f6a7b8'
down_revision = 'n2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'vet_contents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('veterinarian_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['veterinarian_id'], ['veterinarians.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vet_contents_veterinarian_id', 'vet_contents', ['veterinarian_id'])


def downgrade():
    op.drop_index('ix_vet_contents_veterinarian_id', table_name='vet_contents')
    op.drop_table('vet_contents')

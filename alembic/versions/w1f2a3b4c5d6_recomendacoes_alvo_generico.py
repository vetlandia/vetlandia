"""recomendacoes com alvo generico (vet ou clinica)

Revision ID: w1f2a3b4c5d6
Revises: v0e1f2a3b4c5
Create Date: 2026-06-20 12:00:00.000000

Aditiva e reversível: generaliza o alvo da recomendação (target_type/target_id)
para veterinário OU clínica. Backfill dos registros existentes (eram p/ vet).
Mantém target_vet_id (legado, agora nullable).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'w1f2a3b4c5d6'
down_revision = 'v0e1f2a3b4c5'
branch_labels = None
depends_on = None


def upgrade():
    rec_type = postgresql.ENUM('veterinarian', 'clinic', name='recommendertype', create_type=False)
    op.add_column('recommendations', sa.Column('target_type', rec_type, nullable=True))
    op.add_column('recommendations', sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True))
    # Backfill: registros existentes eram sempre para veterinário
    op.execute("UPDATE recommendations SET target_type = 'veterinarian', target_id = target_vet_id WHERE target_id IS NULL")
    op.alter_column('recommendations', 'target_type', nullable=False)
    op.alter_column('recommendations', 'target_id', nullable=False)
    op.alter_column('recommendations', 'target_vet_id', existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.create_index('ix_recommendations_target_id', 'recommendations', ['target_id'])
    op.drop_constraint('unique_recommendation', 'recommendations', type_='unique')
    op.create_unique_constraint('unique_recommendation_v2', 'recommendations', ['author_type', 'author_id', 'target_type', 'target_id'])


def downgrade():
    op.drop_constraint('unique_recommendation_v2', 'recommendations', type_='unique')
    op.create_unique_constraint('unique_recommendation', 'recommendations', ['author_type', 'author_id', 'target_vet_id'])
    op.drop_index('ix_recommendations_target_id', table_name='recommendations')
    # volta target_vet_id a NOT NULL (falha se houver recomendações p/ clínica)
    op.alter_column('recommendations', 'target_vet_id', existing_type=postgresql.UUID(as_uuid=True), nullable=False)
    op.drop_column('recommendations', 'target_id')
    op.drop_column('recommendations', 'target_type')

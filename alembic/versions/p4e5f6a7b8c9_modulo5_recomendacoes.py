"""modulo5 recomendacoes profissionais

Revision ID: p4e5f6a7b8c9
Revises: o3d4e5f6a7b8
Create Date: 2026-06-20 05:00:00.000000

Aditiva e reversível: nova tabela recommendations (vet ou clínica recomenda
um veterinário), com moderação. Cria os enums recommendertype/recommendationstatus.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'p4e5f6a7b8c9'
down_revision = 'o3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    rec_type = postgresql.ENUM('veterinarian', 'clinic', name='recommendertype')
    rec_status = postgresql.ENUM('pending', 'approved', 'rejected', name='recommendationstatus')
    rec_type.create(bind, checkfirst=True)
    rec_status.create(bind, checkfirst=True)

    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('author_type', postgresql.ENUM('veterinarian', 'clinic', name='recommendertype', create_type=False), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_vet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', name='recommendationstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['target_vet_id'], ['veterinarians.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('author_type', 'author_id', 'target_vet_id', name='unique_recommendation'),
        sa.CheckConstraint('length(content) >= 10', name='min_recommendation_length'),
    )
    op.create_index('ix_recommendations_author_id', 'recommendations', ['author_id'])
    op.create_index('ix_recommendations_target_vet_id', 'recommendations', ['target_vet_id'])
    op.create_index('ix_recommendations_status', 'recommendations', ['status'])


def downgrade():
    op.drop_index('ix_recommendations_status', table_name='recommendations')
    op.drop_index('ix_recommendations_target_vet_id', table_name='recommendations')
    op.drop_index('ix_recommendations_author_id', table_name='recommendations')
    op.drop_table('recommendations')
    bind = op.get_bind()
    postgresql.ENUM(name='recommendationstatus').drop(bind, checkfirst=True)
    postgresql.ENUM(name='recommendertype').drop(bind, checkfirst=True)

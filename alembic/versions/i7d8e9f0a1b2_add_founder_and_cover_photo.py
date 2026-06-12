"""add is_founder and cover_photo_url

Revision ID: i7d8e9f0a1b2
Revises: h6c7d8e9f0a1
Create Date: 2026-06-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'i7d8e9f0a1b2'
down_revision = 'h6c7d8e9f0a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('veterinarians', sa.Column('is_founder', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('veterinarians', sa.Column('cover_photo_url', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('is_founder', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('clinics', sa.Column('cover_photo_url', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('veterinarians', 'cover_photo_url')
    op.drop_column('veterinarians', 'is_founder')
    op.drop_column('clinics', 'cover_photo_url')
    op.drop_column('clinics', 'is_founder')

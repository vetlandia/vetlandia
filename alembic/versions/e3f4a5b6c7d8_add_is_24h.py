"""Add is_24h to veterinarians and clinics

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa

revision = 'e3f4a5b6c7d8'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('veterinarians', sa.Column('is_24h', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('clinics', sa.Column('is_24h', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('veterinarians', 'is_24h')
    op.drop_column('clinics', 'is_24h')

"""photo_url columns to TEXT for base64 data URLs

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-06-08

"""
from alembic import op
import sqlalchemy as sa

revision = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('veterinarians', 'photo_url', type_=sa.Text(), existing_nullable=True)
    op.alter_column('clinics', 'logo_url',   type_=sa.Text(), existing_nullable=True)
    op.alter_column('clinics', 'photo_url',  type_=sa.Text(), existing_nullable=True)


def downgrade():
    op.alter_column('veterinarians', 'photo_url', type_=sa.String(500), existing_nullable=True)
    op.alter_column('clinics', 'logo_url',   type_=sa.String(500), existing_nullable=True)
    op.alter_column('clinics', 'photo_url',  type_=sa.String(500), existing_nullable=True)

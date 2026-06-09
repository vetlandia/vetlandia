"""Add photo_url to tutors

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa

revision = 'f4a5b6c7d8e9'
down_revision = 'e3f4a5b6c7d8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tutors', sa.Column('photo_url', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('tutors', 'photo_url')

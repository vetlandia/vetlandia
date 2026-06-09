"""add comment status

Revision ID: h6c7d8e9f0a1
Revises: g5b6c7d8e9f0
Create Date: 2026-06-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'h6c7d8e9f0a1'
down_revision = 'g5b6c7d8e9f0'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    # casestatus type already exists from previous migration
    conn.execute(sa.text("""
        ALTER TABLE case_comments
        ADD COLUMN IF NOT EXISTS status casestatus NOT NULL DEFAULT 'pending'
    """))
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_case_comments_status
        ON case_comments (status)
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_case_comments_status"))
    conn.execute(sa.text("ALTER TABLE case_comments DROP COLUMN IF EXISTS status"))

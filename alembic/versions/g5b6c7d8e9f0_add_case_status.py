"""add case status

Revision ID: g5b6c7d8e9f0
Revises: f4a5b6c7d8e9
Create Date: 2026-06-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'g5b6c7d8e9f0'
down_revision = 'f4a5b6c7d8e9'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Create enum type (idempotent)
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE casestatus AS ENUM ('pending', 'approved', 'rejected');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """))

    # Add column (idempotent)
    conn.execute(sa.text("""
        ALTER TABLE clinical_cases
        ADD COLUMN IF NOT EXISTS status casestatus NOT NULL DEFAULT 'pending'
    """))

    # Create index (idempotent)
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_clinical_cases_status
        ON clinical_cases (status)
    """))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_clinical_cases_status"))
    conn.execute(sa.text("ALTER TABLE clinical_cases DROP COLUMN IF EXISTS status"))
    conn.execute(sa.text("DROP TYPE IF EXISTS casestatus"))

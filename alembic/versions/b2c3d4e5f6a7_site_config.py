"""site_config: key-value store for popup + other settings

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "site_config",
        sa.Column("key", sa.String(100), primary_key=True),
        sa.Column("value", sa.Text, nullable=True),
    )
    op.execute("INSERT INTO site_config (key, value) VALUES ('popup_enabled', 'true')")
    op.execute("INSERT INTO site_config (key, value) VALUES ('popup_vet_limit', '100')")
    op.execute("INSERT INTO site_config (key, value) VALUES ('popup_clinic_limit', '30')")


def downgrade():
    op.drop_table("site_config")

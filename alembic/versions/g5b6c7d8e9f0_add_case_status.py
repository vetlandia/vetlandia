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

_casestatus = sa.Enum('pending', 'approved', 'rejected', name='casestatus')


def upgrade():
    _casestatus.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'clinical_cases',
        sa.Column(
            'status',
            sa.Enum('pending', 'approved', 'rejected', name='casestatus', create_type=False),
            nullable=False,
            server_default='pending',
        )
    )
    op.create_index('ix_clinical_cases_status', 'clinical_cases', ['status'])


def downgrade():
    op.drop_index('ix_clinical_cases_status', table_name='clinical_cases')
    op.drop_column('clinical_cases', 'status')
    _casestatus.drop(op.get_bind(), checkfirst=True)

"""estudantes de veterinaria (crmv opcional + campos de estudante)

Revision ID: v0e1f2a3b4c5
Revises: u9d0e1f2a3b4
Create Date: 2026-06-20 11:00:00.000000

Aditiva e reversível: permite estudantes (sem CRMV). Torna crmv nullable e
adiciona is_student, student_institution e disp_estagio.
"""
from alembic import op
import sqlalchemy as sa

revision = 'v0e1f2a3b4c5'
down_revision = 'u9d0e1f2a3b4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('veterinarians', 'crmv', existing_type=sa.String(length=20), nullable=True)
    op.add_column('veterinarians', sa.Column('is_student', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('veterinarians', sa.Column('student_institution', sa.String(length=255), nullable=True))
    op.add_column('veterinarians', sa.Column('disp_estagio', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index('ix_veterinarians_is_student', 'veterinarians', ['is_student'])


def downgrade():
    op.drop_index('ix_veterinarians_is_student', table_name='veterinarians')
    op.drop_column('veterinarians', 'disp_estagio')
    op.drop_column('veterinarians', 'student_institution')
    op.drop_column('veterinarians', 'is_student')
    # Atenção: volta a NOT NULL; falha se houver vet sem CRMV (estudantes).
    op.alter_column('veterinarians', 'crmv', existing_type=sa.String(length=20), nullable=False)

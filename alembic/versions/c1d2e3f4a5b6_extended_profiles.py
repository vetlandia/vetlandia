"""extended profile fields for tutor, vet and clinic

Revision ID: c1d2e3f4a5b6
Revises: a8e658a14ef4
Create Date: 2026-06-08

"""
from alembic import op
import sqlalchemy as sa

revision = 'c1d2e3f4a5b6'
down_revision = 'a8e658a14ef4'
branch_labels = None
depends_on = None


def upgrade():
    # tutors
    op.add_column('tutors', sa.Column('cpf', sa.String(14), nullable=True))
    op.add_column('tutors', sa.Column('state', sa.String(2), nullable=True))
    op.add_column('tutors', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('tutors', sa.Column('address', sa.String(500), nullable=True))
    op.add_column('tutors', sa.Column('complement', sa.String(200), nullable=True))
    op.add_column('tutors', sa.Column('pets', sa.Text(), nullable=True))

    # veterinarians
    op.add_column('veterinarians', sa.Column('cpf', sa.String(14), nullable=True))
    op.add_column('veterinarians', sa.Column('whatsapp', sa.String(20), nullable=True))
    op.add_column('veterinarians', sa.Column('complement', sa.String(200), nullable=True))
    op.add_column('veterinarians', sa.Column('animal_species', sa.Text(), nullable=True))

    # clinics
    op.add_column('clinics', sa.Column('razao_social', sa.String(255), nullable=True))
    op.add_column('clinics', sa.Column('cnpj', sa.String(18), nullable=True))
    op.add_column('clinics', sa.Column('whatsapp', sa.String(20), nullable=True))
    op.add_column('clinics', sa.Column('complement', sa.String(200), nullable=True))
    op.add_column('clinics', sa.Column('convenios', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('animal_species', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('specialties', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('photo_url', sa.String(500), nullable=True))


def downgrade():
    op.drop_column('tutors', 'cpf')
    op.drop_column('tutors', 'state')
    op.drop_column('tutors', 'city')
    op.drop_column('tutors', 'address')
    op.drop_column('tutors', 'complement')
    op.drop_column('tutors', 'pets')

    op.drop_column('veterinarians', 'cpf')
    op.drop_column('veterinarians', 'whatsapp')
    op.drop_column('veterinarians', 'complement')
    op.drop_column('veterinarians', 'animal_species')

    op.drop_column('clinics', 'razao_social')
    op.drop_column('clinics', 'cnpj')
    op.drop_column('clinics', 'whatsapp')
    op.drop_column('clinics', 'complement')
    op.drop_column('clinics', 'convenios')
    op.drop_column('clinics', 'animal_species')
    op.drop_column('clinics', 'specialties')
    op.drop_column('clinics', 'photo_url')

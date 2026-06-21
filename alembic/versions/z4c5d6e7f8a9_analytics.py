"""analytics: profile_views, search_logs, page_views

Revision ID: z4c5d6e7f8a9
Revises: y3b4c5d6e7f8
Create Date: 2026-06-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "z4c5d6e7f8a9"
down_revision = "y3b4c5d6e7f8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "profile_views",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("viewer_ip_hash", sa.String(64), nullable=True),
        sa.Column("viewer_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("viewed_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_pv_entity_date", "profile_views", ["entity_type", "entity_id", "viewed_at"])
    op.create_index("idx_pv_date", "profile_views", ["viewed_at"])

    op.create_table(
        "search_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("query", sa.String(200), nullable=True),
        sa.Column("specialty", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("entity_type", sa.String(20), nullable=True),
        sa.Column("result_count", sa.Integer, default=0),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("searched_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_sl_date", "search_logs", ["searched_at"])
    op.create_index("idx_sl_specialty", "search_logs", ["specialty"])
    op.create_index("idx_sl_city", "search_logs", ["city"])

    op.create_table(
        "page_views",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("occurred_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_pgv_date", "page_views", ["occurred_at"])
    op.create_index("idx_pgv_ip_date", "page_views", ["ip_hash", "occurred_at"])


def downgrade():
    op.drop_table("page_views")
    op.drop_table("search_logs")
    op.drop_table("profile_views")

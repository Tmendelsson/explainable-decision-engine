"""add correlation_id and enriched_data to decisions

Revision ID: 002
Revises: 001
Create Date: 2026-03-31
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "decisions",
        sa.Column("correlation_id", sa.String(36), nullable=True),
    )
    op.add_column(
        "decisions",
        sa.Column("enriched_data", sa.JSON(), nullable=True),
    )
    op.create_index("ix_decisions_correlation_id", "decisions", ["correlation_id"])


def downgrade() -> None:
    op.drop_index("ix_decisions_correlation_id", table_name="decisions")
    op.drop_column("decisions", "enriched_data")
    op.drop_column("decisions", "correlation_id")

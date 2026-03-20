"""add missing indexes on decisions and rules

Revision ID: 002
Revises: 001
Create Date: 2026-03-20
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # decisions — filter/sort columns used frequently
    op.create_index("ix_decisions_product", "decisions", ["product"])
    op.create_index("ix_decisions_status", "decisions", ["status"])
    op.create_index("ix_decisions_created_at", "decisions", ["created_at"])

    # rules — used in every active-rule lookup
    op.create_index("ix_rules_is_active", "rules", ["is_active"])
    op.create_index("ix_rules_product_type", "rules", ["product_type"])


def downgrade() -> None:
    op.drop_index("ix_rules_product_type", table_name="rules")
    op.drop_index("ix_rules_is_active", table_name="rules")
    op.drop_index("ix_decisions_created_at", table_name="decisions")
    op.drop_index("ix_decisions_status", table_name="decisions")
    op.drop_index("ix_decisions_product", table_name="decisions")

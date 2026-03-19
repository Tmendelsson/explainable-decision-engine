"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("field", sa.String(50), nullable=False),
        sa.Column("operator", sa.String(10), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("product_type", sa.String(50), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_rules_name", "rules", ["name"], unique=True)

    op.create_table(
        "decisions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("transaction_id", sa.String(36), nullable=False),
        sa.Column("cpf", sa.String(14), nullable=False),
        sa.Column("product", sa.String(100), nullable=False),
        sa.Column("monthly_income", sa.Float(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("credit_score", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("matched_rules", sa.JSON(), nullable=True),
        sa.Column("input_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_decisions_transaction_id", "decisions", ["transaction_id"], unique=True)
    op.create_index("ix_decisions_cpf", "decisions", ["cpf"])


def downgrade() -> None:
    op.drop_index("ix_decisions_cpf", table_name="decisions")
    op.drop_index("ix_decisions_transaction_id", table_name="decisions")
    op.drop_table("decisions")
    op.drop_index("ix_rules_name", table_name="rules")
    op.drop_table("rules")

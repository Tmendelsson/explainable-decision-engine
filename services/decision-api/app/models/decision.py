import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Decision(Base):
    __tablename__ = "decisions"
    __table_args__ = (
        Index("ix_decisions_product", "product"),
        Index("ix_decisions_status", "status"),
        Index("ix_decisions_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    transaction_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, default=lambda: str(uuid.uuid4())
    )
    # MVP 2: correlation_id links the full async chain
    correlation_id: Mapped[Optional[str]] = mapped_column(
        String(36), index=True, nullable=True
    )
    cpf: Mapped[str] = mapped_column(String(14), index=True, nullable=False)
    product: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    credit_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    matched_rules: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    # MVP 2: enriched signals stored for audit and explainability
    enriched_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

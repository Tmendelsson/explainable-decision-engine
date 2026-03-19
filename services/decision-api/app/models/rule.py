import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Campo do payload avaliado: monthly_income, age, credit_score
    field: Mapped[str] = mapped_column(String(50), nullable=False)

    # Operador: lt, gt, lte, gte, eq
    operator: Mapped[str] = mapped_column(String(10), nullable=False)

    # Valor de referência para comparação
    value: Mapped[float] = mapped_column(Float, nullable=False)

    # Ação disparada: deny, manual_review, flag
    action: Mapped[str] = mapped_column(String(20), nullable=False)

    # Penalidade subtraída do score base (100)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)

    # Regras de maior prioridade são avaliadas primeiro
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # None = aplicável a todos os produtos
    product_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

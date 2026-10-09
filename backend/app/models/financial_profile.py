import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class FinancialProfile(Base, TimestampMixin):
    __tablename__ = "financial_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    monthly_income: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    monthly_expenses: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    existing_debt_monthly_obligation: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    remaining_cash_flow: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    total_assets: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    total_liabilities: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2),
        nullable=True,
    )

    debt_service_coverage_ratio: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="SELF_DECLARED",
        nullable=False,
    )

    user = relationship(
        "User",
        lazy="joined",
    )

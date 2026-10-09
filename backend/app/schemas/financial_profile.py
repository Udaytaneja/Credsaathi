import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class FinancialProfileBase(BaseModel):
    monthly_income: Decimal
    monthly_expenses: Decimal
    existing_debt_monthly_obligation: Decimal = Decimal("0.00")
    remaining_cash_flow: Decimal
    total_assets: Decimal | None = None
    total_liabilities: Decimal | None = None
    debt_service_coverage_ratio: Decimal | None = None


class FinancialProfileCreate(FinancialProfileBase):
    pass


class FinancialProfileResponse(FinancialProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    verification_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

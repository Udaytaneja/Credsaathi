import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class LoanRequirementBase(BaseModel):
    purpose: str
    requested_amount: Decimal
    tenure_months: int
    preferred_interest_rate: Decimal | None = None
    collateral_available: bool = False
    collateral_type: str | None = None


class LoanRequirementCreate(LoanRequirementBase):
    pass


class LoanRequirementResponse(LoanRequirementBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

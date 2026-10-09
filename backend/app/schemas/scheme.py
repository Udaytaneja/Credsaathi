import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict


class SchemeBase(BaseModel):
    name: str
    code: str
    purpose: str
    description: str
    category: str | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    min_tenure_months: int | None = None
    max_tenure_months: int | None = None
    interest_rate_min: Decimal | None = None
    interest_rate_max: Decimal | None = None
    subsidy_percentage: Decimal | None = None
    required_documents: Any | None = None
    eligibility_criteria: dict[str, Any] | None = None
    source: str
    status: str = "ACTIVE"


class SchemeCreate(SchemeBase):
    pass


class SchemeResponse(SchemeBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

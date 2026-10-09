import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_APPLICATION_STATUSES = {
    "DRAFT",
    "SUBMITTED",
    "UNDER_REVIEW",
    "ADDITIONAL_INFO_REQUIRED",
    "ACCEPTED",
    "REJECTED",
    "CLOSED",
}

# Allowed status transitions matrix
ALLOWED_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"SUBMITTED", "CLOSED"},
    "SUBMITTED": {"UNDER_REVIEW", "ADDITIONAL_INFO_REQUIRED", "REJECTED", "CLOSED"},
    "UNDER_REVIEW": {"ADDITIONAL_INFO_REQUIRED", "ACCEPTED", "REJECTED", "CLOSED"},
    "ADDITIONAL_INFO_REQUIRED": {"SUBMITTED", "UNDER_REVIEW", "CLOSED"},
    "ACCEPTED": {"CLOSED"},
    "REJECTED": {"CLOSED"},
    "CLOSED": set(),
}


class ApplicationBase(BaseModel):
    scheme_id: uuid.UUID
    organization_id: uuid.UUID | None = None
    requested_amount: Decimal = Field(..., gt=0)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        upper_status = v.upper().strip()
        if upper_status not in VALID_APPLICATION_STATUSES:
            raise ValueError(
                f"Invalid application status '{v}'. Allowed statuses: {sorted(list(VALID_APPLICATION_STATUSES))}"
            )
        return upper_status


class ApplicationResponse(ApplicationBase):
    id: uuid.UUID
    application_number: str
    user_id: uuid.UUID
    status: str
    readiness_score: Decimal | None = None
    submitted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

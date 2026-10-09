import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApplicantProfileBase(BaseModel):
    entity_name: str | None = None
    udyam_registration_no: str | None = None
    category: str | None = None
    state: str | None = None
    district: str | None = None
    pincode: str | None = None


class ApplicantProfileCreate(ApplicantProfileBase):
    pass


class ApplicantProfileUpdate(ApplicantProfileBase):
    pass


class ApplicantProfileResponse(ApplicantProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    identity_verified: bool
    business_verified: bool
    financials_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

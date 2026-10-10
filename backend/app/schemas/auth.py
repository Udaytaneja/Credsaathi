import uuid
from typing import Any
from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(default="APPLICANT", description="Requested role: APPLICANT or BANKER")
    organization_id: uuid.UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def populate_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" not in data and "full_name" in data:
                data["name"] = data["full_name"]
        return data


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserSessionResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    organization: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSessionResponse

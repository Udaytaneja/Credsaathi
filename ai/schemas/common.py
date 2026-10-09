"""Common Pydantic base schemas, error representations, and response envelopes."""
import uuid
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ModelMetadata(BaseModel):
    """Metadata describing the AI/ML model or engine utilized for a request."""
    provider: str = Field(..., description="Provider name (e.g. OpenAI, Anthropic, CredSaathi-Internal)")
    model: str = Field(..., description="Model identifier or architecture name")
    version: str = Field(..., description="Version of the model or prompt template")


class ErrorDetail(BaseModel):
    """Structured error payload for AI service responses."""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")
    field: Optional[str] = Field(default=None, description="Request parameter or field that caused the error")


class ResponseEnvelope(BaseModel, Generic[T]):
    """Standard unified response wrapper for all AI API endpoints."""
    success: bool = Field(default=True, description="Indicates if request succeeded")
    data: Optional[T] = Field(default=None, description="Response payload data")
    model: Optional[ModelMetadata] = Field(default=None, description="Model metadata used for execution")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Correlation ID for tracking")
    errors: List[ErrorDetail] = Field(default_factory=list, description="List of error details if unsuccessful")

    @classmethod
    def success_response(
        cls,
        data: T,
        model_metadata: Optional[ModelMetadata] = None,
        request_id: Optional[str] = None,
    ) -> "ResponseEnvelope[T]":
        """Factory method for successful responses."""
        return cls(
            success=True,
            data=data,
            model=model_metadata,
            request_id=request_id or str(uuid.uuid4()),
            errors=[]
        )

    @classmethod
    def error_response(
        cls,
        errors: List[ErrorDetail],
        model_metadata: Optional[ModelMetadata] = None,
        request_id: Optional[str] = None,
    ) -> "ResponseEnvelope[None]":
        """Factory method for error responses."""
        return cls(
            success=False,
            data=None,
            model=model_metadata,
            request_id=request_id or str(uuid.uuid4()),
            errors=errors
        )

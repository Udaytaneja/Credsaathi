from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from ai.utils.logging import logger

if TYPE_CHECKING:
    from ai.schemas.common import ModelMetadata


class AIServiceException(Exception):
    """Base exception for all AI Service errors."""

    def __init__(
        self,
        message: str,
        code: str = "AI_SERVICE_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        field: Optional[str] = None,
        model_metadata: Optional[ModelMetadata] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field = field
        self.model_metadata = model_metadata


class AIModelException(AIServiceException):
    """Raised when an downstream AI model provider fails."""

    def __init__(self, message: str, model_metadata: Optional[ModelMetadata] = None):
        super().__init__(
            message=message,
            code="MODEL_EXECUTION_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            model_metadata=model_metadata,
        )


class AIValidationException(AIServiceException):
    """Raised when input validation fails for AI operations."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="INVALID_AI_INPUT",
            status_code=status.HTTP_400_BAD_REQUEST,
            field=field,
        )


class AIFirewallException(AIServiceException):
    """Raised when an agent tool invocation is blocked by the Agent Firewall."""

    def __init__(self, message: str, tool_name: Optional[str] = None):
        super().__init__(
            message=message,
            code="AGENT_FIREWALL_VIOLATION",
            status_code=status.HTTP_403_FORBIDDEN,
            field=tool_name,
        )


class AIGuardrailViolationException(AIServiceException):
    """Raised when an AI input or output fails security/compliance guardrails."""

    def __init__(self, message: str, guardrail_name: Optional[str] = None):
        super().__init__(
            message=message,
            code="GUARDRAIL_VIOLATION",
            status_code=status.HTTP_400_BAD_REQUEST,
            field=guardrail_name,
        )


class AIRateLimitException(AIServiceException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class AITimeoutException(AIServiceException):
    """Raised when processing times out."""

    def __init__(self, message: str = "AI operation timed out"):
        super().__init__(
            message=message,
            code="OPERATION_TIMEOUT",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


async def ai_service_exception_handler(request: Request, exc: AIServiceException) -> JSONResponse:
    """Global FastAPI handler converting AIServiceExceptions to standard ResponseEnvelope JSON."""
    from ai.schemas.common import ErrorDetail, ResponseEnvelope

    request_id = getattr(request.state, "request_id", None)
    logger.error(f"AIServiceException caught: [{exc.code}] {exc.message} (status: {exc.status_code})")

    error_detail = ErrorDetail(code=exc.code, message=exc.message, field=exc.field)
    envelope = ResponseEnvelope.error_response(
        errors=[error_detail],
        model_metadata=exc.model_metadata,
        request_id=request_id,
    )
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled server exceptions."""
    from ai.schemas.common import ErrorDetail, ResponseEnvelope

    request_id = getattr(request.state, "request_id", None)
    logger.exception(f"Unhandled exception encountered: {str(exc)}")

    error_detail = ErrorDetail(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred in the AI Service."
    )
    envelope = ResponseEnvelope.error_response(
        errors=[error_detail],
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=envelope.model_dump(),
    )

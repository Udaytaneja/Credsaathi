"""Health check endpoint for CredSaathi AI Layer."""
from typing import Dict
from fastapi import APIRouter, Request
from ai.configs.settings import settings
from ai.model_router.registry import model_registry
from ai.schemas.common import ResponseEnvelope

router = APIRouter()


@router.get("/health", response_model=ResponseEnvelope[Dict[str, str]])
async def get_health(request: Request):
    """Returns AI service health status and environment details."""
    request_id = getattr(request.state, "request_id", None)
    health_data = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0"
    }
    model_metadata = model_registry.get_metadata("default")
    return ResponseEnvelope.success_response(
        data=health_data,
        model_metadata=model_metadata,
        request_id=request_id
    )

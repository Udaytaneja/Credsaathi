"""Models inspection endpoint for CredSaathi AI Layer."""
from typing import List
from fastapi import APIRouter, Request
from ai.model_router.registry import ModelInfo, model_registry
from ai.schemas.common import ResponseEnvelope

router = APIRouter()


@router.get("/models", response_model=ResponseEnvelope[List[ModelInfo]])
async def get_registered_models(request: Request):
    """Returns list of active registered AI model engines and capabilities."""
    request_id = getattr(request.state, "request_id", None)
    models_list = model_registry.list_models()
    model_metadata = model_registry.get_metadata("default")

    return ResponseEnvelope.success_response(
        data=models_list,
        model_metadata=model_metadata,
        request_id=request_id
    )

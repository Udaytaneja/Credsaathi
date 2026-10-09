"""Gateway endpoints package."""
from ai.gateway.endpoints.assistant import router as assistant_router
from ai.gateway.endpoints.extraction import router as extraction_router
from ai.gateway.endpoints.financial import router as financial_router
from ai.gateway.endpoints.health import router as health_router
from ai.gateway.endpoints.matching import router as matching_router
from ai.gateway.endpoints.models import router as models_router

__all__ = [
    "health_router",
    "models_router",
    "matching_router",
    "extraction_router",
    "financial_router",
    "assistant_router",
]

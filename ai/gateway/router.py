"""API Gateway Router for CredSaathi AI Layer."""
from fastapi import APIRouter
from ai.gateway.endpoints import (
    assistant_router,
    extraction_router,
    financial_router,
    health_router,
    matching_router,
    models_router,
)

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(models_router, tags=["Models"])
api_router.include_router(matching_router, tags=["Scheme Matching"])
api_router.include_router(extraction_router, tags=["Document AI"])
api_router.include_router(financial_router, tags=["Financial Intelligence"])
api_router.include_router(assistant_router, tags=["RAG Assistant"])

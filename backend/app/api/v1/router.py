from fastapi import APIRouter

from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.assistant import router as assistant_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.financial import router as financial_router
from app.api.v1.endpoints.schemes import router as schemes_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(applications_router, prefix="/applications", tags=["Applications"])
api_v1_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_v1_router.include_router(schemes_router, prefix="/schemes", tags=["Schemes"])
api_v1_router.include_router(financial_router, prefix="/financial", tags=["Financial Engine"])
api_v1_router.include_router(assistant_router, prefix="/assistant", tags=["Saakshi Assistant"])

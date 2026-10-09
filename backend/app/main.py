from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Enforce production security check on startup
    settings.check_production_safety()
    yield

app = FastAPI(
    title=settings.app_name,
    description="Backend API for the CredSaathi financial platform",
    version=settings.app_version,
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API V1 Router
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "credsaathi-backend",
        "version": settings.app_version,
    }
"""CredSaathi AI Service main entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai.configs.settings import settings
from ai.gateway.errors import AIServiceException, ai_service_exception_handler, unhandled_exception_handler
from ai.gateway.middleware import CorrelationIdMiddleware, SimpleRateLimiterMiddleware
from ai.gateway.router import api_router
from ai.utils.logging import logger


def create_app() -> FastAPI:
    """FastAPI Application factory for CredSaathi AI Layer."""
    app = FastAPI(
        title=settings.SERVICE_NAME,
        description="Stateless AI Layer microservice for CredSaathi (Matching, Document AI, Financial Summaries, RAG)",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Configurable CORS Middleware setup
    origins = settings.cors_origins_list
    if not origins and settings.ENVIRONMENT == "development":
        origins = ["http://localhost:3000", "http://localhost:5173"]
    elif not origins:
        origins = []  # Strict empty list in production unless explicitly configured via AI_CORS_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # AI Middleware setup
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(SimpleRateLimiterMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

    # Exception Handlers setup
    app.add_exception_handler(AIServiceException, ai_service_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Include Gateway Router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    logger.info(f"{settings.SERVICE_NAME} initialized successfully.")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai.main:app", host="0.0.0.0", port=8001, reload=True)

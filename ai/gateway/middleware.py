"""Middleware for Correlation ID tracking, timeouts, and basic rate limiting."""
import time
import uuid
from typing import Callable, Dict
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from ai.configs.settings import settings
from ai.schemas.common import ErrorDetail, ResponseEnvelope
from ai.utils.logging import logger, request_id_ctx


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Injects and extracts X-Request-ID headers for request correlation tracking."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        token = request_id_ctx.set(request_id)

        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiter middleware for AI API endpoints."""

    def __init__(self, app, requests_per_minute: int = settings.RATE_LIMIT_PER_MINUTE):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.ip_store: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip health endpoints from rate limiting
        if request.url.path.endswith("/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60.0

        # Clean timestamps older than 60s
        timestamps = [ts for ts in self.ip_store.get(client_ip, []) if ts > window_start]

        if len(timestamps) >= self.requests_per_minute:
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            logger.warning(f"Rate limit exceeded for client IP: {client_ip}")
            error_detail = ErrorDetail(
                code="RATE_LIMIT_EXCEEDED",
                message=f"Rate limit of {self.requests_per_minute} requests/min exceeded."
            )
            envelope = ResponseEnvelope.error_response(errors=[error_detail], request_id=request_id)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=envelope.model_dump(),
                headers={"Retry-After": "60", "X-Request-ID": request_id}
            )

        timestamps.append(now)
        self.ip_store[client_ip] = timestamps
        return await call_next(request)

import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.support import router as support_router
from app.core.config import settings
from app.core.runtime import IdempotencyStore, RateLimiter, request_id_from_headers, safe_client_ip, trace_context

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Idempotency-Key", "X-Request-ID"],
)
app.include_router(health_router)
app.include_router(support_router)
app.state.rate_limiter = RateLimiter(
    limit=settings.rate_limit_requests, window_seconds=settings.rate_limit_window_seconds
)
app.state.idempotency_store = IdempotencyStore(ttl_seconds=settings.idempotency_ttl_seconds)
logger = logging.getLogger("soulcare.api")


def build_error_response(code: str, message: str, request_id: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": request_id}},
    )


@app.middleware("http")
async def request_controls_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    request.state.request_id = request_id_from_headers(request)
    request.state.client_ip = safe_client_ip(request)
    request.state.started_at = time.perf_counter()
    request.state.trace = trace_context(request)

    if request.method in {"POST", "PUT", "PATCH"}:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                parsed_length = int(content_length)
            except ValueError:
                parsed_length = settings.request_body_limit_bytes + 1
            if parsed_length > settings.request_body_limit_bytes:
                return build_error_response(
                    code="payload_too_large",
                    message="Request payload exceeds the configured size limit.",
                    request_id=request.state.request_id,
                    status_code=413,
                )

    if not app.state.rate_limiter.is_allowed(f"{request.state.client_ip}:{request.url.path}"):
        return build_error_response(
            code="rate_limited",
            message="Rate limit exceeded. Retry later.",
            request_id=request.state.request_id,
            status_code=429,
        )

    response = await call_next(request)
    duration_ms = round((time.perf_counter() - request.state.started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none';"
    logger.info(
        "request_completed",
        extra={
            "event": request.state.trace("request_completed")["event"],
            "request_id": request.state.request_id,
            "client_ip": request.state.client_ip,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return build_error_response(
        code="validation_error",
        message=f"Request validation failed: {exc.errors()[0]['msg']}",
        request_id=getattr(request.state, "request_id", "unknown"),
        status_code=422,
    )


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException) -> JSONResponse:
    message = str(exc.detail) if exc.detail else "Request failed."
    return build_error_response(
        code="request_failed",
        message=message,
        request_id=getattr(request.state, "request_id", "unknown"),
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, _: Exception) -> JSONResponse:
    return build_error_response(
        code="internal_error",
        message="Unexpected server error.",
        request_id=getattr(request.state, "request_id", "unknown"),
        status_code=500,
    )

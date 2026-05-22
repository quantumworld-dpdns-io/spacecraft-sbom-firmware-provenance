from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sbom_provenance.api.middleware import RateLimitMiddleware, SecurityHeadersMiddleware
from sbom_provenance.api.routes import (
    approval_router,
    firmware_router,
    health_router,
    provenance_router,
    sbom_router,
    search_router,
    security_router,
)
from sbom_provenance.config import get_settings
from sbom_provenance.core.database import db_manager
from sbom_provenance.core.logging import setup_logging

setup_logging()

_start_time: float = time.time()


@asynccontextmanager
async def lifespan(app: FastApplication) -> AsyncGenerator[None, None]:
    # Startup
    await db_manager.create_all()
    yield
    # Shutdown
    await db_manager.close()


class FastApplication(FastAPI):
    pass


def create_application() -> FastApplication:
    settings = get_settings()

    app = FastApplication(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting
    app.add_middleware(RateLimitMiddleware)

    # Routers
    app.include_router(health_router)
    app.include_router(sbom_router)
    app.include_router(firmware_router)
    app.include_router(provenance_router)
    app.include_router(approval_router)
    app.include_router(security_router)
    app.include_router(search_router)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )

    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start
        response.headers["X-Process-Time-Ms"] = str(round(elapsed * 1000, 2))
        return response

    return app


app = create_application()

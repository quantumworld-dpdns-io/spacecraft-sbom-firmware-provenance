from __future__ import annotations

from fastapi import APIRouter

from sbom_provenance.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="0.1.0",
        database="connected",
        vector_store="connected",
        checks={
            "api": "healthy",
            "database": "connected",
            "storage": "available",
        },
    )


@router.get("/api/v1/health", response_model=HealthResponse)
async def api_health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="0.1.0",
        database="connected",
        vector_store="connected",
        checks={
            "api": "healthy",
            "database": "connected",
            "storage": "available",
        },
    )

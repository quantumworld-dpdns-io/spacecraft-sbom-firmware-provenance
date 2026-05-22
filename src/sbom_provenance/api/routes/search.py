from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.core.database import get_db
from sbom_provenance.services.search_service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["Search"])


@router.get("", response_model=dict)
async def global_search(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = SearchService(db)
    result = await service.global_search(
        query=q,
        skip=(page - 1) * per_page,
        limit=per_page,
    )
    return result


@router.get("/sbom", response_model=dict)
async def search_sbom(
    q: str = Query(..., min_length=1, max_length=200),
    field: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = SearchService(db)
    items, total = await service.search_sbom(
        query=q,
        field=field,
        skip=(page - 1) * per_page,
        limit=per_page,
    )
    return {
        "query": q,
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/firmware", response_model=dict)
async def search_firmware(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = SearchService(db)
    items, total = await service.search_firmware(
        query=q,
        skip=(page - 1) * per_page,
        limit=per_page,
    )
    return {
        "query": q,
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }

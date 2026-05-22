from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.api.dependencies import require_role
from sbom_provenance.core.database import get_db
from sbom_provenance.schemas.provenance import ProvenanceChainCreate, ProvenanceChainResponse
from sbom_provenance.services.provenance_service import ProvenanceService

router = APIRouter(prefix="/api/v1/provenance", tags=["Provenance"])


@router.post("/chains", response_model=ProvenanceChainResponse, status_code=status.HTTP_201_CREATED)
async def create_provenance_chain(
    data: ProvenanceChainCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("editor")),
) -> Any:
    service = ProvenanceService(db)
    chain = await service.create_chain(data)
    return chain


@router.get("/chains", response_model=dict)
async def list_provenance_chains(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = ProvenanceService(db)
    items, total = await service.list_chains(
        skip=(page - 1) * per_page,
        limit=per_page,
    )
    return {
        "items": [ProvenanceChainResponse.model_validate(c) for c in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/chains/{chain_id}", response_model=ProvenanceChainResponse)
async def get_provenance_chain(
    chain_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = ProvenanceService(db)
    chain = await service.get_chain_by_id(chain_id)
    if not chain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provenance chain not found")
    return chain


@router.get("/trace/{target_type}/{target_id}", response_model=dict)
async def trace_provenance(
    target_type: str,
    target_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = ProvenanceService(db)
    trace = await service.trace(target_id, target_type)
    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No provenance trace found")
    return trace


@router.post("/chains/{chain_id}/verify", response_model=dict)
async def verify_provenance_chain(
    chain_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("reviewer")),
) -> Any:
    service = ProvenanceService(db)
    result = await service.verify_chain(chain_id)
    return result

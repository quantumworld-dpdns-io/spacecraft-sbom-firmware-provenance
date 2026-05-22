from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.api.dependencies import get_current_user, require_role
from sbom_provenance.core.database import get_db
from sbom_provenance.schemas.common import PaginatedResponse
from sbom_provenance.schemas.sbom import (
    SBOMDocumentCreate,
    SBOMDocumentResponse,
    SBOMDocumentUpdate,
    SBOMValidateRequest,
    SBOMValidateResponse,
)
from sbom_provenance.services.sbom_service import SBOMService
from sbom_provenance.utils.exporters import SBOMExporter

router = APIRouter(prefix="/api/v1/sbom", tags=["SBOM"])


@router.post("", response_model=SBOMDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_sbom(
    data: SBOMDocumentCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("editor")),
) -> Any:
    service = SBOMService(db)
    document = await service.create(data)
    return document


@router.get("", response_model=dict)
async def list_sboms(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str | None = Query(None),
    sort_order: str = Query("desc"),
    organization: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = SBOMService(db)
    items, total = await service.list(
        skip=(page - 1) * per_page,
        limit=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        organization=organization,
    )
    return {
        "items": [SBOMDocumentResponse.model_validate(doc) for doc in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/{document_id}", response_model=SBOMDocumentResponse)
async def get_sbom(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = SBOMService(db)
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SBOM document not found")
    return document


@router.patch("/{document_id}", response_model=SBOMDocumentResponse)
async def update_sbom(
    document_id: str,
    data: SBOMDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("editor")),
) -> Any:
    service = SBOMService(db)
    document = await service.update(document_id, data)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SBOM document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sbom(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("admin")),
) -> None:
    service = SBOMService(db)
    deleted = await service.delete(document_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SBOM document not found")


@router.post("/{document_id}/validate", response_model=dict)
async def validate_sbom(
    document_id: str,
    request: SBOMValidateRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = SBOMService(db)
    result = await service.validate(document_id, request.checks)
    return result


@router.get("/{document_id}/export")
async def export_sbom(
    document_id: str,
    fmt: str = Query("spdx", pattern=r"^(spdx|cyclonedx|json|xml)$"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = SBOMService(db)
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SBOM document not found")

    sbom_data = {
        "name": document.name,
        "version": document.version,
        "organization": document.organization,
        "packages": [
            {
                "spdx_id": p.spdx_id,
                "name": p.name,
                "version": p.version,
                "supplier": p.supplier,
                "download_location": p.download_location,
                "hashes": p.hashes,
                "license": p.license_concluded,
                "copyright": p.copyright_text,
                "purl": p.purl,
            }
            for p in (document.packages or [])
        ],
        "relationships": [],
        "dependencies": [],
    }
    return SBOMExporter.export_sbom(sbom_data, fmt)


@router.get("/stats/summary", response_model=dict)
async def sbom_statistics(
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = SBOMService(db)
    return await service.get_statistics()

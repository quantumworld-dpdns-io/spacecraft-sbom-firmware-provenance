from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.api.dependencies import get_current_user, require_role
from sbom_provenance.core.database import get_db
from sbom_provenance.schemas.vulnerability import (
    VulnerabilityCreate,
    VulnerabilityResponse,
    VulnerabilityScanCreate,
    VulnerabilityScanResponse,
)
from sbom_provenance.services.vulnerability_service import VulnerabilityService

router = APIRouter(prefix="/api/v1/security", tags=["Security"])


@router.post("/vulnerabilities", response_model=VulnerabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_vulnerability(
    data: VulnerabilityCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("editor")),
) -> Any:
    service = VulnerabilityService(db)
    vuln = await service.create_vulnerability(data)
    return vuln


@router.get("/vulnerabilities", response_model=dict)
async def list_vulnerabilities(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = VulnerabilityService(db)
    items, total = await service.list_vulnerabilities(
        skip=(page - 1) * per_page,
        limit=per_page,
        severity=severity,
        status=status,
    )
    return {
        "items": [VulnerabilityResponse.model_validate(v) for v in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/vulnerabilities/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vuln_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = VulnerabilityService(db)
    vuln = await service.get_vulnerability_by_id(vuln_id)
    if not vuln:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vulnerability not found")
    return vuln


@router.post("/scans", response_model=VulnerabilityScanResponse, status_code=status.HTTP_201_CREATED)
async def start_vulnerability_scan(
    data: VulnerabilityScanCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("editor")),
) -> Any:
    service = VulnerabilityService(db)
    scan = await service.start_scan(data)
    return scan


@router.get("/scans/{scan_id}", response_model=VulnerabilityScanResponse)
async def get_vulnerability_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = VulnerabilityService(db)
    scan = await service.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


@router.get("/stats/summary", response_model=dict)
async def security_statistics(
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = VulnerabilityService(db)
    return await service.get_statistics()

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.api.dependencies import get_current_user, require_role
from sbom_provenance.core.database import get_db
from sbom_provenance.schemas.firmware import (
    FirmwareHashVerify,
    FirmwareImageCreate,
    FirmwareImageResponse,
    FirmwareVerifyResponse,
)
from sbom_provenance.services.firmware_service import FirmwareService
from sbom_provenance.services.hash_service import HashService

router = APIRouter(prefix="/api/v1/firmware", tags=["Firmware"])


@router.post("", response_model=FirmwareImageResponse, status_code=status.HTTP_201_CREATED)
async def register_firmware(
    data: FirmwareImageCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("editor")),
) -> Any:
    service = FirmwareService(db)
    firmware = await service.register(data)
    return firmware


@router.get("", response_model=dict)
async def list_firmware(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    device: str | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = FirmwareService(db)
    items, total = await service.list(
        skip=(page - 1) * per_page,
        limit=per_page,
        device=device,
        status=status,
    )
    return {
        "items": [FirmwareImageResponse.model_validate(fw) for fw in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/{firmware_id}", response_model=FirmwareImageResponse)
async def get_firmware(
    firmware_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = FirmwareService(db)
    firmware = await service.get_by_id(firmware_id)
    if not firmware:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firmware not found")
    return firmware


@router.post("/{firmware_id}/verify", response_model=dict)
async def verify_firmware(
    firmware_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = FirmwareService(db)
    result = await service.verify(firmware_id)
    return result


@router.post("/hash/verify", response_model=dict)
async def verify_firmware_hash(
    request: FirmwareHashVerify,
    db: AsyncSession = Depends(get_db),
) -> Any:
    hash_service = HashService(db)
    result = await hash_service.verify_hash(
        firmware_id=request.firmware_id,
        expected_hash=request.expected_hash,
        algorithm=request.algorithm,
    )
    return result


@router.post("/hash/compute", response_model=dict)
async def compute_firmware_hash(
    data: dict,
    db: AsyncSession = Depends(get_db),
) -> Any:
    algorithm = data.get("algorithm", "sha256")
    raw_data = data.get("data", "")
    if isinstance(raw_data, str):
        raw_data = raw_data.encode()
    hash_service = HashService(db)
    result = await hash_service.compute_hash(raw_data, algorithm)
    return result


@router.get("/stats/summary", response_model=dict)
async def firmware_statistics(
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = FirmwareService(db)
    return await service.get_statistics()

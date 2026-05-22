from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.api.dependencies import get_current_user, require_role
from sbom_provenance.core.database import get_db
from sbom_provenance.schemas.approval import (
    ApprovalPolicyCreate,
    ApprovalPolicyResponse,
    ApprovalRequestCreate,
    ApprovalRequestResponse,
    ApprovalReviewAction,
)
from sbom_provenance.services.approval_service import ApprovalService

router = APIRouter(prefix="/api/v1/approvals", tags=["Approvals"])


@router.post("/requests", response_model=ApprovalRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_request(
    data: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    service = ApprovalService(db)
    requester = current_user.get("sub", "unknown")
    request = await service.create_request(data, requester)
    return request


@router.get("/requests", response_model=dict)
async def list_approval_requests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = ApprovalService(db)
    items, total = await service.list_requests(
        skip=(page - 1) * per_page,
        limit=per_page,
        status=status,
    )
    return {
        "items": [ApprovalRequestResponse.model_validate(r) for r in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/requests/{request_id}", response_model=ApprovalRequestResponse)
async def get_approval_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = ApprovalService(db)
    request = await service.get_request_by_id(request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
    return request


@router.post("/requests/{request_id}/review", response_model=ApprovalRequestResponse)
async def review_approval_request(
    request_id: str,
    action: ApprovalReviewAction,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    service = ApprovalService(db)
    reviewer = current_user.get("sub", "unknown")
    request = await service.review(request_id, action.action, reviewer, action.comment)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
    return request


@router.get("/requests/{request_id}/audit", response_model=dict)
async def get_approval_audit_log(
    request_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = ApprovalService(db)
    items, total = await service.get_audit_logs(
        approval_id=request_id,
        skip=(page - 1) * per_page,
        limit=per_page,
    )
    return {
        "items": [
            {
                "id": log.id,
                "action": log.action,
                "actor": log.actor,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
                "ip_address": log.ip_address,
            }
            for log in items
        ],
        "total": total,
    }


@router.post("/policies", response_model=ApprovalPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_policy(
    data: ApprovalPolicyCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_role("admin")),
) -> Any:
    service = ApprovalService(db)
    policy = await service.create_policy(data)
    return policy


@router.get("/policies", response_model=list[ApprovalPolicyResponse])
async def list_approval_policies(
    db: AsyncSession = Depends(get_db),
) -> Any:
    service = ApprovalService(db)
    policies = await service.list_policies()
    return policies

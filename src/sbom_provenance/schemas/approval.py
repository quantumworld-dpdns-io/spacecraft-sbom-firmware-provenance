from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ApprovalRequestCreate(BaseModel):
    request_type: str = Field(..., min_length=1, max_length=50)
    target_id: str = Field(..., min_length=1, max_length=36)
    target_type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    justification: str | None = None
    risk_assessment: dict[str, Any] | None = None
    priority: str = "medium"
    reviewers: list[str] | None = None
    metadata_json: dict[str, Any] | None = None


class ApprovalRequestResponse(BaseModel):
    id: str
    request_type: str
    target_id: str
    target_type: str
    requester: str
    reviewers: list[str] | None
    status: str
    priority: str
    title: str
    description: str | None
    justification: str | None
    risk_assessment: dict[str, Any] | None
    approved_by: str | None
    approved_at: datetime | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] | None

    class Config:
        from_attributes = True


class ApprovalReviewAction(BaseModel):
    action: str = Field(..., pattern=r"^(approve|reject|request_changes)$")
    comment: str | None = None


class ApprovalPolicyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    policy_type: str = Field(..., min_length=1, max_length=50)
    target_type: str = Field(..., min_length=1, max_length=50)
    rules: dict[str, Any]
    required_approvers: int = 1
    auto_approve: bool = False
    metadata_json: dict[str, Any] | None = None


class ApprovalPolicyResponse(BaseModel):
    id: str
    name: str
    description: str | None
    policy_type: str
    target_type: str
    rules: dict
    required_approvers: int
    auto_approve: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

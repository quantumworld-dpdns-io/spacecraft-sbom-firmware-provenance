from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.models.approval import ApprovalAuditLog, ApprovalPolicy, ApprovalRequest
from sbom_provenance.schemas.approval import ApprovalPolicyCreate, ApprovalRequestCreate


class ApprovalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_request(self, data: ApprovalRequestCreate, requester: str) -> ApprovalRequest:
        request = ApprovalRequest(
            request_type=data.request_type,
            target_id=data.target_id,
            target_type=data.target_type,
            requester=requester,
            title=data.title,
            description=data.description,
            justification=data.justification,
            risk_assessment=data.risk_assessment,
            priority=data.priority,
            reviewers=data.reviewers,
            metadata_json=data.metadata_json,
        )
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_request_by_id(self, request_id: str) -> ApprovalRequest | None:
        result = await self.session.execute(
            select(ApprovalRequest).where(ApprovalRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def list_requests(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
    ) -> tuple[list[ApprovalRequest], int]:
        query = select(ApprovalRequest)
        count_query = select(ApprovalRequest.id)
        if status:
            query = query.where(ApprovalRequest.status == status)
            count_query = count_query.where(ApprovalRequest.status == status)
        total_result = await self.session.execute(count_query)
        total = len(total_result.all())
        query = query.order_by(ApprovalRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def review(
        self,
        request_id: str,
        action: str,
        reviewer: str,
        comment: str | None = None,
    ) -> ApprovalRequest | None:
        request = await self.get_request_by_id(request_id)
        if not request:
            return None

        if action == "approve":
            request.status = "approved"
            request.approved_by = reviewer
            request.approved_at = datetime.now(UTC)
        elif action == "reject":
            request.status = "rejected"
            request.rejection_reason = comment
        elif action == "request_changes":
            request.status = "changes_requested"

        audit = ApprovalAuditLog(
            approval_id=request_id,
            action=action,
            actor=reviewer,
            details=comment,
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def create_policy(self, data: ApprovalPolicyCreate) -> ApprovalPolicy:
        policy = ApprovalPolicy(
            name=data.name,
            description=data.description,
            policy_type=data.policy_type,
            target_type=data.target_type,
            rules=data.rules,
            required_approvers=data.required_approvers,
            auto_approve=data.auto_approve,
            metadata_json=data.metadata_json,
        )
        self.session.add(policy)
        await self.session.commit()
        await self.session.refresh(policy)
        return policy

    async def list_policies(self) -> list[ApprovalPolicy]:
        result = await self.session.execute(
            select(ApprovalPolicy).where(ApprovalPolicy.is_active == True)
        )
        return list(result.scalars().all())

    async def get_audit_logs(
        self, approval_id: str, skip: int = 0, limit: int = 20
    ) -> tuple[list[ApprovalAuditLog], int]:
        query = (
            select(ApprovalAuditLog)
            .where(ApprovalAuditLog.approval_id == approval_id)
            .order_by(ApprovalAuditLog.created_at.desc())
        )
        count_query = select(ApprovalAuditLog.id).where(
            ApprovalAuditLog.approval_id == approval_id
        )
        total_result = await self.session.execute(count_query)
        total = len(total_result.all())
        result = await self.session.execute(query.offset(skip).limit(limit))
        items = list(result.scalars().all())
        return items, total

from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.models.firmware import FirmwareImage
from sbom_provenance.models.sbom import SBOMDocument


class SearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search_sbom(
        self,
        query: str,
        field: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        q = select(SBOMDocument)
        count_q = select(SBOMDocument.id)

        search_pattern = f"%{query}%"

        if field == "name":
            q = q.where(SBOMDocument.name.ilike(search_pattern))
            count_q = count_q.where(SBOMDocument.name.ilike(search_pattern))
        elif field == "organization":
            q = q.where(SBOMDocument.organization.ilike(search_pattern))
            count_q = count_q.where(SBOMDocument.organization.ilike(search_pattern))
        else:
            q = q.where(
                or_(
                    SBOMDocument.name.ilike(search_pattern),
                    SBOMDocument.organization.ilike(search_pattern),
                    SBOMDocument.supplier.ilike(search_pattern),
                    SBOMDocument.creator.ilike(search_pattern),
                )
            )
            count_q = count_q.where(
                or_(
                    SBOMDocument.name.ilike(search_pattern),
                    SBOMDocument.organization.ilike(search_pattern),
                    SBOMDocument.supplier.ilike(search_pattern),
                    SBOMDocument.creator.ilike(search_pattern),
                )
            )

        total_result = await self.session.execute(count_q)
        total = len(total_result.all())
        q = q.order_by(SBOMDocument.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(q)
        docs = result.scalars().all()

        items = [
            {
                "id": d.id,
                "name": d.name,
                "version": d.version,
                "organization": d.organization,
                "format_type": d.format_type,
                "created_at": d.created_at.isoformat(),
                "is_verified": d.is_verified,
            }
            for d in docs
        ]
        return items, total

    async def search_firmware(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        search_pattern = f"%{query}%"
        q = select(FirmwareImage).where(
            or_(
                FirmwareImage.name.ilike(search_pattern),
                FirmwareImage.device.ilike(search_pattern),
                FirmwareImage.manufacturer.ilike(search_pattern),
                FirmwareImage.version.ilike(search_pattern),
            )
        )
        count_q = select(FirmwareImage.id).where(
            or_(
                FirmwareImage.name.ilike(search_pattern),
                FirmwareImage.device.ilike(search_pattern),
                FirmwareImage.manufacturer.ilike(search_pattern),
                FirmwareImage.version.ilike(search_pattern),
            )
        )
        total_result = await self.session.execute(count_q)
        total = len(total_result.all())
        q = q.order_by(FirmwareImage.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(q)
        fws = result.scalars().all()

        items = [
            {
                "id": f.id,
                "name": f.name,
                "version": f.version,
                "device": f.device,
                "manufacturer": f.manufacturer,
                "status": f.status,
                "is_approved": f.is_approved,
                "created_at": f.created_at.isoformat(),
            }
            for f in fws
        ]
        return items, total

    async def global_search(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> dict[str, Any]:
        sbom_items, sbom_total = await self.search_sbom(query, skip=skip, limit=limit)
        fw_items, fw_total = await self.search_firmware(query, skip=skip, limit=limit)

        return {
            "query": query,
            "results": {
                "sbom_documents": {"items": sbom_items, "total": sbom_total},
                "firmware_images": {"items": fw_items, "total": fw_total},
            },
            "total_results": sbom_total + fw_total,
        }

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.models.sbom import SBOMDocument, SBOMPackage, SBOMRelationship
from sbom_provenance.schemas.sbom import SBOMDocumentCreate, SBOMDocumentUpdate


class SBOMService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: SBOMDocumentCreate) -> SBOMDocument:
        document = SBOMDocument(
            name=data.name,
            version=data.version,
            spec_version=data.spec_version,
            format_type=data.format_type,
            organization=data.organization,
            supplier=data.supplier,
            creator=data.creator,
            metadata_json=data.metadata_json,
        )
        self.session.add(document)
        await self.session.flush()

        for pkg_data in data.packages:
            package = SBOMPackage(
                document_id=document.id,
                spdx_id=pkg_data.spdx_id,
                name=pkg_data.name,
                version=pkg_data.version,
                supplier=pkg_data.supplier,
                download_location=pkg_data.download_location,
                license_declared=pkg_data.license_declared,
                license_concluded=pkg_data.license_concluded,
                copyright_text=pkg_data.copyright_text,
                package_type=pkg_data.package_type,
                purl=pkg_data.purl,
                cpe=pkg_data.cpe,
                description=pkg_data.description,
                hashes=pkg_data.hashes,
                metadata_json=pkg_data.metadata_json,
            )
            self.session.add(package)

        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, document_id: str) -> SBOMDocument | None:
        result = await self.session.execute(
            select(SBOMDocument).where(SBOMDocument.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: str | None = None,
        sort_order: str = "desc",
        **filters: Any,
    ) -> tuple[list[SBOMDocument], int]:
        query = select(SBOMDocument)
        count_query = select(SBOMDocument.id)

        for field, value in filters.items():
            if hasattr(SBOMDocument, field) and value is not None:
                column = getattr(SBOMDocument, field)
                query = query.where(column == value)
                count_query = count_query.where(column == value)

        total_result = await self.session.execute(count_query)
        total = len(total_result.all())

        if sort_by and hasattr(SBOMDocument, sort_by):
            sort_col = getattr(SBOMDocument, sort_by)
            query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())
        else:
            query = query.order_by(SBOMDocument.created_at.desc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def update(self, document_id: str, data: SBOMDocumentUpdate) -> SBOMDocument | None:
        document = await self.get_by_id(document_id)
        if not document:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def delete(self, document_id: str) -> bool:
        document = await self.get_by_id(document_id)
        if not document:
            return False
        await self.session.delete(document)
        await self.session.commit()
        return True

    async def validate(self, document_id: str, checks: list[str]) -> dict:
        document = await self.get_by_id(document_id)
        if not document:
            return {"is_valid": False, "errors": [{"field": "id", "message": "Document not found"}], "warnings": [], "checks_passed": 0, "checks_failed": 1}

        errors = []
        warnings = []

        if "schema" in checks:
            if not document.spec_version:
                errors.append({"field": "spec_version", "message": "Missing spec version"})
            if not document.packages:
                warnings.append({"field": "packages", "message": "Document has no packages"})

        if "hashes" in checks:
            for pkg in document.packages:
                if not pkg.hashes:
                    warnings.append({"field": f"package.{pkg.spdx_id}", "message": "Package has no hashes"})

        if "duplicates" in checks:
            seen = set()
            for pkg in document.packages:
                if pkg.spdx_id in seen:
                    errors.append({"field": f"package.{pkg.spdx_id}", "message": "Duplicate SPDX ID"})
                seen.add(pkg.spdx_id)

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "checks_passed": len(checks) - len(errors),
            "checks_failed": len(errors),
        }

    async def get_statistics(self) -> dict[str, Any]:
        result = await self.session.execute(select(SBOMDocument))
        documents = result.scalars().all()
        total_packages = 0
        format_counts: dict[str, int] = {}
        for doc in documents:
            total_packages += len(doc.packages) if doc.packages else 0
            fmt = doc.format_type or "unknown"
            format_counts[fmt] = format_counts.get(fmt, 0) + 1
        return {
            "total_documents": len(documents),
            "total_packages": total_packages,
            "verified_documents": sum(1 for d in documents if d.is_verified),
            "format_distribution": format_counts,
        }

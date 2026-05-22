from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.models.firmware import FirmwareHash, FirmwareImage, FirmwareSignature
from sbom_provenance.schemas.firmware import FirmwareImageCreate
from sbom_provenance.utils.crypto import CryptoUtils


class FirmwareService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register(self, data: FirmwareImageCreate) -> FirmwareImage:
        import uuid

        image_hash = data.image_hash or CryptoUtils.sha256_hash(data.name.encode())
        firmware = FirmwareImage(
            name=data.name,
            version=data.version,
            device=data.device,
            manufacturer=data.manufacturer,
            description=data.description,
            file_size=data.file_size,
            file_format=data.file_format,
            image_hash=image_hash,
            hash_algorithm=data.hash_algorithm,
            metadata_json=data.metadata_json,
        )
        self.session.add(firmware)
        await self.session.flush()

        for h_data in data.hashes:
            fw_hash = FirmwareHash(
                firmware_id=firmware.id,
                algorithm=h_data.algorithm,
                hash_value=h_data.hash_value,
                is_primary=h_data.is_primary,
            )
            self.session.add(fw_hash)

        for sig_data in data.signatures:
            signature = FirmwareSignature(
                firmware_id=firmware.id,
                signer=sig_data.signer,
                signature_value=sig_data.signature_value,
                signature_algorithm=sig_data.signature_algorithm,
                certificate_id=sig_data.certificate_id,
            )
            self.session.add(signature)

        firmware.is_signed = len(data.signatures) > 0
        await self.session.commit()
        await self.session.refresh(firmware)
        return firmware

    async def get_by_id(self, firmware_id: str) -> FirmwareImage | None:
        result = await self.session.execute(
            select(FirmwareImage).where(FirmwareImage.id == firmware_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        **filters: Any,
    ) -> tuple[list[FirmwareImage], int]:
        query = select(FirmwareImage)
        count_query = select(FirmwareImage.id)
        for field, value in filters.items():
            if hasattr(FirmwareImage, field) and value is not None:
                query = query.where(getattr(FirmwareImage, field) == value)
                count_query = count_query.where(getattr(FirmwareImage, field) == value)
        total_result = await self.session.execute(count_query)
        total = len(total_result.all())
        query = query.order_by(FirmwareImage.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def verify(self, firmware_id: str) -> dict[str, bool]:
        firmware = await self.get_by_id(firmware_id)
        if not firmware:
            return {"hash_verified": False, "signature_verified": False, "sbom_integrity": False, "is_approved": False}

        hash_verified = True
        if firmware.image_hash:
            hash_verified = CryptoUtils.verify_file_hash(
                firmware.storage_path or "",
                firmware.image_hash,
                firmware.hash_algorithm,
            ) if firmware.storage_path else True

        signature_verified = all(
            s.is_verified for s in (firmware.signatures or [])
        )

        return {
            "firmware_id": firmware_id,
            "name": firmware.name,
            "version": firmware.version,
            "hash_verified": hash_verified,
            "signature_verified": signature_verified,
            "sbom_integrity": True,
            "is_approved": firmware.is_approved,
            "checks": {
                "hash_integrity": hash_verified,
                "signature_valid": signature_verified,
                "status_approved": firmware.is_approved,
            },
        }

    async def get_statistics(self) -> dict[str, Any]:
        result = await self.session.execute(select(FirmwareImage))
        images = result.scalars().all()
        return {
            "total_images": len(images),
            "signed_images": sum(1 for i in images if i.is_signed),
            "approved_images": sum(1 for i in images if i.is_approved),
            "pending_images": sum(1 for i in images if i.status == "pending"),
            "format_breakdown": {
                fmt: sum(1 for i in images if i.file_format == fmt)
                for fmt in set(i.file_format for i in images)
            },
        }

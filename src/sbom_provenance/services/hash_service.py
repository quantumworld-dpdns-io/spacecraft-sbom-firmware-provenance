from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sbom_provenance.models.firmware import FirmwareHash, FirmwareImage
from sbom_provenance.utils.crypto import CryptoUtils


class HashService:
    SUPPORTED_ALGORITHMS = {"sha256", "sha384", "sha512", "blake2b"}

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def compute_hash(
        self, data: bytes, algorithm: str = "sha256"
    ) -> dict:
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Use one of {self.SUPPORTED_ALGORITHMS}")
        result = CryptoUtils.generate_firmware_digest(data, algorithm)
        return {
            "algorithm": algorithm,
            "hex_digest": result["hex_digest"],
            "size_bytes": result["size_bytes"],
            "computed_at": datetime.now(UTC).isoformat(),
        }

    async def verify_hash(
        self, firmware_id: str, expected_hash: str, algorithm: str = "sha256"
    ) -> dict:
        result = await self.session.execute(
            select(FirmwareImage).where(FirmwareImage.id == firmware_id)
        )
        firmware = result.scalar_one_or_none()
        if not firmware:
            return {
                "verified": False,
                "error": "Firmware not found",
                "firmware_id": firmware_id,
            }

        stored_hash = firmware.image_hash
        match = stored_hash.lower() == expected_hash.lower()

        if match:
            firmware.status = "verified"
        else:
            firmware.status = "hash_mismatch"

        fw_hash = FirmwareHash(
            firmware_id=firmware_id,
            algorithm=algorithm,
            hash_value=expected_hash,
            is_primary=True,
        )
        self.session.add(fw_hash)
        await self.session.commit()

        return {
            "firmware_id": firmware_id,
            "algorithm": algorithm,
            "computed_hash": stored_hash,
            "expected_hash": expected_hash,
            "match": match,
            "verified_at": datetime.now(UTC).isoformat(),
        }

    async def get_hash_history(self, firmware_id: str) -> list[dict]:
        result = await self.session.execute(
            select(FirmwareHash)
            .where(FirmwareHash.firmware_id == firmware_id)
            .order_by(FirmwareHash.created_at.desc())
        )
        hashes = result.scalars().all()
        return [
            {
                "id": h.id,
                "algorithm": h.algorithm,
                "hash_value": h.hash_value,
                "is_primary": h.is_primary,
                "created_at": h.created_at.isoformat(),
            }
            for h in hashes
        ]

    async def bulk_verify(
        self, firmware_ids: list[str], expected_hashes: dict[str, str]
    ) -> list[dict]:
        results = []
        for fw_id in firmware_ids:
            expected = expected_hashes.get(fw_id)
            if expected:
                result = await self.verify_hash(fw_id, expected)
                results.append(result)
        return results

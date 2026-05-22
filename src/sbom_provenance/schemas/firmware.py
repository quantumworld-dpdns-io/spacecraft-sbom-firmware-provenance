from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class FirmwareHashCreate(BaseModel):
    algorithm: str = Field(default="sha256", pattern=r"^(sha256|sha384|sha512|blake2b)$")
    hash_value: str = Field(..., min_length=32, max_length=128)
    is_primary: bool = False


class FirmwareSignatureCreate(BaseModel):
    signer: str = Field(..., min_length=1, max_length=255)
    signature_value: str = Field(..., min_length=1)
    signature_algorithm: str = Field(..., pattern=r"^(rsa|ecdsa|ed25519|hmac)-\w+$")
    certificate_id: str | None = None


class FirmwareImageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    device: str = Field(..., min_length=1, max_length=255)
    manufacturer: str | None = None
    description: str | None = None
    file_size: int | None = None
    file_format: str = "bin"
    image_hash: str | None = None
    hash_algorithm: str = "sha256"
    metadata_json: dict[str, Any] | None = None
    hashes: list[FirmwareHashCreate] = Field(default_factory=list)
    signatures: list[FirmwareSignatureCreate] = Field(default_factory=list)


class FirmwareImageResponse(BaseModel):
    id: str
    name: str
    version: str
    device: str
    manufacturer: str | None
    description: str | None
    file_size: int | None
    file_format: str
    image_hash: str
    hash_algorithm: str
    status: str
    sbom_document_id: str | None
    storage_path: str | None
    metadata_json: dict[str, Any] | None
    is_signed: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    hashes: list[dict] = Field(default_factory=list)
    signatures: list[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True


class FirmwareHashVerify(BaseModel):
    firmware_id: str
    expected_hash: str
    algorithm: str = "sha256"


class FirmwareHashResponse(BaseModel):
    firmware_id: str
    algorithm: str
    computed_hash: str
    expected_hash: str
    match: bool
    verified_at: str


class FirmwareVerifyResponse(BaseModel):
    firmware_id: str
    name: str
    version: str
    hash_verified: bool
    signature_verified: bool
    sbom_integrity: bool
    is_approved: bool
    checks: dict[str, bool]

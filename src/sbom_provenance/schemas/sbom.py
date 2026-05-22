from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SBOMPackageCreate(BaseModel):
    spdx_id: str = Field(..., pattern=r"^SPDXRef-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=100)
    supplier: str | None = None
    download_location: str | None = None
    license_declared: str | None = None
    license_concluded: str | None = None
    copyright_text: str | None = None
    package_type: str = "library"
    purl: str | None = None
    cpe: str | None = None
    description: str | None = None
    hashes: dict[str, str] | None = None
    metadata_json: dict[str, Any] | None = None


class SBOMPackageResponse(BaseModel):
    id: str
    document_id: str
    spdx_id: str
    name: str
    version: str
    supplier: str | None
    download_location: str | None
    license_declared: str | None
    license_concluded: str | None
    copyright_text: str | None
    package_type: str
    purl: str | None
    cpe: str | None
    description: str | None
    hashes: dict[str, str] | None
    metadata_json: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True


class SBOMDocumentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    spec_version: str = "SPDX-2.3"
    format_type: str = "spdx"
    organization: str | None = None
    supplier: str | None = None
    creator: str | None = None
    metadata_json: dict[str, Any] | None = None
    packages: list[SBOMPackageCreate] = Field(default_factory=list)


class SBOMDocumentUpdate(BaseModel):
    name: str | None = None
    version: str | None = None
    organization: str | None = None
    supplier: str | None = None
    metadata_json: dict[str, Any] | None = None
    signature: str | None = None


class SBOMDocumentResponse(BaseModel):
    id: str
    name: str
    version: str
    spec_version: str
    format_type: str
    organization: str | None
    supplier: str | None
    creator: str | None
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] | None
    signature: str | None
    is_verified: bool
    document_hash: str | None
    packages: list[SBOMPackageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SBOMValidateRequest(BaseModel):
    document_id: str
    checks: list[str] = Field(default=["schema", "hashes", "duplicates", "licenses"])


class SBOMValidateResponse(BaseModel):
    is_valid: bool
    errors: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0

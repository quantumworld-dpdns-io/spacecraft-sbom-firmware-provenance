from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ProvenanceNodeCreate(BaseModel):
    node_type: str = Field(..., min_length=1, max_length=50)
    entity_name: str = Field(..., min_length=1, max_length=255)
    entity_type: str = Field(..., min_length=1, max_length=50)
    entity_id: str = Field(..., min_length=1, max_length=36)
    action: str = Field(..., min_length=1, max_length=100)
    signer: str | None = None
    signature: str | None = None
    metadata_json: dict[str, Any] | None = None
    parent_id: str | None = None


class ProvenanceAttestationCreate(BaseModel):
    attestation_type: str = Field(..., min_length=1, max_length=100)
    predicate_type: str = Field(..., min_length=1, max_length=255)
    subject: dict[str, Any]
    predicate: dict[str, Any]
    issuer: str = Field(..., min_length=1, max_length=255)
    expires_at: datetime | None = None
    signature: str | None = None


class ProvenanceChainCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    target_type: str = Field(..., min_length=1, max_length=50)
    target_id: str = Field(..., min_length=1, max_length=36)
    metadata_json: dict[str, Any] | None = None
    nodes: list[ProvenanceNodeCreate] = Field(default_factory=list)
    attestations: list[ProvenanceAttestationCreate] = Field(default_factory=list)


class ProvenanceChainResponse(BaseModel):
    id: str
    name: str
    description: str | None
    target_type: str
    target_id: str
    is_complete: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    metadata_json: dict[str, Any] | None
    nodes: list[dict] = Field(default_factory=list)
    attestations: list[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ProvenanceTraceResponse(BaseModel):
    chain_id: str
    target_id: str
    target_type: str
    path: list[dict[str, Any]]
    depth: int
    is_complete: bool
    total_verifications: int
    passed_verifications: int
    failed_verifications: int

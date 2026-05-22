from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sbom_provenance.core.database import Base


class ProvenanceChain(Base):
    __tablename__ = "provenance_chains"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    is_complete: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    nodes: Mapped[list["ProvenanceNode"]] = relationship(
        "ProvenanceNode", back_populates="chain", cascade="all, delete-orphan"
    )
    attestations: Mapped[list["ProvenanceAttestation"]] = relationship(
        "ProvenanceAttestation", back_populates="chain", cascade="all, delete-orphan"
    )


class ProvenanceNode(Base):
    __tablename__ = "provenance_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chain_id: Mapped[str] = mapped_column(String(36), ForeignKey("provenance_chains.id"), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    signer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    hash_value: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)

    chain: Mapped["ProvenanceChain"] = relationship("ProvenanceChain", back_populates="nodes")


class ProvenanceAttestation(Base):
    __tablename__ = "provenance_attestations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chain_id: Mapped[str] = mapped_column(String(36), ForeignKey("provenance_chains.id"), nullable=False)
    attestation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    predicate_type: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[dict] = mapped_column(JSONB, nullable=False)
    predicate: Mapped[dict] = mapped_column(JSONB, nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    chain: Mapped["ProvenanceChain"] = relationship("ProvenanceChain", back_populates="attestations")

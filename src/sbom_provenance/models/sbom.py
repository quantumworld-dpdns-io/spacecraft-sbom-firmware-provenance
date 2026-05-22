from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sbom_provenance.core.database import Base


class SBOMDocument(Base):
    __tablename__ = "sbom_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    spec_version: Mapped[str] = mapped_column(String(20), default="SPDX-2.3")
    format_type: Mapped[str] = mapped_column(String(20), default="spdx")
    organization: Mapped[str] = mapped_column(String(255), nullable=True)
    supplier: Mapped[str] = mapped_column(String(255), nullable=True)
    creator: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    document_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    packages: Mapped[list["SBOMPackage"]] = relationship(
        "SBOMPackage", back_populates="document", cascade="all, delete-orphan"
    )
    relationships: Mapped[list["SBOMRelationship"]] = relationship(
        "SBOMRelationship", back_populates="document", cascade="all, delete-orphan"
    )


class SBOMPackage(Base):
    __tablename__ = "sbom_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("sbom_documents.id"), nullable=False)
    spdx_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    supplier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    download_location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    license_declared: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    license_concluded: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    copyright_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    package_type: Mapped[str] = mapped_column(String(50), default="library")
    purl: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cpe: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hashes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["SBOMDocument"] = relationship("SBOMDocument", back_populates="packages")


class SBOMRelationship(Base):
    __tablename__ = "sbom_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("sbom_documents.id"), nullable=False)
    source_element: Mapped[str] = mapped_column(String(255), nullable=False)
    target_element: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False, default="DEPENDS_ON")
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    document: Mapped["SBOMDocument"] = relationship("SBOMDocument", back_populates="relationships")

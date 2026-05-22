from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sbom_provenance.core.database import Base


class FirmwareImage(Base):
    __tablename__ = "firmware_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    device: Mapped[str] = mapped_column(String(255), nullable=False)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    file_format: Mapped[str] = mapped_column(String(20), default="bin")
    image_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    hash_algorithm: Mapped[str] = mapped_column(String(20), default="sha256")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sbom_document_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("sbom_documents.id"), nullable=True)
    storage_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_signed: Mapped[bool] = mapped_column(default=False)
    is_approved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    hashes: Mapped[list["FirmwareHash"]] = relationship(
        "FirmwareHash", back_populates="firmware", cascade="all, delete-orphan"
    )
    signatures: Mapped[list["FirmwareSignature"]] = relationship(
        "FirmwareSignature", back_populates="firmware", cascade="all, delete-orphan"
    )


class FirmwareHash(Base):
    __tablename__ = "firmware_hashes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firmware_id: Mapped[str] = mapped_column(String(36), ForeignKey("firmware_images.id"), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(20), nullable=False)
    hash_value: Mapped[str] = mapped_column(String(128), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    firmware: Mapped["FirmwareImage"] = relationship("FirmwareImage", back_populates="hashes")


class FirmwareSignature(Base):
    __tablename__ = "firmware_signatures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firmware_id: Mapped[str] = mapped_column(String(36), ForeignKey("firmware_images.id"), nullable=False)
    signer: Mapped[str] = mapped_column(String(255), nullable=False)
    signature_value: Mapped[str] = mapped_column(Text, nullable=False)
    signature_algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    certificate_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    verification_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    firmware: Mapped["FirmwareImage"] = relationship("FirmwareImage", back_populates="signatures")

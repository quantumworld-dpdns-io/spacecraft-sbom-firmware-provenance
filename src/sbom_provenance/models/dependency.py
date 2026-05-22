from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sbom_provenance.core.database import Base


class DependencyGraph(Base):
    __tablename__ = "dependency_graphs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    root_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_resolved: Mapped[bool] = mapped_column(default=False)
    depth: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    edges: Mapped[list["DependencyEdge"]] = relationship(
        "DependencyEdge", back_populates="graph", cascade="all, delete-orphan"
    )


class DependencyEdge(Base):
    __tablename__ = "dependency_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    graph_id: Mapped[str] = mapped_column(String(36), ForeignKey("dependency_graphs.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(100), default="depends_on")
    is_optional: Mapped[bool] = mapped_column(default=False)
    version_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    graph: Mapped["DependencyGraph"] = relationship("DependencyGraph", back_populates="edges")

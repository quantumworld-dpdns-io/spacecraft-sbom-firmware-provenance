from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sbom_provenance.models.provenance import ProvenanceAttestation, ProvenanceChain, ProvenanceNode
from sbom_provenance.schemas.provenance import ProvenanceChainCreate


class ProvenanceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_chain(self, data: ProvenanceChainCreate) -> ProvenanceChain:
        chain = ProvenanceChain(
            name=data.name,
            description=data.description,
            target_type=data.target_type,
            target_id=data.target_id,
            metadata_json=data.metadata_json,
        )
        self.session.add(chain)
        await self.session.flush()

        for node_data in data.nodes:
            node = ProvenanceNode(
                chain_id=chain.id,
                parent_id=node_data.parent_id,
                node_type=node_data.node_type,
                entity_name=node_data.entity_name,
                entity_type=node_data.entity_type,
                entity_id=node_data.entity_id,
                action=node_data.action,
                signer=node_data.signer,
                signature=node_data.signature,
                metadata_json=node_data.metadata_json,
            )
            self.session.add(node)

        for att_data in data.attestations:
            attestation = ProvenanceAttestation(
                chain_id=chain.id,
                attestation_type=att_data.attestation_type,
                predicate_type=att_data.predicate_type,
                subject=att_data.subject,
                predicate=att_data.predicate,
                issuer=att_data.issuer,
                expires_at=att_data.expires_at,
                signature=att_data.signature,
            )
            self.session.add(attestation)

        await self.session.commit()
        await self.session.refresh(chain)
        return chain

    async def get_chain_by_id(self, chain_id: str) -> ProvenanceChain | None:
        result = await self.session.execute(
            select(ProvenanceChain)
            .where(ProvenanceChain.id == chain_id)
            .options(
                selectinload(ProvenanceChain.nodes),
                selectinload(ProvenanceChain.attestations),
            )
        )
        return result.scalar_one_or_none()

    async def trace(self, target_id: str, target_type: str) -> dict[str, Any] | None:
        result = await self.session.execute(
            select(ProvenanceChain).where(
                ProvenanceChain.target_id == target_id,
                ProvenanceChain.target_type == target_type,
            )
        )
        chain = result.scalar_one_or_none()
        if not chain:
            return None

        # Build path from nodes
        nodes = chain.nodes or []
        path = sorted(
            [
                {
                    "node_id": n.id,
                    "entity_name": n.entity_name,
                    "entity_type": n.entity_type,
                    "action": n.action,
                    "timestamp": n.timestamp.isoformat() if n.timestamp else None,
                    "signer": n.signer,
                }
                for n in nodes
            ],
            key=lambda x: x.get("timestamp", ""),
        )

        attestations = chain.attestations or []
        verified = sum(1 for a in attestations if a.is_verified)

        return {
            "chain_id": chain.id,
            "target_id": target_id,
            "target_type": target_type,
            "path": path,
            "depth": len(nodes),
            "is_complete": chain.is_complete,
            "total_verifications": len(attestations),
            "passed_verifications": verified,
            "failed_verifications": len(attestations) - verified,
        }

    async def list_chains(
        self, skip: int = 0, limit: int = 20
    ) -> tuple[list[ProvenanceChain], int]:
        query = select(ProvenanceChain).order_by(ProvenanceChain.created_at.desc())
        count_query = select(ProvenanceChain.id)
        total_result = await self.session.execute(count_query)
        total = len(total_result.all())
        result = await self.session.execute(query.offset(skip).limit(limit))
        items = list(result.scalars().all())
        return items, total

    async def verify_chain(self, chain_id: str) -> dict:
        chain = await self.get_chain_by_id(chain_id)
        if not chain:
            return {"verified": False, "reason": "Chain not found"}

        nodes = chain.nodes or []
        attestations = chain.attestations or []
        all_signed = all(n.signature is not None for n in nodes if n.signer)
        all_verified = all(a.is_verified for a in attestations)

        chain.is_verified = all_signed and all_verified
        chain.is_complete = len(nodes) > 0
        await self.session.commit()

        return {
            "verified": chain.is_verified,
            "complete": chain.is_complete,
            "node_count": len(nodes),
            "attestation_count": len(attestations),
            "all_nodes_signed": all_signed,
            "all_attestations_verified": all_verified,
        }

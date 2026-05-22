from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestProvenanceAPI:
    async def test_create_provenance_chain(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/provenance/chains",
            json={
                "name": "Test Provenance Chain",
                "target_type": "firmware",
                "target_id": "fw-001",
            },
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Provenance Chain"
        assert "id" in data

    async def test_get_provenance_chain(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/provenance/chains",
            json={"name": "Get Test Chain", "target_type": "firmware", "target_id": "fw-002"},
            headers={"X-API-Key": "test-key"},
        )
        chain_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/provenance/chains/{chain_id}",
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == chain_id

    async def test_verify_provenance_chain(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/provenance/chains",
            json={"name": "Verify Test", "target_type": "firmware", "target_id": "fw-003"},
            headers={"X-API-Key": "test-key"},
        )
        chain_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/v1/provenance/chains/{chain_id}/verify",
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "verified" in data
        assert "complete" in data

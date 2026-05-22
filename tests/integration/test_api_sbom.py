from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestSBOMAPI:
    async def test_create_sbom(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/sbom",
            json={"name": "Integration Test SBOM", "version": "1.0.0", "organization": "NASA"},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Integration Test SBOM"
        assert data["version"] == "1.0.0"
        assert data["organization"] == "NASA"
        assert "id" in data

    async def test_get_sbom(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/sbom",
            json={"name": "Get Test SBOM", "version": "1.0.0"},
            headers={"X-API-Key": "test-key"},
        )
        doc_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/sbom/{doc_id}",
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == doc_id

    async def test_list_sboms(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/sbom",
            params={"page": 1, "per_page": 10},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    async def test_delete_sbom(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/sbom",
            json={"name": "Delete Test", "version": "1.0.0"},
            headers={"X-API-Key": "test-key"},
        )
        doc_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/sbom/{doc_id}",
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 204

        get_resp = await client.get(
            f"/api/v1/sbom/{doc_id}",
            headers={"X-API-Key": "test-key"},
        )
        assert get_resp.status_code == 404

    async def test_sbom_statistics(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/sbom/stats/summary",
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_packages" in data

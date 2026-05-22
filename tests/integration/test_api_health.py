from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestHealthAPI:
    async def test_health_endpoint(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"
        assert "database" in data
        assert "vector_store" in data

    async def test_api_health_endpoint(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_health_returns_json(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.headers["content-type"].startswith("application/json")

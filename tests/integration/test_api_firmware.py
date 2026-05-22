from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestFirmwareAPI:
    async def test_register_firmware(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/firmware",
            json={
                "name": "OBC Firmware v2",
                "version": "2.1.0",
                "device": "OBC-750",
                "manufacturer": "SpaceX",
            },
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "OBC Firmware v2"
        assert data["device"] == "OBC-750"
        assert data["status"] == "pending"

    async def test_get_firmware(self, client: AsyncClient):
        create_resp = await client.post(
            "/api/v1/firmware",
            json={"name": "Get Test FW", "version": "1.0.0", "device": "ADCS-300"},
            headers={"X-API-Key": "test-key"},
        )
        fw_id = create_resp.json()["id"]

        response = await client.get(
            f"/api/v1/firmware/{fw_id}",
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == fw_id

    async def test_list_firmware(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/firmware",
            params={"page": 1, "per_page": 10},
            headers={"X-API-Key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

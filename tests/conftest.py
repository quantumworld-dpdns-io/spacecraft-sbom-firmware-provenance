from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sbom_provenance.config import Settings, get_settings
from sbom_provenance.core.database import Base, DatabaseManager


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    from sbom_provenance.main import create_application

    app = create_application()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        environment="test",
        database_url="sqlite+aiosqlite:///:memory:",
        secret_key="test-secret-key-for-testing-only-1234567890",
        debug=True,
    )


@pytest.fixture
def sbom_create_data() -> dict[str, Any]:
    return {
        "name": "Test SBOM",
        "version": "1.0.0",
        "organization": "NASA",
        "spec_version": "SPDX-2.3",
        "format_type": "spdx",
    }


@pytest.fixture
def firmware_create_data() -> dict[str, Any]:
    return {
        "name": "Test Firmware",
        "version": "2.1.0",
        "device": "OBC-750",
        "manufacturer": "SpaceX",
        "hash_algorithm": "sha256",
    }


@pytest.fixture
def provenance_chain_data() -> dict[str, Any]:
    return {
        "name": "Test chain",
        "target_type": "firmware",
        "target_id": "test-fw-001",
    }


@pytest.fixture
def approval_request_data() -> dict[str, Any]:
    return {
        "request_type": "deployment",
        "target_id": "test-fw-001",
        "target_type": "firmware",
        "title": "Test approval",
        "priority": "high",
    }

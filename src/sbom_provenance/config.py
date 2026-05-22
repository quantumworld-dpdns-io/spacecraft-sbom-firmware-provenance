from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Spacecraft SBOM & Firmware Provenance"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = Field(default="INFO")
    secret_key: str = Field(default="change-me-in-production", min_length=32)

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./sbom_provenance.db",
        description="Database connection URL",
    )
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: RedisDsn | None = Field(default=None)

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    api_allowed_origins: list[str] = Field(default=["http://localhost:3000"])
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default=["*"])
    cors_allow_headers: list[str] = Field(default=["*"])

    # Authentication
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    bcrypt_rounds: int = 12
    api_key_header: str = "X-API-Key"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # File Upload
    max_upload_size_mb: int = 100
    allowed_upload_extensions: list[str] = Field(
        default=[".json", ".spdx", ".cdx", ".xml", ".bin", ".hex", ".elf"]
    )

    # Vector Database
    vector_db_provider: Literal["chroma", "qdrant", "lancedb"] = "chroma"
    vector_db_url: str = "http://localhost:8001"
    vector_db_collection: str = "sbom_embeddings"
    embedding_dimension: int = 384

    # Security
    bcrypt_rounds: int = 12
    hsts_max_age: int = 31536000
    content_security_policy: str = "default-src 'self'"
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"

    # External Services
    nvd_api_key: str | None = Field(default=None)
    github_token: str | None = Field(default=None)

    # Storage
    storage_backend: Literal["local", "s3", "gcs"] = "local"
    storage_path: str = "./data/sbom_storage"
    s3_bucket: str | None = None
    s3_region: str | None = None

    @field_validator("secret_key", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v == "change-me-in-production" and os.environ.get("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()

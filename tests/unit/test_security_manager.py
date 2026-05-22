from __future__ import annotations

import pytest
from jose import jwt

from sbom_provenance.core.security import SecurityManager, get_security_manager


class TestSecurityManager:
    @pytest.fixture
    def security(self):
        return SecurityManager()

    def test_hash_password(self, security):
        password = "test-password-123"
        hashed = security.hash_password(password)
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self, security):
        password = "test-password-123"
        hashed = security.hash_password(password)
        assert security.verify_password(password, hashed)

    def test_verify_password_incorrect(self, security):
        password = "test-password-123"
        hashed = security.hash_password(password)
        assert not security.verify_password("wrong-password", hashed)

    def test_create_access_token(self, security):
        data = {"sub": "user-123", "role": "admin"}
        token = security.create_access_token(data)
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_create_refresh_token(self, security):
        data = {"sub": "user-123"}
        token = security.create_refresh_token(data)
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_decode_valid_token(self, security):
        data = {"sub": "user-123", "role": "admin"}
        token = security.create_access_token(data)
        decoded = security.decode_token(token)
        assert decoded["sub"] == "user-123"
        assert decoded["role"] == "admin"
        assert decoded["type"] == "access"

    def test_decode_invalid_token(self, security):
        with pytest.raises(ValueError, match="Invalid or expired token"):
            security.decode_token("invalid-token")

    def test_verify_access_token(self, security):
        data = {"sub": "user-123"}
        token = security.create_access_token(data)
        payload = security.verify_token(token, "access")
        assert payload["sub"] == "user-123"

    def test_verify_token_wrong_type(self, security):
        data = {"sub": "user-123"}
        token = security.create_access_token(data)
        with pytest.raises(ValueError, match="Invalid token type"):
            security.verify_token(token, "refresh")

    def test_generate_api_key(self, security):
        api_key = security.generate_api_key()
        assert api_key.startswith("sbom_")
        assert len(api_key) > 10

    def test_singleton(self):
        s1 = get_security_manager()
        s2 = get_security_manager()
        assert s1 is s2

    def test_access_token_contains_claims(self, security):
        data = {"sub": "user-456", "role": "editor"}
        token = security.create_access_token(data, expires_delta=None)
        decoded = security.decode_token(token)
        assert decoded["sub"] == "user-456"
        assert decoded["role"] == "editor"
        assert decoded["type"] == "access"
        assert "exp" in decoded

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import lru_cache

from jose import JWTError, jwt
from passlib.context import CryptContext

from sbom_provenance.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)


class SecurityManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.secret_key = self.settings.secret_key
        self.algorithm = self.settings.algorithm
        self.access_token_expire = self.settings.access_token_expire_minutes
        self.refresh_token_expire = self.settings.refresh_token_expire_days

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + (
            expires_delta or timedelta(minutes=self.access_token_expire)
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise ValueError("Invalid or expired token")

    def verify_token(self, token: str, expected_type: str = "access") -> dict:
        payload = self.decode_token(token)
        if payload.get("type") != expected_type:
            raise ValueError(f"Invalid token type, expected {expected_type}")
        return payload

    def generate_api_key(self) -> str:
        import secrets
        return f"sbom_{secrets.token_urlsafe(32)}"


@lru_cache
def get_security_manager() -> SecurityManager:
    return SecurityManager()

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path.startswith("/api/v1") and request.url.path != "/api/v1/health":
            auth_header = request.headers.get("Authorization")
            if not auth_header and not request.headers.get("X-API-Key"):
                pass  # Let route-level security handle it
        response = await call_next(request)
        return response

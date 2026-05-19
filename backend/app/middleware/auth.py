# backend/app/middleware/auth.py
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import decode_token, extract_bearer_token
from app.utils.exceptions import AuthenticationError


class OptionalAuthMiddleware(BaseHTTPMiddleware):
    """Decode a bearer token when present and attach claims for logs/handlers."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                token = extract_bearer_token(authorization)
                request.state.jwt_claims = decode_token(token)
            except AuthenticationError:
                request.state.jwt_claims = None
        return await call_next(request)

# backend/app/utils/exceptions.py
from http import HTTPStatus


class AppError(Exception):
    """Base exception mapped to the API envelope error shape."""

    def __init__(self, message: str, status_code: int = HTTPStatus.BAD_REQUEST, code: str = "app_error") -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class AuthenticationError(AppError):
    """Raised when a request cannot be authenticated."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, HTTPStatus.UNAUTHORIZED, "authentication_error")


class AuthorizationError(AppError):
    """Raised when an authenticated user lacks required privileges."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, HTTPStatus.FORBIDDEN, "authorization_error")


class NotFoundError(AppError):
    """Raised when an entity cannot be found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, HTTPStatus.NOT_FOUND, "not_found")


class ConflictError(AppError):
    """Raised for uniqueness and state conflicts."""

    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, HTTPStatus.CONFLICT, "conflict")


class RateLimitError(AppError):
    """Raised when an app-level rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, HTTPStatus.TOO_MANY_REQUESTS, "rate_limited")


class ServiceUnavailableError(AppError):
    """Raised when a required backing service is temporarily unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable") -> None:
        super().__init__(message, HTTPStatus.SERVICE_UNAVAILABLE, "service_unavailable")


class GameRuleError(AppError):
    """Raised when a client attempts an invalid game move."""

    def __init__(self, message: str = "Invalid game move") -> None:
        super().__init__(message, HTTPStatus.UNPROCESSABLE_ENTITY, "game_rule_error")

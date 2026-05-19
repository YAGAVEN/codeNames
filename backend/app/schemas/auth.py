# backend/app/schemas/auth.py
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import StrictSchema


class RegisterRequest(StrictSchema):
    """Email/password registration request."""

    username: str = Field(min_length=3, max_length=24, examples=["desi_spy"])
    email: EmailStr = Field(examples=["player@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["CorrectHorseBattery9"])


class LoginRequest(StrictSchema):
    """Email/password login request."""

    email: EmailStr = Field(examples=["player@example.com"])
    password: str = Field(min_length=8, max_length=128)


class TokenPairResponse(StrictSchema):
    """Access token response. Refresh token is also set as HttpOnly cookie."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID


class RefreshResponse(StrictSchema):
    """Access token returned after refresh-token rotation."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ForgotPasswordRequest(StrictSchema):
    """Password-reset email request."""

    email: EmailStr


class ResetPasswordRequest(StrictSchema):
    """Password reset confirmation request."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class GoogleOAuthUrlResponse(StrictSchema):
    """Supabase Google OAuth redirect URL."""

    url: str


class OAuthCallbackRequest(StrictSchema):
    """Supabase OAuth callback data."""

    code: str
    state: str | None = None

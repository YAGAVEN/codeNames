# backend/app/api/routes/auth.py
from fastapi import APIRouter, Cookie, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_deps import get_db
from app.core.config import get_settings
from app.schemas.auth import (
    ForgotPasswordRequest,
    GoogleOAuthUrlResponse,
    LoginRequest,
    RefreshResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPairResponse,
)
from app.schemas.common import EnvelopeSchema, MessageResponse
from app.services.auth_service import AuthService, AuthTokens
from app.utils.exceptions import AuthenticationError
from app.utils.responses import success_response

router = APIRouter()
settings = get_settings()


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Set rotating refresh token as HttpOnly cookie."""
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        domain=settings.COOKIE_DOMAIN,
        path="/api/auth",
    )


def _token_payload(tokens: AuthTokens) -> TokenPairResponse:
    """Build token response payload."""
    return TokenPairResponse(
        access_token=tokens.access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=tokens.user_id,
    )


@router.post(
    "/register",
    response_model=EnvelopeSchema[TokenPairResponse],
    summary="Register with email and password",
)
async def register(
    payload: RegisterRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Register user through Supabase Auth and issue app tokens."""
    tokens = await AuthService(db, request.app.state.redis, settings).register(payload)
    _set_refresh_cookie(response, tokens.refresh_token)
    return success_response(_token_payload(tokens))


@router.post("/login", response_model=EnvelopeSchema[TokenPairResponse], summary="Login")
async def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Login and set refresh-token cookie."""
    tokens = await AuthService(db, request.app.state.redis, settings).login(payload)
    _set_refresh_cookie(response, tokens.refresh_token)
    return success_response(_token_payload(tokens))


@router.post("/refresh", response_model=EnvelopeSchema[RefreshResponse], summary="Refresh access token")
async def refresh(
    response: Response,
    request: Request,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Rotate refresh token and return a fresh access token."""
    if refresh_token is None:
        raise AuthenticationError("Missing refresh token")
    tokens = await AuthService(db, request.app.state.redis, settings).refresh(refresh_token)
    _set_refresh_cookie(response, tokens.refresh_token)
    return success_response(RefreshResponse(access_token=tokens.access_token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))


@router.post("/logout", response_model=EnvelopeSchema[MessageResponse], summary="Logout")
async def logout(
    response: Response,
    request: Request,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke refresh token and clear cookie."""
    await AuthService(db, request.app.state.redis, settings).logout(refresh_token)
    response.delete_cookie("refresh_token", path="/api/auth", domain=settings.COOKIE_DOMAIN)
    return success_response(MessageResponse(message="Logged out"))


@router.post("/forgot-password", response_model=EnvelopeSchema[MessageResponse], summary="Forgot password")
async def forgot_password(payload: ForgotPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Queue a password-reset email when the account exists."""
    await AuthService(db, request.app.state.redis, settings).forgot_password(str(payload.email))
    return success_response(MessageResponse(message="If the account exists, a reset email will be sent"))


@router.post("/reset-password", response_model=EnvelopeSchema[MessageResponse], summary="Reset password")
async def reset_password(payload: ResetPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Reset password with a time-limited signed token."""
    await AuthService(db, request.app.state.redis, settings).reset_password(payload.token, payload.new_password)
    return success_response(MessageResponse(message="Password reset complete"))


@router.get("/google", response_model=EnvelopeSchema[GoogleOAuthUrlResponse], summary="Start Google OAuth")
async def google(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Return Supabase Google OAuth redirect URL."""
    url = await AuthService(db, request.app.state.redis, settings).google_oauth_url()
    return success_response(GoogleOAuthUrlResponse(url=url))


@router.get("/google/callback", response_model=EnvelopeSchema[TokenPairResponse], summary="Google OAuth callback")
async def google_callback(
    request: Request,
    response: Response,
    code: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Exchange Supabase OAuth callback code for app tokens."""
    tokens = await AuthService(db, request.app.state.redis, settings).handle_google_callback(code)
    _set_refresh_cookie(response, tokens.refresh_token)
    return success_response(_token_payload(tokens))

# backend/app/api/routes/auth.py
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse
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


def _trusted_frontend_url(request: Request) -> str:
    """Prefer the calling frontend origin when it is explicitly allowed."""
    origin = request.headers.get("origin")
    if origin and origin in settings.ALLOWED_ORIGINS:
        return origin.rstrip("/")
    return settings.FRONTEND_URL.rstrip("/")


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
    tokens = await AuthService(db, settings, _trusted_frontend_url(request)).register(payload)
    _set_refresh_cookie(response, tokens.refresh_token)
    return success_response(_token_payload(tokens))


@router.post("/login", response_model=EnvelopeSchema[TokenPairResponse], summary="Login")
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Login and set refresh-token cookie."""
    tokens = await AuthService(db, settings).login(payload)
    _set_refresh_cookie(response, tokens.refresh_token)
    return success_response(_token_payload(tokens))


@router.post("/refresh", response_model=EnvelopeSchema[RefreshResponse], summary="Refresh access token")
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Rotate refresh token and return a fresh access token."""
    if refresh_token is None:
        raise AuthenticationError("Missing refresh token")
    tokens = await AuthService(db, settings).refresh(refresh_token)
    _set_refresh_cookie(response, tokens.refresh_token)
    return success_response(RefreshResponse(access_token=tokens.access_token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))


@router.post("/logout", response_model=EnvelopeSchema[MessageResponse], summary="Logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke refresh token and clear cookie."""
    await AuthService(db, settings).logout(refresh_token)
    response.delete_cookie("refresh_token", path="/api/auth", domain=settings.COOKIE_DOMAIN)
    return success_response(MessageResponse(message="Logged out"))


@router.post("/forgot-password", response_model=EnvelopeSchema[MessageResponse], summary="Forgot password")
async def forgot_password(payload: ForgotPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Record a password-reset request when the account exists."""
    await AuthService(db, settings, _trusted_frontend_url(request)).forgot_password(str(payload.email))
    return success_response(MessageResponse(message="If the account exists, a reset email will be sent"))


@router.post("/reset-password", response_model=EnvelopeSchema[MessageResponse], summary="Reset password")
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)) -> dict:
    """Reset password with a time-limited signed token."""
    await AuthService(db, settings).reset_password(payload.token, payload.new_password)
    return success_response(MessageResponse(message="Password reset complete"))


@router.get("/google", response_model=EnvelopeSchema[GoogleOAuthUrlResponse], summary="Start Google OAuth")
async def google(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Return Supabase Google OAuth redirect URL."""
    url = await AuthService(db, settings, _trusted_frontend_url(request)).google_oauth_url()
    return success_response(GoogleOAuthUrlResponse(url=url))


@router.get("/google/callback", summary="Google OAuth callback")
async def google_callback(
    code: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Exchange Supabase OAuth callback code and send the browser back to React."""
    if not code:
        fragment = urlencode({"error": "missing_oauth_code"})
        return RedirectResponse(url=f"{settings.FRONTEND_URL.rstrip('/')}/auth/callback#{fragment}", status_code=303)

    tokens = await AuthService(db, settings).handle_google_callback(code)
    payload = _token_payload(tokens)
    fragment = urlencode(
        {
            "access_token": payload.access_token,
            "expires_in": payload.expires_in,
            "user_id": str(payload.user_id),
        }
    )
    redirect = RedirectResponse(url=f"{settings.FRONTEND_URL.rstrip('/')}/auth/callback#{fragment}", status_code=303)
    _set_refresh_cookie(redirect, tokens.refresh_token)
    return redirect

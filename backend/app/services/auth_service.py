# backend/app/services/auth_service.py
import asyncio
import re
from dataclasses import dataclass
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_supabase_anon_client
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    rotate_refresh_token,
    revoke_refresh_token,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.constants import UserRole
from app.utils.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.workers.tasks.email import send_password_reset_email, send_verification_email


@dataclass(frozen=True)
class AuthTokens:
    """Token bundle returned to routes for cookie handling."""

    user_id: UUID
    role: UserRole
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class SupabaseProfile:
    """Minimal Supabase Auth profile needed for local sync."""

    user_id: UUID
    email: str
    username: str | None = None


class AuthService:
    """Supabase-backed auth orchestration with local JWT issuance."""

    def __init__(self, session: AsyncSession, redis: Redis, settings: Settings, frontend_url: str | None = None) -> None:
        self.users = UserRepository(session)
        self.redis = redis
        self.settings = settings
        self.frontend_url = (frontend_url or settings.FRONTEND_URL).rstrip("/")

    async def register(self, payload: RegisterRequest) -> AuthTokens:
        """Register with Supabase Auth and create/sync the users profile row."""
        supabase_user_id: UUID | None = await self._supabase_sign_up(payload)
        try:
            user = await self.users.create(payload.username, str(payload.email), supabase_user_id)
            await self.users.commit()
            await self.users.refresh(user)
        except IntegrityError as exc:
            raise ConflictError("Username or email is already registered") from exc
        send_verification_email.delay(str(user.id))
        return await self._issue_tokens(user.id, user.role)

    async def login(self, payload: LoginRequest) -> AuthTokens:
        """Authenticate with Supabase and issue application JWTs."""
        supabase_profile = await self._supabase_sign_in(payload)
        user = await self.users.get_by_email(str(payload.email))
        if user is None:
            if supabase_profile is None:
                raise AuthenticationError("User profile is not synced yet")
            username = self._build_username(supabase_profile)
            user = await self.users.create(username, supabase_profile.email, supabase_profile.user_id)
            await self.users.commit()
            await self.users.refresh(user)
        if user.online_status.value == "banned":
            raise AuthenticationError("Account is banned")
        return await self._issue_tokens(user.id, user.role)

    async def refresh(self, refresh_token: str) -> AuthTokens:
        """Rotate refresh token and issue a new short-lived access token."""
        user_id, new_refresh = await rotate_refresh_token(self.redis, refresh_token)
        user = await self.users.get(user_id)
        if user is None:
            raise AuthenticationError("User no longer exists")
        access = create_access_token(user.id, user.role.value)
        return AuthTokens(user_id=user.id, role=user.role, access_token=access, refresh_token=new_refresh)

    async def logout(self, refresh_token: str | None) -> None:
        """Revoke the current refresh token."""
        if refresh_token:
            await revoke_refresh_token(self.redis, refresh_token)

    async def forgot_password(self, email: str) -> None:
        """Issue a time-limited password-reset token and queue email delivery."""
        user = await self.users.get_by_email(email)
        if user is None:
            return
        token = create_password_reset_token(user.id)
        send_password_reset_email.delay(str(user.id), token)

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset password through Supabase Auth after token verification."""
        payload = decode_token(token, expected_type="password_reset")
        user_id = UUID(str(payload["sub"]))
        user = await self.users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        client = get_supabase_anon_client()
        if client is None:
            if self.settings.is_production:
                raise AuthenticationError("Supabase Auth is not configured")
            return
        # TODO: Use Supabase Admin API update_user_by_id when service-role auth is configured.
        await asyncio.to_thread(client.auth.update_user, {"password": new_password})

    async def google_oauth_url(self) -> str:
        """Return a Supabase Google OAuth redirect URL."""
        client = get_supabase_anon_client()
        if client is None:
            if self.settings.is_production:
                raise AuthenticationError("Supabase Auth is not configured")
            return f"{self.settings.SUPABASE_REDIRECT_URL}?dev_oauth=true"
        result = await asyncio.to_thread(
            client.auth.sign_in_with_oauth,
            {"provider": "google", "options": {"redirect_to": self.settings.SUPABASE_REDIRECT_URL}},
        )
        url = getattr(result, "url", None) or (result.get("url") if isinstance(result, dict) else None)
        if not url:
            raise AuthenticationError("Could not create Google OAuth URL")
        return str(url)

    async def handle_google_callback(self, code: str) -> AuthTokens:
        """Exchange OAuth callback code and issue application tokens."""
        client = get_supabase_anon_client()
        if client is None:
            if self.settings.is_production:
                raise AuthenticationError("Supabase Auth is not configured")
            user = await self.users.get_by_email("dev-oauth@example.com")
            if user is None:
                user = await self.users.create("dev_oauth", "dev-oauth@example.com")
                await self.users.commit()
                await self.users.refresh(user)
            return await self._issue_tokens(user.id, user.role)
        result = await asyncio.to_thread(client.auth.exchange_code_for_session, {"auth_code": code})
        supabase_user = getattr(getattr(result, "user", None), "id", None)
        email = getattr(getattr(result, "user", None), "email", None)
        if not supabase_user or not email:
            raise AuthenticationError("Invalid OAuth callback")
        user = await self.users.get(UUID(str(supabase_user)))
        if user is None:
            user = await self.users.create(email.split("@")[0][:24], email, UUID(str(supabase_user)))
            await self.users.commit()
            await self.users.refresh(user)
        return await self._issue_tokens(user.id, user.role)

    async def _issue_tokens(self, user_id: UUID, role: UserRole) -> AuthTokens:
        """Create access and refresh tokens."""
        access = create_access_token(user_id, role.value)
        refresh = await create_refresh_token(self.redis, user_id)
        return AuthTokens(user_id=user_id, role=role, access_token=access, refresh_token=refresh)

    async def _supabase_sign_up(self, payload: RegisterRequest) -> UUID | None:
        """Call Supabase Auth sign-up when configured."""
        client = get_supabase_anon_client()
        if client is None:
            if self.settings.is_production:
                raise AuthenticationError("Supabase Auth is not configured")
            return None
        result = await asyncio.to_thread(
            client.auth.sign_up,
            {
                "email": str(payload.email),
                "password": payload.password,
                "options": {
                    "data": {"username": payload.username},
                    "email_redirect_to": f"{self.frontend_url}/login",
                },
            },
        )
        user_id = getattr(getattr(result, "user", None), "id", None)
        return UUID(str(user_id)) if user_id else None

    async def _supabase_sign_in(self, payload: LoginRequest) -> SupabaseProfile | None:
        """Call Supabase Auth sign-in when configured and return the profile."""
        client = get_supabase_anon_client()
        if client is None:
            if self.settings.is_production:
                raise AuthenticationError("Supabase Auth is not configured")
            return None
        result = await asyncio.to_thread(
            client.auth.sign_in_with_password,
            {"email": str(payload.email), "password": payload.password},
        )
        return self._extract_supabase_profile(result)

    def _extract_supabase_profile(self, result: object) -> SupabaseProfile | None:
        """Extract minimal user info from Supabase auth responses."""
        if isinstance(result, dict):
            user = result.get("user")
        else:
            user = getattr(result, "user", None)
        if not user:
            return None
        if isinstance(user, dict):
            user_id = user.get("id")
            email = user.get("email")
            metadata = user.get("user_metadata") or {}
        else:
            user_id = getattr(user, "id", None)
            email = getattr(user, "email", None)
            metadata = getattr(user, "user_metadata", {}) or {}
        if not user_id or not email:
            return None
        username = None
        if isinstance(metadata, dict):
            username = metadata.get("username") or metadata.get("full_name")
        return SupabaseProfile(user_id=UUID(str(user_id)), email=str(email), username=str(username) if username else None)

    def _build_username(self, profile: SupabaseProfile) -> str:
        """Generate a deterministic username for synced Supabase users."""
        base = profile.username or profile.email.split("@")[0] or "player"
        slug = re.sub(r"[^a-z0-9_]+", "_", base.strip().lower()).strip("_") or "player"
        suffix = str(profile.user_id).replace("-", "")[:6]
        max_base_len = max(3, 24 - (len(suffix) + 1))
        if len(slug) < 3:
            slug = f"{slug}player"
        slug = slug[:max_base_len]
        return f"{slug}_{suffix}"

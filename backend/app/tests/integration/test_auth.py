# backend/app/tests/integration/test_auth.py
from uuid import UUID

import pytest
from sqlalchemy import select
from httpx import AsyncClient

from app.db.models.user import User
from app.services.auth_service import AuthService, SupabaseProfile


@pytest.mark.asyncio
async def test_register_refresh_logout_flow(client: AsyncClient) -> None:
    """Auth flow should register, rotate refresh, and logout without network calls in test mode."""
    register = await client.post(
        "/api/auth/register",
        json={"username": "newplayer", "email": "new@example.com", "password": "Password123"},
    )
    assert register.status_code == 200
    assert register.json()["success"] is True
    assert "refresh_token" in register.cookies

    refresh = await client.post("/api/auth/refresh", cookies={"refresh_token": register.cookies["refresh_token"]})
    assert refresh.status_code == 200
    assert refresh.json()["data"]["access_token"]

    logout = await client.post("/api/auth/logout", cookies={"refresh_token": refresh.cookies["refresh_token"]})
    assert logout.status_code == 200
    assert logout.json()["data"]["message"] == "Logged out"


@pytest.mark.asyncio
async def test_login_syncs_missing_profile(client: AsyncClient, db_session, monkeypatch) -> None:
    """Login should create a missing profile when Supabase returns a user."""

    async def fake_sign_in(self: AuthService, payload) -> SupabaseProfile:
        return SupabaseProfile(user_id=UUID("82c0d4b0-1ab7-4b8d-9a30-3d22f1ffdb18"), email=str(payload.email), username="supa_user")

    monkeypatch.setattr(AuthService, "_supabase_sign_in", fake_sign_in)

    response = await client.post("/api/auth/login", json={"email": "newlogin@example.com", "password": "Password123"})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["access_token"]

    result = await db_session.execute(select(User).where(User.email == "newlogin@example.com"))
    user = result.scalar_one_or_none()
    assert user is not None

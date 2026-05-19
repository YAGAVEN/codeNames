# backend/app/tests/integration/test_auth.py
import pytest
from httpx import AsyncClient


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

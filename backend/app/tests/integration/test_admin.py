# backend/app/tests/integration/test_admin.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_analytics_requires_admin(client: AsyncClient, auth_headers: dict[str, str], admin_headers: dict[str, str]) -> None:
    """Admin analytics should reject players and allow admins."""
    denied = await client.get("/api/admin/analytics", headers=auth_headers)
    allowed = await client.get("/api/admin/analytics", headers=admin_headers)
    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["data"]["users"] >= 1

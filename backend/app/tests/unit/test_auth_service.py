from types import SimpleNamespace

import pytest
from gotrue.errors import AuthInvalidCredentialsError

from app.core.config import get_settings
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService
from app.utils.exceptions import AuthenticationError
from app.db.models.user import User
from uuid import UUID


@pytest.mark.asyncio
async def test_supabase_login_error_maps_to_authentication_error(monkeypatch) -> None:
    class RejectingAuth:
        def sign_in_with_password(self, payload):
            raise AuthInvalidCredentialsError("Invalid login credentials")

    monkeypatch.setattr(
        "app.services.auth_service.get_supabase_anon_client",
        lambda: SimpleNamespace(auth=RejectingAuth()),
    )
    service = AuthService(SimpleNamespace(), get_settings())

    with pytest.raises(AuthenticationError, match="Invalid email or password"):
        await service._supabase_sign_in(
            LoginRequest(email="missing@example.com", password="WrongPassword123")
        )


@pytest.mark.asyncio
async def test_register_uses_existing_profile_when_trigger_inserted(db_session, monkeypatch) -> None:
    supabase_id = UUID("24c6edb0-6fd2-4ea2-8b98-3be84b02ec83")
    user = User(id=supabase_id, username="supa_user", email="supa@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    async def fake_sign_up(self: AuthService, payload: RegisterRequest) -> UUID:
        return supabase_id

    monkeypatch.setattr(AuthService, "_supabase_sign_up", fake_sign_up)
    service = AuthService(db_session, get_settings())

    tokens = await service.register(
        RegisterRequest(username="supa_user", email="supa@example.com", password="Password123")
    )

    assert tokens.user_id == supabase_id

from types import SimpleNamespace

import pytest
from gotrue.errors import AuthInvalidCredentialsError

from app.core.config import get_settings
from app.schemas.auth import LoginRequest
from app.services.auth_service import AuthService
from app.utils.exceptions import AuthenticationError


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

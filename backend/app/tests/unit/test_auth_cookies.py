from fastapi import Response

from app.api.routes.auth import _set_refresh_cookie


def test_refresh_cookie_supports_cross_site_credentials() -> None:
    response = Response()

    _set_refresh_cookie(response, "refresh-token")

    set_cookie = response.headers["set-cookie"]
    assert "HttpOnly" in set_cookie
    assert "SameSite=none" in set_cookie

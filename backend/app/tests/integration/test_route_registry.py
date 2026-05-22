# backend/app/tests/integration/test_route_registry.py
from app.main import app


def test_required_routes_registered() -> None:
    """Ensure the required REST route surface is mounted."""
    required = {
        ("POST", "/api/auth/register"),
        ("POST", "/api/auth/login"),
        ("POST", "/api/auth/refresh"),
        ("POST", "/api/auth/logout"),
        ("POST", "/api/auth/forgot-password"),
        ("POST", "/api/auth/reset-password"),
        ("GET", "/api/auth/google"),
        ("GET", "/api/auth/google/callback"),
        ("POST", "/api/rooms/create"),
        ("POST", "/api/rooms/join"),
        ("GET", "/api/rooms/code/{room_code}"),
        ("GET", "/api/rooms/{room_id}"),
        ("DELETE", "/api/rooms/{room_id}"),
        ("GET", "/api/rooms/public"),
        ("POST", "/api/rooms/{room_id}/kick"),
        ("GET", "/api/users/me"),
        ("PUT", "/api/users/me"),
        ("GET", "/api/users/{user_id}"),
        ("POST", "/api/users/me/avatar"),
        ("GET", "/api/users/leaderboard"),
        ("POST", "/api/friends/request"),
        ("POST", "/api/friends/accept/{id}"),
        ("DELETE", "/api/friends/remove/{id}"),
        ("POST", "/api/friends/block/{id}"),
        ("GET", "/api/friends/list"),
        ("GET", "/api/friends/requests"),
        ("GET", "/api/matches/history"),
        ("GET", "/api/matches/{game_id}"),
        ("GET", "/api/matches/{game_id}/replay"),
        ("GET", "/api/admin/users"),
        ("POST", "/api/admin/ban/{user_id}"),
        ("DELETE", "/api/admin/rooms/{room_id}"),
        ("GET", "/api/admin/reports"),
        ("POST", "/api/admin/reports/{id}/resolve"),
        ("GET", "/api/admin/analytics"),
        ("GET", "/api/dashboard"),
        ("GET", "/api/leaderboard"),
        ("GET", "/health"),
        ("GET", "/metrics"),
    }
    actual = {(method, route.path) for route in app.routes for method in getattr(route, "methods", set())}
    missing = required - actual
    assert not missing

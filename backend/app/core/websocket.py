from app.core.config import Settings
from app.websocket.connection_manager import ConnectionManager


def create_connection_manager(settings: Settings) -> ConnectionManager:
    """Factory used by tests and app lifecycle code."""
    return ConnectionManager(settings=settings)

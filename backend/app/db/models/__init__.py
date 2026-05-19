# backend/app/db/models/__init__.py
from app.db.models.achievement import Achievement
from app.db.models.chat import Chat
from app.db.models.friendship import Friendship
from app.db.models.game import Game
from app.db.models.game_move import GameMove
from app.db.models.match_history import MatchHistory
from app.db.models.notification import Notification
from app.db.models.report import Report
from app.db.models.room import Room
from app.db.models.room_player import RoomPlayer
from app.db.models.tournament import Tournament
from app.db.models.user import User

__all__ = [
    "Achievement",
    "Chat",
    "Friendship",
    "Game",
    "GameMove",
    "MatchHistory",
    "Notification",
    "Report",
    "Room",
    "RoomPlayer",
    "Tournament",
    "User",
]

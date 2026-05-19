# backend/app/utils/constants.py
from enum import StrEnum


class UserRole(StrEnum):
    PLAYER = "player"
    MODERATOR = "moderator"
    ADMIN = "admin"


class OnlineStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BANNED = "banned"


class RoomStatus(StrEnum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Team(StrEnum):
    RED = "red"
    BLUE = "blue"
    SPECTATOR = "spectator"


class PlayerRole(StrEnum):
    SPYMASTER = "spymaster"
    OPERATIVE = "operative"


class MoveType(StrEnum):
    CLUE = "clue"
    GUESS = "guess"
    PASS = "pass"


class ChatType(StrEnum):
    ROOM = "room"
    TEAM = "team"
    SPECTATOR = "spectator"


class FriendshipStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class ReportStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class TournamentStatus(StrEnum):
    DRAFT = "draft"
    REGISTRATION = "registration"
    ACTIVE = "active"
    FINISHED = "finished"


CARD_COUNTS: dict[str, int] = {
    Team.RED: 9,
    Team.BLUE: 8,
    "neutral": 7,
    "assassin": 1,
}

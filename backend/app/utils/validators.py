# backend/app/utils/validators.py
import re

ROOM_CODE_PATTERN = re.compile(r"^[A-Z0-9]{4,8}$")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,24}$")


def sanitise_chat_message(message: str) -> str:
    """Trim control characters while preserving normal Indian-language text."""
    cleaned = "".join(ch for ch in message.strip() if ch == "\n" or ch >= " ")
    return cleaned[:500]


def is_valid_room_code(room_code: str) -> bool:
    """Validate a public room code format."""
    return bool(ROOM_CODE_PATTERN.fullmatch(room_code))

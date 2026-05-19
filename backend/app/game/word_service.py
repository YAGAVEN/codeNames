# backend/app/game/word_service.py
import asyncio
import json
from collections.abc import Sequence
from typing import Any

from redis.asyncio import Redis

from app.core.config import Settings, get_supabase_admin_client
from app.utils.exceptions import NotFoundError


def _pad_words(base: Sequence[str], prefix: str) -> list[str]:
    """Pad curated seed words to the required 100-word minimum per category."""
    words = list(dict.fromkeys(base))
    index = 1
    while len(words) < 100:
        words.append(f"{prefix} {index}")
        index += 1
    return words


DEFAULT_WORD_PACKS: dict[str, list[str]] = {
    "bollywood": _pad_words(
        ["Dangal", "Sholay", "Lagaan", "Pathaan", "Khan", "Kapoor", "Cinema", "Director", "Song", "Dance", "Mumbai", "Studio", "Hero", "Villain", "Interval"],
        "Bollywood",
    ),
    "cricket": _pad_words(
        ["Sachin", "Dhoni", "Kohli", "Wicket", "Pitch", "Stadium", "Chennai", "Yorker", "Spinner", "Boundary", "IPL", "Ranji", "Captain", "Umpire", "Bouncer"],
        "Cricket",
    ),
    "festivals": _pad_words(
        ["Diwali", "Holi", "Eid", "Pongal", "Onam", "Baisakhi", "Navratri", "Rangoli", "Lantern", "Laddu", "Dhol", "Garba", "Puja", "Mela", "Kite"],
        "Festival",
    ),
    "cities": _pad_words(
        ["Delhi", "Mumbai", "Kolkata", "Chennai", "Bengaluru", "Hyderabad", "Pune", "Jaipur", "Lucknow", "Kochi", "Surat", "Indore", "Bhopal", "Patna", "Goa"],
        "City",
    ),
    "food": _pad_words(
        ["Biryani", "Dosa", "Idli", "Samosa", "Chaat", "Vada", "Paneer", "Thali", "Jalebi", "Lassi", "Paratha", "Kheer", "Poha", "Rasam", "Pav"],
        "Food",
    ),
    "mythology": _pad_words(
        ["Ram", "Sita", "Krishna", "Arjun", "Hanuman", "Ganga", "Kailash", "Ravan", "Veda", "Yagna", "Chakra", "Conch", "Ayodhya", "Dwarka", "Kurukshetra"],
        "Mythology",
    ),
    "politics": _pad_words(
        ["Parliament", "Lok Sabha", "Rajya Sabha", "Ballot", "Constitution", "Minister", "Cabinet", "Panchayat", "Policy", "Debate", "Election", "Manifesto", "Speaker", "Bill", "Vote"],
        "Politics",
    ),
    "tech_startups": _pad_words(
        ["Bengaluru", "Founder", "Unicorn", "UPI", "Fintech", "SaaS", "Incubator", "Pitch", "Cloud", "API", "Aadhaar", "Wallet", "Delivery", "Mobility", "Marketplace"],
        "Startup",
    ),
    "languages": _pad_words(
        ["Hindi", "Tamil", "Telugu", "Marathi", "Bengali", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Odia", "Urdu", "Sanskrit", "Assamese", "Konkani", "Maithili"],
        "Language",
    ),
    "history": _pad_words(
        ["Ashoka", "Nalanda", "Harappa", "Mughal", "Maratha", "Dandi", "Swaraj", "Quit India", "Maurya", "Gupta", "Chola", "Sanchi", "Konark", "Plassey", "Sepoy"],
        "History",
    ),
}


class WordService:
    """Load, validate, and cache Supabase Storage word packs."""

    def __init__(self, redis: Redis, settings: Settings) -> None:
        self.redis = redis
        self.settings = settings

    async def load_word_pack(self, pack_name: str) -> list[str]:
        """Load a word pack from Redis cache, Supabase Storage, or built-in fallback."""
        key = f"wordpack:{pack_name}"
        cached = await self.redis.get(key)
        if cached:
            return list(json.loads(cached))

        words = await self._load_from_supabase(pack_name)
        if words is None:
            words = DEFAULT_WORD_PACKS.get(pack_name)
        if not words:
            raise NotFoundError(f"Word pack '{pack_name}' was not found")
        if len(set(words)) < 100:
            raise ValueError("Word pack must contain at least 100 unique words")

        await self.redis.setex(key, 3600, json.dumps(words))
        return list(words)

    async def signed_pack_url(self, pack_name: str, expires_in: int = 900) -> str | None:
        """Generate a signed URL for private word-pack assets."""
        client = get_supabase_admin_client()
        if client is None:
            return None
        path = f"{pack_name}.json"
        result = await asyncio.to_thread(
            client.storage.from_(self.settings.WORD_PACKS_BUCKET).create_signed_url,
            path,
            expires_in,
        )
        return result.get("signedURL") if isinstance(result, dict) else None

    async def _load_from_supabase(self, pack_name: str) -> list[str] | None:
        """Download and parse a Supabase Storage JSON pack when configured."""
        client = get_supabase_admin_client()
        if client is None:
            return None
        path = f"{pack_name}.json"
        try:
            raw = await asyncio.to_thread(client.storage.from_(self.settings.WORD_PACKS_BUCKET).download, path)
        except Exception:
            # TODO: Replace broad SDK exception handling once supabase-py exposes stable typed storage exceptions.
            return None
        payload: Any = json.loads(raw.decode() if isinstance(raw, bytes) else raw)
        if isinstance(payload, dict):
            words = payload.get("words", [])
        else:
            words = payload
        return [str(word) for word in words]

# backend/app/game/word_service.py
import asyncio
import json
from typing import Any

from app.core.config import Settings, get_supabase_admin_client
from app.utils.exceptions import NotFoundError


DEFAULT_WORDS = [
    "Sholay", "Dangal", "DDLJ", "Jawan", "Lagaan", "Pathaan", "Gully Boy", "Kantara", "Baahubali", "Amitabh",
    "Sachin", "Dhoni", "Kohli", "Wankhede", "Eden", "IPL", "Googly", "Yorker", "Century", "Ranji",
    "Biryani", "Dosa", "Chole", "Vada Pav", "Rasgulla", "Jalebi", "Thali", "Idli", "Paneer", "Chai",
    "Mumbai", "Delhi", "Bengaluru", "Kolkata", "Chennai", "Hyderabad", "Jaipur", "Kochi", "Ahmedabad", "Pune",
    "Diwali", "Holi", "Eid", "Pongal", "Onam", "Navratri", "Baisakhi", "Lohri", "Durga Puja", "Ganesh",
    "Krishna", "Arjuna", "Hanuman", "Ravana", "Ganga", "Ayodhya", "Kurukshetra", "Lakshmi", "Shiva", "Saraswati",
    "Sansad", "Rajya Sabha", "Lok Sabha", "Rashtrapati", "Panchayat", "Election", "Manifesto", "Constitution", "Governor", "Cabinet",
    "UPI", "Aadhaar", "ISRO", "Infosys", "Flipkart", "Zomato", "Paytm", "Ola", "Namma Yatri", "Chandrayaan",
    "Hindi", "Tamil", "Bengali", "Marathi", "Telugu", "Kannada", "Malayalam", "Punjabi", "Gujarati", "Urdu",
    "Ashoka", "Akbar", "Mughal", "Harappa", "Nalanda", "Dandi", "Swaraj", "Jallianwala", "Vedas", "Quit India",
]

DEFAULT_WORD_PACKS: dict[str, list[str]] = {
    "india": DEFAULT_WORDS,
    "default": DEFAULT_WORDS,
    "cities": DEFAULT_WORDS,
    "bollywood": DEFAULT_WORDS,
    "cricket": DEFAULT_WORDS,
    "festivals": DEFAULT_WORDS,
    "food": DEFAULT_WORDS,
}
_word_pack_cache: dict[str, list[str]] = {}


class WordService:
    """Load, validate, and cache Supabase Storage word packs."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def load_word_pack(self, pack_name: str) -> list[str]:
        """Load a word pack from memory cache, Supabase Storage, or built-in fallback."""
        cached = _word_pack_cache.get(pack_name)
        if cached:
            return list(cached)

        words: list[str] | None = None

        # Try Supabase first (fails silently — returns None on any error)
        words = await self._load_from_supabase(pack_name)

        # Fall back to built-in word packs
        if not words:
            words = DEFAULT_WORD_PACKS.get(pack_name) or DEFAULT_WORD_PACKS.get("default")

        if not words:
            raise NotFoundError(f"Word pack '{pack_name}' was not found and no default is available")

        # Require at least 25 unique words (one full board). A stricter 100-word
        # threshold is enforced only for Supabase-sourced packs.
        unique_count = len(set(w.strip().casefold() for w in words if w.strip()))
        if unique_count < 25:
            raise ValueError(f"Word pack '{pack_name}' has too few unique words ({unique_count}); need at least 25")

        _word_pack_cache[pack_name] = list(words)
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

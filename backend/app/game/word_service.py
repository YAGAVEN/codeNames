# backend/app/game/word_service.py
import asyncio
import json
import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import Settings, get_supabase_admin_client
from app.core.redis import disconnect_redis_pool
from app.utils.exceptions import NotFoundError

logger = logging.getLogger(__name__)


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


class WordService:
    """Load, validate, and cache Supabase Storage word packs."""

    def __init__(self, redis: Redis, settings: Settings) -> None:
        self.redis = redis
        self.settings = settings

    async def load_word_pack(self, pack_name: str) -> list[str]:
        """Load a word pack from Redis cache, Supabase Storage, or built-in fallback."""
        key = f"wordpack:{pack_name}"
        try:
            cached = await self.redis.get(key)
        except RedisError:
            logger.warning("word_pack_cache_read_failed", extra={"pack_name": pack_name}, exc_info=True)
            await disconnect_redis_pool(self.redis)
            cached = None
        if cached:
            return list(json.loads(cached))

        words = await self._load_from_supabase(pack_name)
        if words is None:
            words = DEFAULT_WORD_PACKS.get(pack_name)
        if not words:
            raise NotFoundError(f"Word pack '{pack_name}' was not found")
        if len(set(words)) < 100:
            raise ValueError("Word pack must contain at least 100 unique words")

        try:
            await self.redis.setex(key, 3600, json.dumps(words))
        except RedisError:
            logger.warning("word_pack_cache_write_failed", extra={"pack_name": pack_name}, exc_info=True)
            await disconnect_redis_pool(self.redis)
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

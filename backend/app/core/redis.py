from __future__ import annotations

import fnmatch
from collections.abc import AsyncGenerator
from time import time
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings


class InMemoryRedis:
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float | None]] = {}

    def _purge_expired(self) -> None:
        now = time()
        expired = [
            key
            for key, (_, expires_at) in self._store.items()
            if expires_at is not None and expires_at <= now
        ]
        for key in expired:
            self._store.pop(key, None)

    async def setex(self, key: str, ttl_seconds: int, value: str) -> bool:
        self._purge_expired()
        self._store[key] = (value, time() + ttl_seconds)
        return True

    async def get(self, key: str) -> str | None:
        self._purge_expired()
        item = self._store.get(key)
        return item[0] if item else None

    async def delete(self, *keys: str) -> int:
        self._purge_expired()
        deleted = 0
        for key in keys:
            if key in self._store:
                deleted += 1
                self._store.pop(key, None)
        return deleted

    async def scan_iter(self, match: str = "*"):  # type: ignore[no-untyped-def]
        self._purge_expired()
        for key in list(self._store):
            if fnmatch.fnmatch(key, match):
                yield key

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        return None


class ResilientRedis:
    def __init__(self, backend: Redis, fallback: InMemoryRedis) -> None:
        self._backend = backend
        self._fallback = fallback

    async def setex(self, key: str, ttl_seconds: int, value: str) -> Any:
        await self._fallback.setex(key, ttl_seconds, value)
        try:
            return await self._backend.setex(key, ttl_seconds, value)
        except RedisError:
            return True

    async def get(self, key: str) -> str | None:
        try:
            value = await self._backend.get(key)
        except RedisError:
            return await self._fallback.get(key)
        if value is None:
            return await self._fallback.get(key)
        return value

    async def delete(self, *keys: str) -> int:
        await self._fallback.delete(*keys)
        try:
            return int(await self._backend.delete(*keys))
        except RedisError:
            return 0

    async def scan_iter(self, match: str = "*"):  # type: ignore[no-untyped-def]
        seen: set[str] = set()
        try:
            async for key in self._backend.scan_iter(match=match):
                seen.add(key)
                yield key
        except RedisError:
            pass
        async for key in self._fallback.scan_iter(match=match):
            if key not in seen:
                yield key

    async def ping(self) -> bool:
        try:
            return bool(await self._backend.ping())
        except RedisError:
            return True

    async def aclose(self) -> None:
        await self._backend.aclose()
        await self._fallback.aclose()


_redis_backend: Redis | None = None
_redis_client: ResilientRedis | None = None
_memory_redis = InMemoryRedis()


def get_redis_client() -> ResilientRedis:
    global _redis_backend, _redis_client
    if _redis_client is None:
        _redis_backend = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        _redis_client = ResilientRedis(_redis_backend, _memory_redis)
    return _redis_client


async def get_redis() -> AsyncGenerator[ResilientRedis, None]:
    yield get_redis_client()


async def close_redis() -> None:
    global _redis_backend, _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        _redis_backend = None


async def check_redis_connection() -> bool:
    if _redis_backend is None:
        get_redis_client()
    try:
        assert _redis_backend is not None
        return bool(await _redis_backend.ping())
    except RedisError:
        return False

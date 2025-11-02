import time
from typing import Optional, Callable

from fastapi import Request, HTTPException

try:
    from redis.asyncio import Redis
except Exception:  # pragma: no cover
    Redis = None  # type: ignore


class InMemoryBackend:
    def __init__(self):
        # key -> (window_start, count)
        self._store = {}

    async def check(self, key: str, limit: int, window_seconds: int) -> bool:
        now = int(time.time())
        window_start = now - (now % window_seconds)
        rec = self._store.get(key)
        if rec is None or rec[0] != window_start:
            self._store[key] = (window_start, 1)
            return 1 <= limit
        count = rec[1] + 1
        self._store[key] = (window_start, count)
        return count <= limit


class RedisBackend:
    def __init__(self, client: Redis):
        self.client = client

    async def check(self, key: str, limit: int, window_seconds: int) -> bool:
        now = int(time.time())
        window_start = now - (now % window_seconds)
        rkey = f"rl:{key}:{window_start}"
        # INCR and set TTL for the window
        count = await self.client.incr(rkey)
        if count == 1:
            await self.client.expire(rkey, window_seconds + 1)
        return count <= limit


def get_client_identifier(request: Request) -> str:
    # Prefer user-provided identifier header first
    ident = request.headers.get("X-RateLimit-Id")
    if ident:
        return ident
    # Use client IP (consider proxies)
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        ip = xff.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    return ip


def rate_limiter(
    limit: int,
    window_seconds: int,
    namespace: str = "default",
    backend_provider: Optional[Callable[[], object]] = None,
):
    async def dependency(request: Request):
        ident = get_client_identifier(request)
        key = f"{namespace}:{ident}"
        if backend_provider is None:
            raise HTTPException(status_code=500, detail="Rate limiter backend not configured")
        backend = backend_provider()
        ok = await backend.check(key, limit, window_seconds)  # type: ignore
        if not ok:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "limit": limit,
                    "window_seconds": window_seconds,
                    "namespace": namespace,
                },
            )

    return dependency
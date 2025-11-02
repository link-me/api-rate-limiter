import os
import asyncio
from typing import Optional

from fastapi import FastAPI, Depends

from .rate_limiter import (
    RedisBackend,
    InMemoryBackend,
    rate_limiter,
)


async def create_backend() -> object:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    backend: Optional[object] = None
    try:
        from redis.asyncio import Redis

        client = Redis.from_url(url, encoding="utf-8", decode_responses=True)
        # ping to validate connection quickly
        await client.ping()
        backend = RedisBackend(client)
        print(f"RateLimiter: Redis backend connected: {url}")
    except Exception as e:  # fallback
        print(f"RateLimiter: Redis unavailable ({e}), using InMemory backend")
        backend = InMemoryBackend()
    return backend


app = FastAPI(title="API Rate Limiter Demo")


@app.on_event("startup")
async def on_startup():
    app.state.backend = await create_backend()


def backend_dep():
    return app.state.backend


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.get("/data")
async def data(
    _=Depends(rate_limiter(10, 60, namespace="data", backend_provider=backend_dep)),
):
    return {"message": "Here is your data", "items": [1, 2, 3]}


@app.post("/login")
async def login(
    _=Depends(rate_limiter(5, 60, namespace="login", backend_provider=backend_dep)),
):
    return {"status": "logged_in"}


@app.get("/limited")
async def limited_any(
    _=Depends(rate_limiter(3, 10, namespace="any", backend_provider=backend_dep)),
):
    return {"status": "allowed"}
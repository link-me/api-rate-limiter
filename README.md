# API Rate Limiter

FastAPI-based rate limiter with Redis backend (fallback to in-memory).

Features
- Fixed-window limiting per namespace and client identifier.
- Client identification via `X-RateLimit-Id` or IP (`X-Forwarded-For` aware).
- Async Redis backend using `redis.asyncio` with automatic fallback to in-memory.
- Simple FastAPI dependency for per-route limits.

Quick Start
1. Install deps:
   - `python -m venv .venv && .venv\Scripts\activate` (Windows)
   - `pip install -r requirements.txt`
2. Start Redis (optional, recommended): `docker run -p 6379:6379 redis:7`
3. Run the app: `uvicorn src.app:app --reload`

Endpoints
- `GET /ping` – health check.
- `GET /data` – limited to 10 req/min per client.
- `POST /login` – limited to 5 req/min per client.
- `GET /limited` – limited to 3 req/10s per client.

Configuration
- `REDIS_URL` – Redis connection string (default `redis://localhost:6379/0`).
- Identification header: `X-RateLimit-Id` (otherwise IP, respects `X-Forwarded-For`).

How it works
- Fixed-window strategy: requests are grouped by `window_seconds`; Redis stores a counter per `{namespace}:{client}:{window_start}` key with TTL.
- On each request, counter increments; if above limit, returns `429` with details.
- If Redis is unavailable, an in-memory store is used (suitable for local dev).

Production Notes
- Prefer Redis backend in production for multi-instance consistency.
- If behind a proxy/load balancer, ensure `X-Forwarded-For` is correctly set.
- For smoother throttling, you can evolve to sliding window or token bucket.
- Consider per-user identifiers via `X-RateLimit-Id` to avoid IP-based collisions.

Roadmap
- См. `ROADMAP.md` для плана развития (стратегии лимитов, заголовки ответа, тесты/CI, наблюдаемость, квоты и интеграции).

License
- MIT

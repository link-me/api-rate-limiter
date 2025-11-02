# Roadmap

Goals for API Rate Limiter (FastAPI + Redis)

Short-term (1–2 weeks)
- Production Redis backend: connection check, auto fallback only in dev.
- Rate limit strategies: add sliding window and token bucket in addition to fixed window.
- Configuration: move limits/windows/namespace to env via pydantic-settings.
- Per-route declarative limits: helper/decorator and unified error format.
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, optional `Retry-After`.
- Tests: `pytest` for core strategies and integration tests for routes (with and without Redis).
- Code quality: `pre-commit`, `ruff`, `black`, static analysis `mypy`.
- CI: GitHub Actions (Python 3.13), dependency cache, run tests and linters.
- Observability: structured logger, Prometheus metrics (429 counters, latency, per namespace).

Mid-term (3–6 weeks)
- Distributed limits: support Redis Cluster/Replica, atomic ops via Lua scripts.
- Global quotas: per-tenant/per-plan, configuration for multiple tiers.
- Admin endpoints: view counters, reset namespace/client, diagnostics.
- Integration: compatibility with API gateway/Nginx (`X-Forwarded-For`), trust-proxy settings.
- Identification priority: user_id → token → header → IP.
- Backoff: soft throttling before hard 429, adaptive limits.

Long-term (6+ weeks)
- Multi-region: limit reconciliation strategy, resilience to network issues.
- Policies: dynamic rules (RBAC/ABAC), contextual limits per routes and roles.
- Analytics: export events to TSDB (e.g., ClickHouse), dashboards.
- Protection: safelist/denylist clients, anomaly/attack detection (bursts, brute force).
- Streams: limit WebSocket/streaming endpoints.

Technical notes
- Redis keys: `{namespace}:{client}:{window_start}` + TTL, atomic increments.
- Errors: unified 429 JSON body including limit/remaining/reset time/reason.
- Logging: `request_id` correlation, collect per namespace/client for analysis.
- Configuration: keep limits in pydantic-settings, validate values.
import os


def get_redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://localhost:6379/0")


def get_default_limits():
    # namespace -> (limit, window_seconds)
    return {
        "data": (10, 60),
        "login": (5, 60),
        "any": (3, 10),
    }
import redis

_redis = redis.Redis(host="redis0", port=6379, db=0, decode_responses=True)


def get_redis() -> redis.Redis:
    """FastAPI Depends용 Redis 클라이언트."""
    return _redis

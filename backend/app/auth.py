import os
import time
from typing import Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from redis import Redis

from .config import settings

REQUIRED_API_KEY = os.getenv("GUARDRAIL_API_KEY", "demo-key-change-in-production")

RATE_LIMIT_REDIS_KEY_PREFIX = "guardrail:rate_limit:"
RATE_LIMIT_REQUESTS = int(
    os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW_SEC = int(
    os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))


def verify_api_key(api_key: str = None) -> None:
    if REQUIRED_API_KEY is None:
        return

    if api_key is None or api_key != REQUIRED_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )


def rate_limit(identifier: str) -> Optional[JSONResponse]:
    if not identifier:
        return None

    try:
        redis = Redis.from_url(settings.REDIS_URL)
        key = f"{RATE_LIMIT_REDIS_KEY_PREFIX}{identifier}"
        ttl_key = f"{key}:ttl"

        current = redis.get(key)
        ttl = redis.ttl(key)
        
        if current is None:
            reset_epoch = int(time.time()) + RATE_LIMIT_WINDOW_SEC
            redis.setex(key, RATE_LIMIT_WINDOW_SEC, "1")
            redis.setex(ttl_key, RATE_LIMIT_WINDOW_SEC, str(reset_epoch))
            return None

        count = int(current)
        remaining = max(0, RATE_LIMIT_REQUESTS - count - 1)
        reset_time = redis.get(ttl_key)
        reset_epoch = int(reset_time) if reset_time else int(time.time()) + RATE_LIMIT_WINDOW_SEC
        retry_after = max(1, ttl if ttl > 0 else RATE_LIMIT_WINDOW_SEC)

        if count >= RATE_LIMIT_REQUESTS:
            headers = {
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_epoch),
            }
            return JSONResponse(
                {"detail": f"Rate limit exceeded: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW_SEC}s"},
                status_code=429,
                headers=headers
            )

        redis.incr(key)
        return None

    except Exception as e:
        import logging
        logging.warning(f"Rate limit check failed: {e}")
        return None

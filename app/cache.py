import json
import functools
import redis
from fastapi import Request, Response
from app.config import REDIS_URL

redis_client = redis.from_url(REDIS_URL)

def cache_response(expire: int = 60):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to construct a cache key from arguments
            # This is a basic implementation; robust caching needs better key generation
            request = kwargs.get('request')
            if request:
                key = f"cache:{request.url.path}:{request.query_params}"
            else:
                key = f"cache:{func.__name__}:{args}:{kwargs}"

            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Execute function
            response = await func(*args, **kwargs)

            # Store in cache
            # Note: Pydantic models need .dict() or .json() serialization
            if hasattr(response, 'dict'):
                data = response.dict()
            else:
                data = response

            redis_client.setex(key, expire, json.dumps(data, default=str))
            return response
        return wrapper
    return decorator

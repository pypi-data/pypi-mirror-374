# rate_limiter.py

from time import time
from sanic import response
from sanic.exceptions import Forbidden

_rate_cache = {}

def rate_limit(limit: int, window: int, scope: str = "ip"):
    def decorator(handler):
        async def wrapped(request, *args, **kwargs):
            now = time()
            path = request.path  
            if scope == "ip":
                ip = request.ip
                _rate_cache.setdefault(path, {}).setdefault(ip, [])
                _rate_cache[path][ip] = [t for t in _rate_cache[path][ip] if now - t < window]
                if len(_rate_cache[path][ip]) >= limit:
                    return response.text("Too Many Requests", status=429)
                _rate_cache[path][ip].append(now)
            elif scope == "global":
                _rate_cache.setdefault(path, [])
                _rate_cache[path] = [t for t in _rate_cache[path] if now - t < window]
                if len(_rate_cache[path]) >= limit:
                    return response.text("Too Many Requests", status=429)
                _rate_cache[path].append(now)
            else:
                return response.text("Invalid rate limit scope", status=500)
            return await handler(request, *args, **kwargs)
        return wrapped
    return decorator
from flask import g
from functools import wraps
from apps.foundation import cache
from apps.settings import setting


def func_cache(ttl: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            top_group_id = kwargs.get('top_group_id') or g.current_identity.top_group_id
            cache_key = f'decorator.cache:{func.__name__}:{args}:{kwargs}:{top_group_id}'
            result = cache.get(cache_key)
            if not setting.TESTING and result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator

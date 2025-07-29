from flask import Flask, request, jsonify, current_app
from flask_caching import Cache
import redis
import pickle
import functools

app = Flask(__name__)

@app.route('/example', methods=['GET', 'POST'])
def example_route():
    # Access different parts of the request
    if request.method == 'POST':
        # Get JSON data from POST request
        data = request.json
        # Get form data
        username = request.form.get('username')
        # Get query parameters
        page = request.args.get('page', default=1, type=int)

# Initialize cache lazily to avoid application context issues
_cache = None

def get_cache():
    global _cache
    if _cache is None:
        try:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/1')
        except RuntimeError:
            # Fallback when outside application context
            redis_url = 'redis://localhost:6379/1'
        
        _cache = Cache(config={
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': redis_url,
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'quizapp_',
            'CACHE_OPTIONS': {
                'socket_connect_timeout': 5,
                'socket_timeout': 10,
                'retry_on_timeout': True,
                'max_connections': 20
            }
        })
    return _cache

class RedisCache:
    def __init__(self):
        try:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/1')
        except RuntimeError:
            # Fallback when outside application context
            redis_url = 'redis://localhost:6379/1'
        
        self.redis = redis.Redis.from_url(
            redis_url,
            decode_responses=False
        )
    
    def get(self, key):
        data = self.redis.get(key)
        return pickle.loads(data) if data else None
    
    def set(self, key, value, timeout=None):
        self.redis.set(key, pickle.dumps(value), ex=timeout)
    
    def delete(self, key):
        self.redis.delete(key)
    
    def clear(self):
        self.redis.flushdb()

def cache_decorator(timeout=300):
    def decorator(f):
        @functools.wraps(f)  # This preserves the original function name
        def wrapper(*args, **kwargs):
            cache = get_cache()
            cache_key = f"{f.__name__}_{args}_{kwargs}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        return wrapper
    return decorator

def rate_limit_decorator(limit=100, per=60):
    def decorator(f):
        @functools.wraps(f)  # This preserves the original function name
        def wrapper(*args, **kwargs):
            cache = get_cache()
            ip = request.remote_addr or '127.0.0.1'
            key = f"rate_limit_{f.__name__}_{ip}"
            
            current = cache.get(key) or 0
            if current >= limit:
                return jsonify({
                    "message": "Rate limit exceeded",
                    "error": "too_many_requests"
                }), 429
            
            cache.set(key, current + 1, timeout=per)
            return f(*args, **kwargs)
        return wrapper
    return decorator
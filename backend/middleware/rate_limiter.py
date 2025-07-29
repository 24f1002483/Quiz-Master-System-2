from flask import request, jsonify
from functools import wraps
from flask import current_app
from cache import cache
import time

class RateLimiter:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.check_rate_limit)
    
    @staticmethod
    def get_identifier():
        """Get client identifier for rate limiting"""
        # Use JWT identity if authenticated, otherwise IP address
        from flask_jwt_extended import get_jwt_identity
        identity = get_jwt_identity()
        return identity or request.remote_addr or '127.0.0.1'
    
    @staticmethod
    def check_rate_limit():
        """Global rate limiting middleware"""
        if request.endpoint in current_app.view_functions:
            view_func = current_app.view_functions[request.endpoint]
            if hasattr(view_func, '_rate_limit'):
                limit, window = view_func._rate_limit
                key = f"rate_limit:{request.endpoint}:{RateLimiter.get_identifier()}"
                
                current = cache.get(key) or 0
                if current >= limit:
                    return jsonify({
                        "message": "Rate limit exceeded",
                        "error": "too_many_requests",
                        "limits": {
                            "limit": limit,
                            "window": window,
                            "remaining": 0
                        }
                    }), 429
                
                if current == 0:
                    cache.set(key, 1, timeout=window)
                else:
                    cache.incr(key)
    
    @staticmethod
    def limit(requests=100, window=60):
        """Decorator for endpoint-specific rate limiting"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                f._rate_limit = (requests, window)
                return f(*args, **kwargs)
            return wrapper
        return decorator
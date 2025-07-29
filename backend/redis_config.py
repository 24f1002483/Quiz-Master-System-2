import redis
from flask import current_app
from config import Config

class RedisManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_redis()
        return cls._instance
    
    def init_redis(self):
        self.connection_pool = redis.ConnectionPool.from_url(
            Config.REDIS_URL,
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=10,
            retry_on_timeout=True
        )
        
        # Performance tuning
        self.redis = redis.Redis(connection_pool=self.connection_pool)
        self.redis.config_set('maxmemory-policy', 'allkeys-lru')
        self.redis.config_set('maxmemory', '256mb')
        self.redis.config_set('timeout', 300)
        self.redis.config_set('tcp-keepalive', 60)
    
    def get_redis(self):
        return self.redis
    
    def clear_cache(self):
        """Clear all cache keys"""
        self.redis.flushdb()
    
    def optimize_for_caching(self):
        """Optimize Redis for caching scenarios"""
        self.redis.config_set('activerehashing', 'yes')
        self.redis.config_set('hz', 10)  # Lower CPU usage
        self.redis.config_set('save', '')  # Disable persistence for cache
        return "Redis optimized for caching"

# Singleton instance
redis_manager = RedisManager()
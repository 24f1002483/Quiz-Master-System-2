import redis
from redis.exceptions import ConnectionError
from config import Config
import time
def get_redis_connection():
    """Get optimized Redis connection with connection pooling"""
    return redis.Redis.from_url(
        Config.CELERY_BROKER_URL,
        max_connections=Config.CELERY_REDIS_MAX_CONNECTIONS,
        socket_timeout=10,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )

def test_redis_connection():
    """Test Redis connection with retry logic"""
    max_retries = 3
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            conn = get_redis_connection()
            conn.ping()
            return True
        except ConnectionError as e:
            if i == max_retries - 1:
                raise
            time.sleep(retry_delay)
    
    return False

def optimize_redis_for_celery():
    """Configure Redis for optimal Celery performance"""
    conn = get_redis_connection()
    
    # Configure Redis settings
    conn.config_set('maxmemory-policy', 'allkeys-lru')
    conn.config_set('maxmemory', '256mb')
    conn.config_set('timeout', 300)
    
    # Enable Redis persistence
    conn.config_set('save', '900 1 300 10 60 10000')
    conn.config_set('appendonly', 'yes')
    
    return "Redis optimized for Celery"
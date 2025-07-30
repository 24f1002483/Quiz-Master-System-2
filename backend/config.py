import os
from datetime import timedelta

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///quiz.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
    
    # JWT Configuration
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = False  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 30))
    JWT_ACCESS_TOKEN_EXPIRES = SESSION_TIMEOUT_MINUTES * 60  # Convert to seconds
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 24 hours in seconds
    
    # Activity tracking
    ACTIVITY_CHECK_INTERVAL = 60  # Check activity every 60 seconds
    SESSION_WARNING_THRESHOLD = 5  # Show warning 5 minutes before expiry
    
    # Celery configuration
    broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Enhanced Celery settings
    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    timezone = 'UTC'
    enable_utc = True
    task_track_started = True
    task_time_limit = 30 * 60  # 30 minutes
    task_soft_time_limit = 25 * 60  # 25 minutes
    worker_prefetch_multiplier = 4
    worker_max_tasks_per_child = 1000
    worker_disable_rate_limits = False
    task_acks_late = True
    worker_lost_wait = 30
    result_expires = 3600  # 1 hour
    result_persistent = True
    task_ignore_result = False
    task_store_errors_even_if_ignored = True
    task_always_eager = False
    task_eager_propagates = True
    task_compression = 'gzip'
    
    # Task routing for better queue management
    task_routes = {
        'celery_app.send_daily_reminders': {'queue': 'reminders'},
        'celery_app.generate_monthly_reports': {'queue': 'reports'},
        'celery_app.cleanup_old_data': {'queue': 'maintenance'},
        'notification_services.send_email': {'queue': 'notifications'},
    }
    
    # Queue configuration
    task_default_queue = 'default'
    task_default_exchange = 'default'
    task_default_routing_key = 'default'
    
    # Scheduled tasks with improved timing
    beat_schedule = {
        'send-daily-reminders': {
            'task': 'celery_app.send_daily_reminders',
            'schedule': timedelta(hours=24),  # Run daily at midnight UTC
            'options': {
                'time_limit': 300,  # 5 minutes timeout
                'soft_time_limit': 270,  # 4.5 minutes soft timeout
                'queue': 'reminders'
            }
        },
        'generate-monthly-reports': {
            'task': 'celery_app.generate_monthly_reports',
            'schedule': timedelta(days=30),  # Run on the 1st of each month
            'options': {
                'time_limit': 1800,  # 30 minutes timeout
                'soft_time_limit': 1500,  # 25 minutes soft timeout
                'queue': 'reports'
            }
        },
        'cleanup-old-data': {
            'task': 'celery_app.cleanup_old_data',
            'schedule': timedelta(hours=12),  # Run twice daily
            'options': {
                'time_limit': 300,  # 5 minutes timeout
                'soft_time_limit': 270,  # 4.5 minutes soft timeout
                'queue': 'maintenance'
            }
        }
    }
    
    # Redis optimization settings
    redis_max_connections = 20
    redis_socket_connect_timeout = 5
    redis_socket_timeout = 5
    redis_retry_on_timeout = True
    redis_socket_keepalive = True
    redis_socket_keepalive_options = {
        'TCP_KEEPIDLE': 1,
        'TCP_KEEPINTVL': 3,
        'TCP_KEEPCNT': 5,
    }
    
    # Worker optimization
    worker_concurrency = 4  # Number of worker processes
    worker_prefetch_multiplier = 4  # Prefetch 4 tasks per worker
    worker_max_tasks_per_child = 1000  # Restart worker after 1000 tasks
    task_time_limit = 1800  # 30 minutes
    task_soft_time_limit = 1500  # 25 minutes
    
    # Email service rate limiting
    EMAIL_RATE_LIMIT = '100/m'  # 100 emails per minute
    
    # Notification settings
    NOTIFICATION_BATCH_SIZE = 50  # Process notifications in batches
    NOTIFICATION_RETRY_DELAY = 300  # 5 minutes between retries
    NOTIFICATION_MAX_RETRIES = 3

class DevelopmentConfig(Config):
    DEBUG = True
    task_always_eager = False  # Keep async for testing
    worker_concurrency = 2  # Fewer workers for development

class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    worker_concurrency = 8  # More workers for production
    redis_max_connections = 50
    worker_prefetch_multiplier = 8

class TestingConfig(Config):
    TESTING = True
    SESSION_TIMEOUT_MINUTES = 5  # Shorter timeout for testing
    task_always_eager = True  # Synchronous execution for tests
    worker_concurrency = 1

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
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
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Scheduled tasks
    CELERYBEAT_SCHEDULE = {
        'send-daily-reminders': {
            'task': 'celery_app.send_daily_reminders',
            'schedule': timedelta(hours=24),  # Run daily at midnight UTC
            'options': {
                'time_limit': 300,  # 5 minutes timeout
                'soft_time_limit': 270  # 4.5 minutes soft timeout
            }
        },
        'generate-monthly-reports': {
            'task': 'celery_app.generate_monthly_reports',
            'schedule': timedelta(days=30),  # Run on the 1st of each month
            'options': {
                'time_limit': 1800,  # 30 minutes timeout
                'soft_time_limit': 1500  # 25 minutes soft timeout
            }
        }
    }
    
    # Redis optimization
    CELERY_REDIS_MAX_CONNECTIONS = 20
    CELERYD_PREFETCH_MULTIPLIER = 4  # Prefetch 4 tasks per worker
    CELERYD_CONCURRENCY = 4  # Number of worker processes
    
    # Email service rate limiting
    EMAIL_RATE_LIMIT = '100/m'  # 100 emails per minute
    
    # SMS service rate limiting
    SMS_RATE_LIMIT = '30/m'  # 30 SMS per minute

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    SESSION_TIMEOUT_MINUTES = 5  # Shorter timeout for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models.model import db
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.quiz_routes import quiz_bp
from routes.user_quiz import user_quiz_bp  
from routes.user_routes import user_bp
from routes.score_routes import score_bp  
from routes.search import search_bp
from routes.optimized import api_bp
from routes.export_routes import export_bp
from routes.api_routes import api_routes_bp
from routes.analytics_routes import analytics_bp
from middleware.session_middleware import session_middleware
from config import config
import os
from flask_migrate import Migrate
from flask import send_from_directory

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configure CORS with specific settings
    CORS(app, 
         supports_credentials=True,
         origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         expose_headers=["Content-Type", "Authorization"])
    
    # Load configuration
    app.config.from_object(config[config_name]) 
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    
    # Initialize cache
    cache_initialized = False
    try:
        from cache import get_cache
        cache = get_cache()
        cache.init_app(app)
        cache_initialized = True
        print("✅ Cache initialized successfully")
    except Exception as e:
        print(f"⚠️  Cache initialization failed: {e}")
        # Continue without cache if Redis is not available
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)  # No prefix - routes will be /login, /register, etc.
    app.register_blueprint(quiz_bp)
    app.register_blueprint(user_quiz_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(score_bp)
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(api_bp)  # Optimized API v2 routes
    app.register_blueprint(export_bp, url_prefix='/api')  # Export routes
    app.register_blueprint(api_routes_bp, url_prefix='/api')  # Direct API routes
    app.register_blueprint(analytics_bp)  # Analytics routes
    
    # Register session middleware
    @app.before_request
    def before_request():
        response = session_middleware()
        if response:
            return response

    @app.route('/')
    def index():
        return send_from_directory('../frontend/dist', 'index.html')

    @app.route('/<path:path>')
    def static_proxy(path):
        return send_from_directory('../frontend/dist', path)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        # Create default admin if not present
        from models.model import User, Role
        admin_username = 'admin@quizmaster.com'
        admin_password = 'admin123'
        admin = User.query.filter_by(role=Role.ADMIN).first()
        if not admin:
            admin = User(username=admin_username, full_name='Admin', qualification='Admin', dob=None, role=Role.ADMIN)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
    
    # Check Redis status
    redis_status = "✅ Running"
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except Exception as e:
        redis_status = "❌ Not running"
    
    print("🚀 Starting Quiz Master Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("👤 Default admin credentials:")
    print("   Username: admin@quizmaster.com")
    print("   Password: admin123")
    print(f"🔴 Redis Status: {redis_status}")
    
    if "✅" in redis_status:
        print("🎉 Full functionality available (caching + background tasks)")
    else:
        print("⚠️  Limited functionality (no caching or background tasks)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
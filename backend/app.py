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
    try:
        from cache import get_cache
        cache = get_cache()
        cache.init_app(app)
    except Exception as e:
        print(f"Warning: Cache initialization failed: {e}")
        # Continue without cache if Redis is not available
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(user_quiz_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(score_bp)
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(api_bp)  # Optimized API v2 routes
    
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
    

    
    app.run(debug=True)
from flask import request, jsonify, g, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta
import time

# Store user activity timestamps (in production, use Redis or database)
user_activity = {}

def update_user_activity(user_id):
    """Update user's last activity timestamp"""
    user_activity[user_id] = time.time()

def get_user_activity(user_id):
    """Get user's last activity timestamp"""
    return user_activity.get(user_id, 0)

def is_session_expired(user_id, timeout_minutes=None):
    """Check if user's session has expired due to inactivity"""
    if timeout_minutes is None:
        # Get timeout from config
        timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
    
    last_activity = get_user_activity(user_id)
    if last_activity == 0:
        return True
    
    timeout_seconds = timeout_minutes * 60
    return (time.time() - last_activity) > timeout_seconds

def session_middleware():
    """Middleware to check session timeout on protected routes"""
    # Skip session check for OPTIONS requests (CORS preflight)
    if request.method == 'OPTIONS':
        return None
    
    # Skip session check for login and public routes
    public_routes = ['/login', '/register', '/refresh', '/session/status']
    
    if request.path in public_routes:
        return None
    
    try:
        # Verify JWT token
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        if user_id:
            # Always update user activity first to prevent race conditions
            update_user_activity(user_id)
            
            # Check if session has expired due to inactivity
            if is_session_expired(user_id):
                # Clear user activity
                user_activity.pop(user_id, None)
                print(f"Session expired for user {user_id} on route {request.path}")
                return jsonify({
                    'message': 'Session expired due to inactivity. Please login again.',
                    'code': 'SESSION_EXPIRED'
                }), 401
            
    except Exception as e:
        # JWT verification failed
        print(f"JWT verification failed: {e}")
        return jsonify({
            'message': 'Invalid or expired token. Please login again.',
            'code': 'TOKEN_INVALID'
        }), 401
    
    return None

def clear_user_session(user_id):
    """Clear user's session data"""
    user_activity.pop(user_id, None) 
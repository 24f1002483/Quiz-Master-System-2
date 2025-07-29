from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, unset_jwt_cookies, set_access_cookies, set_refresh_cookies
from models.model import db, User
from middleware.session_middleware import update_user_activity, clear_user_session
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/refresh', methods=['POST', 'OPTIONS'])
def refresh():
    """Refresh access token using refresh token"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'}), 200
    
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt
        verify_jwt_in_request(refresh=True)
        user_id = get_jwt_identity()
        
        if user_id:
            # Create new access token
            new_access_token = create_access_token(identity=user_id, expires_delta=timedelta(minutes=30))
            
            # Update user activity
            update_user_activity(user_id)
            
            # Get session timeout from config
            session_timeout = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
            
            resp = jsonify({
                'message': 'Token refreshed successfully',
                'access_token': new_access_token,
                'session_timeout': session_timeout
            })
            
            # Set new access token in cookies
            set_access_cookies(resp, new_access_token)
            
            return resp, 200
        else:
            return jsonify({'message': 'Invalid refresh token'}), 401
            
    except Exception as e:
        return jsonify({'message': 'Invalid or expired refresh token'}), 401

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'}), 200
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    qualification = data.get('qualification')
    dob = data.get('dob')
    if not username or not password:
        return jsonify({'message': 'Missing required fields'}), 400
    if User.query.filter(User.username == username).first():
        return jsonify({'message': 'Username already exists'}), 409
    dob_date = datetime.strptime(dob, '%Y-%m-%d').date() if dob else None
    if dob_date:
        today = datetime.utcnow().date()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        if age < 5:
            return jsonify({'message': 'User must be at least 5 years old to register.'}), 400
    # Set both username and email to the username value
    user = User(
        username=username,
        full_name=full_name,
        qualification=qualification,
        dob=dob_date
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'}), 200
    
    try:
        data = request.get_json(silent=True)
        print("JSON payload:", data)

        if not data:
            return jsonify({'message': 'Invalid or missing JSON'}), 400

        username = data.get('username')
        password = data.get('password')

        print("Username:", username, "Password:", password)

        if not username or not password:
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=30))
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=timedelta(hours=24))
        
        # Update user activity on login
        update_user_activity(str(user.id))
        
        # Get session timeout from config
        session_timeout = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
        
        # Return token in response body for frontend localStorage
        resp = jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.serialize(),
            'session_timeout': session_timeout  # minutes
        })
        
        # Also set cookies for backend compatibility
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        return resp, 200

    except Exception as e:
        import traceback
        print("Exception occurred:", e)
        traceback.print_exc()
        return jsonify({'message': 'Internal error', 'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    # Clear user session data
    clear_user_session(user_id)
    
    resp = jsonify({'message': 'Logout successful'})
    unset_jwt_cookies(resp)
    return resp, 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Update user activity
    update_user_activity(user_id)
    
    return jsonify(user.serialize()), 200

@auth_bp.route('/session/status', methods=['GET', 'OPTIONS'])
def session_status():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'}), 200
    
    # For GET requests, try to get user info but don't require it
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        if user_id:
            from middleware.session_middleware import get_user_activity, is_session_expired, update_user_activity
            
            # Update user activity when checking status
            update_user_activity(user_id)
            
            last_activity = get_user_activity(user_id)
            is_expired = is_session_expired(user_id)
            
            # Get session timeout from config
            session_timeout = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
            
            print(f"Session status check for user {user_id}: last_activity={last_activity}, is_expired={is_expired}, timeout={session_timeout}")
            
            return jsonify({
                'user_id': user_id,
                'last_activity': last_activity,
                'is_expired': is_expired,
                'session_timeout': session_timeout  # minutes
            }), 200
        else:
            # Get session timeout from config
            session_timeout = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
            
            return jsonify({
                'user_id': None,
                'last_activity': 0,
                'is_expired': True,
                'session_timeout': session_timeout
            }), 200
    except Exception as e:
        # Get session timeout from config
        session_timeout = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
        
        return jsonify({
            'user_id': None,
            'last_activity': 0,
            'is_expired': True,
            'session_timeout': session_timeout
        }), 200 
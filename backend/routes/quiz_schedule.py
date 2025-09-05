from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
from models.model import db, Quiz, User
from functools import wraps

schedule_bp = Blueprint('schedule', __name__, url_prefix='/api/schedule')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != 'admin':
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@schedule_bp.route('/quiz', methods=['POST'])
@jwt_required()
@admin_required
def create_scheduled_quiz():
    data = request.get_json()
    
    try:
        # Parse dates and duration
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        duration = int(data['duration'])  # in minutes
        
        if start_date >= end_date:
            return jsonify({"message": "End date must be after start date"}), 400
        
        new_quiz = Quiz(
            title=data['title'],
            description=data.get('description', ''),
            chapter_id=data['chapter_id'],
            start_date=start_date,
            end_date=end_date,
            time_duration=duration,
            is_active=True
        )
        
        db.session.add(new_quiz)
        db.session.commit()
        
        return jsonify(new_quiz.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@schedule_bp.route('/quiz/<int:quiz_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_quiz_schedule(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    try:
        if 'start_date' in data:
            quiz.start_date = datetime.fromisoformat(data['start_date'])
        if 'end_date' in data:
            quiz.end_date = datetime.fromisoformat(data['end_date'])
        if 'duration' in data:
            quiz.time_duration = int(data['duration'])
        
        if quiz.start_date >= quiz.end_date:
            return jsonify({"message": "End date must be after start date"}), 400
        
        db.session.commit()
        return jsonify(quiz.serialize()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@schedule_bp.route('/quiz/status', methods=['GET'])
def check_quiz_statuses():
    # This could be run periodically to deactivate expired quizzes
    now = datetime.now(timezone.utc)
    expired_quizzes = Quiz.query.filter(
        Quiz.end_date < now,
        Quiz.is_active == True
    ).all()
    
    for quiz in expired_quizzes:
        quiz.is_active = False
    
    db.session.commit()
    return jsonify({"message": f"Updated {len(expired_quizzes)} quizzes"}), 200
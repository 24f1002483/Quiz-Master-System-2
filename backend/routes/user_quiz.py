from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from models.model import db, Quiz, UserQuizAttempt
from functools import wraps

user_quiz_bp = Blueprint('user_quiz', __name__, url_prefix='/api/user/quiz')


@user_quiz_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_quizzes():
    user_id = get_jwt_identity()
    now = datetime.now(timezone.utc)
    
    # Get quizzes that are active and within their scheduled time
    quizzes = Quiz.query.filter(
        Quiz.is_active == True,
        Quiz.start_date <= now,
        Quiz.end_date >= now
    ).all()
    
    # Allow multiple attempts - don't filter out completed quizzes
    # Users can retake quizzes as many times as they want
    available_quizzes = quizzes
    
    return jsonify([q.serialize() for q in available_quizzes])

@user_quiz_bp.route('/start/<int:quiz_id>', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    user_id = get_jwt_identity()
    quiz = Quiz.query.get_or_404(quiz_id)
    now = datetime.now(timezone.utc)
    
    # Check if quiz is available
    if not quiz.is_available():
        return jsonify({"message": "Quiz is not currently available"}), 400
    
    # Check if user already has an in-progress attempt
    existing_attempt = UserQuizAttempt.query.filter_by(
        user_id=user_id,
        quiz_id=quiz_id,
        status='in_progress'
    ).first()
    
    if existing_attempt:
        return jsonify({
            'attempt_id': existing_attempt.id,
            'quiz_id': quiz_id,
            'time_remaining': quiz.time_remaining(),
            'start_time': existing_attempt.start_time.isoformat() if existing_attempt.start_time else now.isoformat()
        }), 200
    
    # Create new attempt
    new_attempt = UserQuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        start_time=now,
        status='in_progress',
        total_questions=len(quiz.questions)  # Set total questions from quiz
    )
    
    db.session.add(new_attempt)
    db.session.commit()
    
    return jsonify({
        'attempt_id': new_attempt.id,
        'quiz_id': quiz_id,
        'time_remaining': quiz.time_remaining(),
        'start_time': now.isoformat()
    }), 201

@user_quiz_bp.route('/check-time/<int:attempt_id>', methods=['GET'])
@jwt_required()
def check_quiz_time(attempt_id):
    attempt = UserQuizAttempt.query.get_or_404(attempt_id)
    if str(attempt.user_id) != get_jwt_identity():
        return jsonify({"message": "Unauthorized"}), 403
    
    quiz = attempt.quiz
    time_remaining = quiz.time_remaining()
    
    if time_remaining <= 0:
        attempt.status = 'expired'
        db.session.commit()
        return jsonify({
            'time_remaining': 0,
            'status': 'expired',
            'message': 'Quiz time has expired'
        }), 200
    
    return jsonify({
        'time_remaining': time_remaining,
        'status': 'in_progress'
    }), 200
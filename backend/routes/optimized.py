from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.model import User, Quiz, Subject
# from cache import cache_decorator, rate_limit_decorator  # Temporarily disabled
import time
from datetime import datetime
api_bp = Blueprint('api', __name__, url_prefix='/api/v2')

@api_bp.route('/subjects', methods=['GET'])
@jwt_required()
# @cache_decorator(timeout=60)  # Temporarily disabled
# @rate_limit_decorator(limit=100, per=60)  # Temporarily disabled
def get_subjects():
    """Get all subjects with caching and rate limiting"""
    time.sleep(0.5)  # Simulate DB query
    subjects = Subject.query.filter_by(is_active=True).all()
    return jsonify([s.serialize() for s in subjects])

@api_bp.route('/quizzes', methods=['GET'])
@jwt_required()
# @cache_decorator(timeout=30)  # Temporarily disabled
# @rate_limit_decorator(limit=150, per=60)  # Temporarily disabled
def get_quizzes():
    """Get available quizzes with caching and rate limiting"""
    time.sleep(0.7)  # Simulate DB query
    quizzes = Quiz.query.filter(
        Quiz.is_active == True,
        Quiz.start_date <= datetime.utcnow(),
        Quiz.end_date >= datetime.utcnow()
    ).all()
    return jsonify([q.serialize() for q in quizzes])

@api_bp.route('/users', methods=['GET'])
@jwt_required()
# @cache_decorator(timeout=120)  # Temporarily disabled
# @rate_limit_decorator(limit=50, per=60)  # Temporarily disabled
def get_users():
    """Get all users (admin only) with caching and rate limiting"""
    time.sleep(1.0)  # Simulate DB query
    users = User.query.all()
    return jsonify([u.serialize() for u in users])

@api_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
# @cache_decorator(timeout=30)  # Temporarily disabled
# @rate_limit_decorator(limit=100, per=60)  # Temporarily disabled
def get_quiz_by_id(quiz_id):
    """Get a specific quiz by ID with caching and rate limiting"""
    time.sleep(0.3)  # Simulate DB query
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify(quiz.serialize())